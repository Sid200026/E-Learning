from django.contrib import admin
from .models import ResetPasswordLink, EmailTemplate, SocialAccount

admin.site.register(ResetPasswordLink)
admin.site.register(EmailTemplate)
admin.site.register(SocialAccount)
