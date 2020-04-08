from django.contrib import admin
from .models import CoursePurchased, Receipt

# Register your models here.
admin.site.register(CoursePurchased)
admin.site.register(Receipt)
