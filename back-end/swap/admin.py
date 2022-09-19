from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import User, Wallet 


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display =  ['username','email','password']
    list_editable = ['email']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_staff or not request.user.is_superuser:
            form.base_fields.get('groups').disabled = True
            form.base_fields.get('user_permissions').disabled = True
            form.base_fields.get('email_address').disabled = True
            form.base_fields.get('is_superuser').disabled = True
        else:
            return form

# The admin userPermission will define 
class UserPermissionMixin:
    def has_view_permission(self, request, obj=None):
        # return False if request.user.is_anonymous else True
        return True

    def has_add_permission(self, request, obj=None):
        # if not request.user.is_superuser or not request.user.is_staff:
        #     return False
        # else: return True
        return True

    def has_change_permission(self, request, obj=None):
        # if not request.user.is_superuser:
        #     return False
        # else: return True        
        True

    def has_delete_permission(self, request, obj=None):
        # if not request.user.is_superuser:
        #     return False
        # else: return True        
        return True


@admin.register(Wallet)
class WalletAdmin(UserPermissionMixin ,admin.ModelAdmin):
    list_display = ['address', 'balance']