from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Course(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    currency = models.CharField(max_length=3, default="INR")

    def __str__(self):
        return f"{self.name}"


class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    course = models.ForeignKey(
        Course, related_name="comments", on_delete=models.CASCADE
    )

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

    class Meta:
        verbose_name_plural = "Replies"

    def __str__(self):
        return f"Reply {self.author.username} {self.title}"
