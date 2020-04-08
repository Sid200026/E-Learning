from rest_framework import serializers
from django.contrib.auth import get_user_model
from comments.models import Course
from comments.serializers import CourseNameSerializer
from .models import Receipt, CoursePurchased

User = get_user_model()


class IDSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class StringIDSerializer(serializers.Serializer):
    id = serializers.CharField()


class PaymentSerializer(serializers.Serializer):
    razorpay_payment_id = serializers.CharField()
    razorpay_order_id = serializers.CharField()
    razorpay_signature = serializers.CharField()


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = "__all__"

class CoursePurchasedSerializer(serializers.ModelSerializer):
    course = CourseNameSerializer()
    class Meta:
        model = CoursePurchased
        fields = "__all__"