from django import forms
from django.conf import settings
from common.sysutil import CHOICES


class pricecheckform(forms.Form):
    item_number = forms.CharField(max_length=30,label='Item Number / Barcode');
    fuzzy_search = forms.CharField(max_length=3, label='Fuzzy Search',
                                   choices=CHOICES['YES_NO']
                )


class LookupCodeForm(forms.ModelForm):
    class Meta:
        model = CmnLookupCodes
        fields = '__all__'