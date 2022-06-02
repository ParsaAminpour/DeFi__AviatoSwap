from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display =  ['username','email','password']
    list_editable = ['email']


