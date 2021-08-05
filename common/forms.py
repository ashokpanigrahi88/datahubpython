from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from common.models import *
from django.db import connection


def get_sequenceval(p_sequence):
    with connection.cursor() as cursor:
        cursor.execute("SELECT " + p_sequence + "  From Dual")
        row = cursor.fetchone()
        print(row)
        print(p_sequence+' '+str(row[0]))
        return row[0]

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CmnUsers
        fields = CmnUsers.fieldlist()

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
        user.update_source = 'RESETPASSWORD'
        user.user_password = self.cleaned_data["password1"]
        user.is_staff = True
        user.active = 'Y'
        user.bu_id = 1
        user.set_password(self.cleaned_data["password1"])
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

