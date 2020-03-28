from django.contrib.auth import get_user_model
from django.http import Http404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import EmailMessage
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import resetPasswordSerializer
from .models import ResetPasswordLink, EmailTemplate, SocialAccount
from .constants import ErrorMessages
import requests
import json
import string
import random

User = get_user_model()


def passwordGenerator():
    chars = string.ascii_letters + string.digits
    password = ""
    for i in range(8):  # Length of generated password is 8
        password += random.choice(chars)
    while validate_password(password) is not None:
        password = passwordGenerator()
    return password


def send_email(subject, body, to):
    email = EmailMessage(subject=subject, body=body, to=[to,])
    email.send(fail_silently=False)


class ResetPassword(APIView):
    def get_user(self, pk):
        try:
            return User.objects.get(email=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, username, format=None):
        user = self.get_user(username)
        # TODO : Add an url link
        randomURL = ResetPasswordLink.getTokenForEmail(user)
        send_email(
            "Reset Password Request",
            EmailTemplate.objects.filter(shortTitle__icontains="reset")[
                0
            ].template.format(user.username, randomURL),
            user.email,
        )
        data = {
            "result": True,
            "message": "Email has been sent with the reset link",
            "error": "",
        }
        return Response(data=data, status=status.HTTP_200_OK)

    def post(self, request, username, format=None):
        serializer = resetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            data = {"result": False, "error": ErrorMessages.notValid.value}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        password = serializer.validated_data.get("password")
        resetKey = serializer.validated_data.get("resetKey")
        user = self.get_user(username)
        try:
            validate_password(password)
        except Exception as error:
            data = {"result": False, "error": str(error)}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        if check_password(password, user.password):
            data = {"result": False, "error": ErrorMessages.samePassword.value}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        if not resetKey == ResetPasswordLink.objects.get(user=user).passwordResetParam:
            data = {"result": False, "error": ErrorMessages.invalidCode.value}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        if not ResetPasswordLink.objects.get(user=user).checkIfValid():
            data = {"result": False, "error": ErrorMessages.expired.value}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.set_password(password)
            user.save()
            data = {
                "result": True,
                "message": ErrorMessages.passwordChange.value,
                "error": "",
            }
            send_email(
                "Password Updated Successfullyƒ",
                EmailTemplate.objects.filter(shortTitle__icontains="update")[
                    0
                ].template.format(user.first_name),
                user.email,
            )
            return Response(data=data, status=status.HTTP_201_CREATED)


class SocialLogin(APIView):
    def get(self, request, provider, format=None):
        social_provider = SocialAccount.objects.filter(
            provider__iexact=provider
        ).first()
        return HttpResponseRedirect(
            f"{social_provider.authorization_code_url.format(social_provider.client_id, social_provider.redirect_url)}"
        )


class SocialSignUp(APIView):
    def get(self, request, provider, format=None):
        authorization_code = request.GET.get("code")
        error = request.GET.get("error")
        if authorization_code and error is None:
            social_provider = SocialAccount.objects.filter(
                provider__iexact=provider
            ).first()
            if social_provider.provider == "LinkedIn":
                response = requests.post(
                    f"{social_provider.access_code_url.format(authorization_code,social_provider.redirect_url,social_provider.client_id, social_provider.client_secret)}",
                    headers={"Content-Type": "x-www-form-urlencoded"},
                )
                if response.status_code == 200:
                    access_token = json.loads(response.content)["access_token"]
                    response = requests.get(
                        social_provider.profile_url,
                        headers={"Authorization": "Bearer " + access_token},
                    )
                    if response.status_code == 200:
                        pyobj = json.loads(response.content)
                        firstname = pyobj["localizedFirstName"]
                        lastname = pyobj["localizedLastName"]
                        username = pyobj["id"]
                        response = requests.get(
                            social_provider.email_url,
                            headers={"Authorization": "Bearer " + access_token},
                        )
                        if response.status_code == 200:
                            email = None
                            pyobj = json.loads(response.content)["elements"]
                            for access_point in pyobj:
                                if (
                                    access_point["type"] == "EMAIL"
                                    and access_point["primary"] == True
                                ):
                                    email = access_point["handle~"]["emailAddress"]
                                    break
                            userInstance = User.objects.filter(email=email).first()
                            if userInstance is not None:
                                login(request, userInstance)
                                data = {"success": True, "errors": None}
                                return Response(
                                    data=data, status=status.HTTP_201_CREATED
                                )
                            new_password = passwordGenerator()
                            try:
                                userInstance = User.objects.create_user(
                                    username=username,
                                    first_name=firstname,
                                    last_name=lastname,
                                    email=email,
                                    password=new_password,
                                )
                            except:
                                data = {
                                    "success": False,
                                    "errors": "Could not create a new user",
                                }
                                return Response(
                                    data=data, status=status.HTTP_400_BAD_REQUEST
                                )
                            login(request, userInstance)
                            send_email(
                                "Welcome to Be of Use",
                                EmailTemplate.objects.filter(
                                    shortTitle__icontains="created"
                                )[0].template.format(firstname, email, new_password),
                                email,
                            )
                            data = {"success": True, "errors": None}
                            return Response(data=data, status=status.HTTP_201_CREATED)
                        else:
                            data = {
                                "success": False,
                                "errors": "Could not connect to LinkedIn",
                            }
                            return Response(
                                data=data, status=status.HTTP_400_BAD_REQUEST
                            )
                    else:
                        data = {
                            "success": False,
                            "errors": "Could not connect to LinkedIn",
                        }
                        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data = {"success": False, "errors": "Could not connect to LinkedIn"}
                    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            elif social_provider.provider == "Facebook":
                pass
        else:
            data = {"success": False, "errors": "Could not connect to social accounts"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)