from django.contrib.auth import get_user_model
from django.http import Http404
from django.core.mail import EmailMessage
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import resetPasswordSerializer
from .email_messages import EmailTemplates
from .models import ResetPasswordLink
from .constants import ErrorMessages

User = get_user_model()


def send_email(subject, body, to):
    email = EmailMessage(subject=subject, body=body, to=[to, ])
    email.send(fail_silently=False)


class ResetPassword(APIView):
    def get_user(self, pk):
        try:
            return User.objects.get(username=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, username, format=None):
        user = self.get_user(username)
        # TODO : Add an url link
        randomURL = ResetPasswordLink.getTokenForEmail(user)
        send_email("Reset Password Request", EmailTemplates.sendResetURL.value.format(
            user.username, randomURL), user.email)
        data = {'result': True, 'message': "Email has been sent with the reset link", 'error': ""}
        return Response(data=data, status=status.HTTP_200_OK)

    def post(self, request, username, format=None):
        serializer = resetPasswordSerializer(data = request.data)
        if not serializer.is_valid():
            data = {'result': False, 'error': ErrorMessages.notValid.value}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        password = serializer.validated_data.get('password')
        resetKey = serializer.validated_data.get('resetKey')
        user = self.get_user(username)
        try:
            validate_password(password)
        except Exception as error:
            data = {'result': False, 'error': str(error)}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        if check_password(password, user.password):
            data = {'result': False, 'error': ErrorMessages.samePassword.value}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        if not resetKey == ResetPasswordLink.objects.get(user=user).passwordResetParam:
            data = {'result': False, 'error': ErrorMessages.invalidCode.value}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        if not ResetPasswordLink.objects.get(user=user).checkIfValid():
            data = {'result': False, 'error': ErrorMessages.expired.value}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.set_password(password)
            user.save()
            data = {'result': True, 'message': ErrorMessages.passwordChange.value, 'error': ""}
            return Response(data=data, status=status.HTTP_201_CREATED)
