from django.db import models
from comments.models import Course
from django.contrib.auth import get_user_model

User = get_user_model()


class CoursePurchased(models.Model):
    user = models.ForeignKey(
        User, related_name="courses_purchased", on_delete=models.CASCADE
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="+")
    purchased_on = models.DateTimeField(editable=False, auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.course}"

    class Meta:
        verbose_name_plural = "Courses Purchased"
        verbose_name = "Course Purchased"
