from django import forms
from django.forms import modelformset_factory, inlineformset_factory

from common.models import CmnLanguages
from django.forms import BaseModelFormSet

class BaseLanguageFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = CmnLanguages.objects.all()

LanguagesFormSet = modelformset_factory(CmnLanguages, fields ='__all__', extra=0,
                                        formset = BaseLanguageFormSet, can_delete=True)


class LanguageForm(forms.ModelForm):

    class Meta:
        model = CmnLanguages
        fields = ('language_code','language_name')