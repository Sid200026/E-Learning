from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.author.username} {self.title}"


class Reply(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name="replies", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    comment = models.ForeignKey(
        Comment, related_name="replies", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Reply {self.author.username} {self.title}"


class Course(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return f"${self.name}"
