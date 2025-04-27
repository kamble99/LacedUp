from django.contrib import admin
from .models import Account
from django.contrib.auth.admin import UserAdmin


class AccountAdmin(admin.ModelAdmin):
    list_display=('email','first_name','last_name','username','date_joined','last_login','is_active')
admin.site.register(Account,AccountAdmin)
