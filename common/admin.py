from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from common.sysutil import *
from django.apps import apps

from common.models import CmnUsers, CmnModules, CmnFunctions

class OratechAdminSite(AdminSite):
    # Text to put at the end of each page's <title>.
    site_title = ugettext_lazy('Oratech Admin')

    # Text to put in each page's <h1> (and above login form).
    site_header = ugettext_lazy('Oratech Administration')
    site_url = "/"
    # Text to put at the top of the admin index page.
    index_title = ugettext_lazy('Oratech Administration')

admin_site = OratechAdminSite()
admin.site.site_header = 'Oratech Administration'
admin.site.site_title = ugettext_lazy('Oratech Admin')
admin.site.index_title = ugettext_lazy('Oratech')

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CmnUsers
        fields = ('user_name', 'user_full_name', 'email', 'password', 'is_active', 'is_admin')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        if not user.user_id:
           user.user_id = get_sequenceval('cmn_users_s.nextval')
        user.set_password(self.cleaned_data["password1"])
        user.user_password = self.cleaned_data["password1"]
        user.update_source = 'RESETPASSWORD'
        user.is_staff = True
        user.active = 'Y'
        user.bu_id = 1
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CmnUsers
        fields = ('user_name', 'user_full_name', 'email', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        print('updating password')
        if not user.user_id:
           user.user_id = get_sequenceval('cmn_users_s.nextval')
        user.set_password(self.cleaned_data["password1"])
        print('Current Password')
        user.user_password = self.cleaned_data["password1"]
        #user.update_source = 'RESETPASSWORD'
        if commit:
            user.save()
        return user

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('user_name','user_full_name','email', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('user_name','email', 'password')}),
        ('Personal info', {'fields': ('user_full_name',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_name','email', 'user_full_name', 'password1', 'password2'),
        }),
    )
    search_fields = ('user_name',)
    ordering = ('user_name',)
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(CmnUsers, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)

class CmnFunctionsInline(admin.TabularInline):
    model = CmnFunctions
    fk_name = "module_id"

class CmnModulesAdmin(admin.ModelAdmin):
    inlines = [
        CmnFunctions,
    ]

#get all modules but register only sys nodels
models = apps.get_models('common')

for model in models:
    try:
        if model._meta.model_name.startswith('sys') or \
                model._meta.model_name in ['cmnfunctions','cmnmenus','cmnresponsibilities','cmnmodules','cmnmailmergeheaders']:
            admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass