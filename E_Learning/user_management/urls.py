from django.urls import path, re_path
from .views import ResetPassword

app_name = 'user_management'

urlpatterns = [
    path("reset/<str:username>", ResetPassword.as_view(), name="reset_password"),
]