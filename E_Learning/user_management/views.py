from django.contrib.auth import get_user_model
from django.http import Http404
from django.core.mail import EmailMessage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import userSerializer
from .email_messages import EmailTemplates

User = get_user_model()


def send_email(subject, body, to):
    email = EmailMessage(subject = subject, body = body, to=[to,])
    email.send(fail_silently=False)


class ResetPassword(APIView):
    def get_user(self, pk):
        try:
            return User.objects.get(username=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, username, format=None):
        user = self.get_user(username)
        randomURL = "abcd.com"
        send_email("Reset Password Request", EmailTemplates.sendResetURL.value.format(
            user.username, randomURL), user.email)
        data = {'result': True, 'message': "Email has been sent with the reset link"}
        return Response(data=data, status=status.HTTP_200_OK)
