from django import forms
from common.models import CmnLookupTypes, CmnLookupCodes
from django.conf import settings


class LookupForm(forms.ModelForm):

    class Meta:
        model = CmnLookupTypes
        fields = ('lookup_type','lookup_module','security_level','lookup_desc')


class LookupCodeForm(forms.ModelForm):
    start_date = forms.DateField(
                widget=forms.SelectDateWidget(),input_formats=settings.DATE_INPUT_FORMATS)
    end_date = forms.DateField(
                widget=forms.SelectDateWidget(),input_formats=settings.DATE_INPUT_FORMATS)
    lookup_code = forms.CharField(label='Lookup Type',
                                  widget=forms.TextInput(attrs={'onchange':'syncFunction()'})
                                  )

    def __init__(self, *args, **kwargs):
        super(LookupCodeForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.clt_lookup_type:
            self.fields['clt_lookup_type'].widget.attrs['readonly'] = 'readonly'
            self.fields['lookup_code'].widget.attrs['readonly'] = 'readonly'

    class Meta:
        model = CmnLookupCodes
        fields = model.fieldlist()