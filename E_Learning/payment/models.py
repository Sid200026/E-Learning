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


class Receipt(models.Model):
    STATUS_CHOICES = [
        ("Success", "Success"),
        ("Fail", "Fail"),
        ("In-Progress", "In-Progress"),
        ("Not Started", "Not Started"),
    ]
    user = models.ForeignKey(User, related_name="receipts", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="Not Started"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="+")
    order_id = models.CharField(max_length=30, null=True, blank=True)
    payment_id = models.CharField(max_length=30, null=True, blank=True)
    refund_id = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}"
