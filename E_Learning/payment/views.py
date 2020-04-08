from django.shortcuts import render, HttpResponse
from django.http import Http404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils.timezone import datetime
from django.conf import settings
from configparser import ConfigParser

import pytz
import razorpay
import pytz


from .serializers import IDSerializer, StringIDSerializer, PaymentSerializer
from .models import CoursePurchased, Receipt
from comments.models import Course
import logging

config = ConfigParser()
config.read("./secret.ini")
Razorpay_Key_ID = config.get("Razorpay", "key_id")
Razorpay_Secret = config.get("Razorpay", "key_secret")

client = razorpay.Client(auth=(Razorpay_Key_ID, Razorpay_Secret))


class Order(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = IDSerializer(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data["id"]
            courseInstance = Course.objects.filter(pk=id).first()
            if courseInstance is None:
                data = {
                    "error": "Course does not exist",
                    "message": "",
                    "result": False,
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            if CoursePurchased.objects.filter(
                course=courseInstance, user=request.user
            ).exists():
                data = {
                    "error": "Course already purchased",
                    "message": "",
                    "result": False,
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            receiptInstance, created = Receipt.objects.get_or_create(
                user=request.user, course=courseInstance, refund_id=None
            )
            DATA = {
                "amount": courseInstance.price * 100,
                "currency": courseInstance.currency,
                "payment_capture": "1",
                "receipt": f"{receiptInstance.pk}",
            }
            data = client.order.create(data=DATA)
            receiptInstance.order_id = data["id"]
            receiptInstance.save()
            return Response(data=data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FetchPayment(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = StringIDSerializer(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data["id"]
            receiptInstance = Receipt.objects.filter(
                user=request.user, order_id=id, refund_id__isnull=True
            ).first()
            if receiptInstance is None:
                data = {
                    "error": "No such receipt exists",
                    "message": "",
                    "result": False,
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            data = client.order.payments(receiptInstance.order_id)
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CapturePayment(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        payment_id = request.POST.get("razorpay_payment_id", "")
        order_id = request.POST.get("razorpay_order_id", "")
        try:
            client.utility.verify_payment_signature(request.POST)
        except Exception as error:
            data = {
                "error": str(error),
                "message": "",
                "result": False,
            }
            return HttpResponse("No signature match")
        receiptInstance = Receipt.objects.filter(
            order_id=order_id, refund_id__isnull=True
        ).first()
        if receiptInstance is None:
            return HttpResponse("No such receipt")
        data = None
        try:
            data = client.payment.fetch(payment_id)
        except Exception as error:
            return HttpResponse("No such payment can be done")
        # Payment is valid
        user = receiptInstance.user
        courseInstance = receiptInstance.course
        coursePurchasedInstance = CoursePurchased(user=user, course=courseInstance)
        coursePurchasedInstance.save()
        receiptInstance.status = "Success"
        receiptInstance.payment_id = payment_id
        receiptInstance.save()
        if not user.is_authenticated:
            login(request, user)
        return HttpResponse("Success")


class Refund(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = IDSerializer(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data["id"]
            coursePurchasedInstance = CoursePurchased.objects.filter(
                course__id=id, user=request.user
            ).first()
            if coursePurchasedInstance is None:
                data = {
                    "error": "No such course exists",
                    "message": "",
                    "result": False,
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            currentDate = datetime.now(pytz.timezone(settings.TIME_ZONE))
            # If more than 4 week refund shouldn't be allowed
            if (currentDate - coursePurchasedInstance.purchased_on).days // 7 > 4:
                data = {
                    "error": "Refund period has exceeded",
                    "message": "",
                    "result": False,
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            receiptInstance = Receipt.objects.filter(
                course=coursePurchasedInstance.course,
                user=request.user,
                payment_id__isnull=False,
            ).first()
            try:
                data = client.payment.refund(
                    receiptInstance.payment_id,
                    coursePurchasedInstance.course.price * 100,
                )
            except Exception as error:
                data = {
                    "error": str(error),
                    "message": "",
                    "result": False,
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            coursePurchasedInstance.delete()
            receiptInstance.order_id = None
            receiptInstance.payment_id = None
            receiptInstance.refund_id = data["id"]
            receiptInstance.save()
            data = {
                "entity": data["entity"],
                "amount": data["amount"],
                "status": data["status"],
            }
            return Response(data=data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FetchRefund(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = StringIDSerializer(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data["id"]
            receiptInstance = Receipt.objects.filter(
                user=request.user, refund_id=id
            ).first()
            if receiptInstance is None:
                data = {
                    "error": "No such receipt exists",
                    "message": "",
                    "result": False,
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            data = client.refund.fetch(receiptInstance.refund_id)
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
