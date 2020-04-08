from django.urls import path, re_path
from .views import (
    Order,
    FetchPayment,
    CapturePayment,
    Refund,
    FetchRefund,
    CoursesPurchased,
    Receipts,
)

app_name = "payment"

urlpatterns = [
    path("order/", Order.as_view(), name="order"),
    path("fetchPayment/", FetchPayment.as_view(), name="fetch_payment"),
    path("capturePayment/", CapturePayment.as_view(), name="capture_payment"),
    path("refund/", Refund.as_view(), name="refund"),
    path("fetchRefund/", FetchRefund.as_view(), name="fetch_refund"),
    path("receipts/", Receipts.as_view(), name="receipts"),
    path("coursesPurchased/", CoursesPurchased.as_view(), name="courses_purchased"),
]
