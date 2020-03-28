from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils.timezone import utc, datetime
from django.conf import settings
import pytz

User = get_user_model()


class ResetPasswordLink(models.Model):
    passwordResetParam = models.CharField(max_length=6)
    createdTime = models.DateTimeField(auto_now=False, auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} : {self.createdTime}"

    def checkIfValid(self):
        currentTime = datetime.now(pytz.timezone(settings.TIME_ZONE))
        difference = (currentTime - self.createdTime).total_seconds() / 60
        if difference > 15:
            # Time limit has been exceeded, issue new token
            return False
        else:
            return True

    @classmethod
    def getTokenForEmail(cls, user, **kwargs):
        instance, created = cls.objects.get_or_create(
            user=user, defaults={"passwordResetParam": cls.generateRandomKey}
        )
        if not created:
            # Check if it is still valid
            if instance.checkIfValid():
                return instance.passwordResetParam
            else:
                instance.delete()
                return cls.getTokenForEmail(cls, user)
        else:
            return instance.passwordResetParam

    @classmethod
    def generateRandomKey(cls):
        return get_random_string(length=6)


class EmailTemplate(models.Model):
    shortTitle = models.CharField(max_length=32)
    template = models.TextField()

    def __str__(self):
        return f"{self.shortTitle}"


class SocialAccount(models.Model):
    client_id = models.CharField(max_length=50, null=True, blank=True)
    client_secret = models.CharField(max_length=50, null=True, blank=True)
    redirect_url = models.URLField(max_length=200, null=True, blank=True)
    provider = models.CharField(max_length=32, null=True, blank=True)
    authorization_code_url = models.CharField(max_length=300, null=True, blank=True)
    access_code_url = models.CharField(max_length=300, null=True, blank=True)
    profile_url = models.URLField(max_length=300, null=True, blank=True)
    email_url = models.URLField(max_length=300, null=True, blank=True)

    def __str__(self):
        return f"{self.provider}"
