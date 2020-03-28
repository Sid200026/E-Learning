from django.urls import path, re_path
from .views import ResetPassword, SocialLogin, SocialSignUp

app_name = "user_management"

urlpatterns = [
    path("reset/<str:username>", ResetPassword.as_view(), name="reset_password"),
    path("social/initial/<str:provider>", SocialLogin.as_view(), name="social_login"),
    path("social/<str:provider>", SocialSignUp.as_view(), name="social_signup"),
]
