from django.urls import path, re_path
from .views import ResetPassword, SocialLogin, SocialSignUp, SendResetEmail

app_name = "user_management"

urlpatterns = [
    path("reset/request/", SendResetEmail.as_view(), name="reset_request"),
    path("reset/", ResetPassword.as_view(), name="reset_password"),
    path("social/initial/<str:provider>", SocialLogin.as_view(), name="social_login"),
    path("social/<str:provider>", SocialSignUp.as_view(), name="social_signup"),
]
