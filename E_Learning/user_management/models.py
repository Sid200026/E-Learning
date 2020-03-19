from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils.timezone import utc, datetime

User = get_user_model()

# Create your models here.


class ResetPasswordLink(models.Model):
    passwordResetParam = models.CharField(max_length=6)
    createdTime = models.DateTimeField(auto_now=False, auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} : {self.createdTime}"

    def checkIfValid(self):
        currentTime = datetime.utcnow().replace(tzinfo=utc)
        difference = (currentTime - self.createdTime).total_seconds()/60
        if(difference > 15):
            # Time limit has been exceeded, issue new token
            return False
        else:
            return True

    @classmethod
    def getTokenForEmail(cls, user):
        instance, created = cls.objects.get_or_create(
            user=user, defaults={'passwordResetParam': cls.generateRandomKey})
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
