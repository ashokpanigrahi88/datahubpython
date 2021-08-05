from django import forms
from django.conf import settings
from common.models import CmnCommodityCodes, CmnCommodityRates

### From XML
ccc_field_list = ('commodity_code',
                'name',
                'section',
                'chapter',
                'heading',
                'active',
                'legal_act',
                'exclusions',
                'conditions',
                'measure_type',
                'additional_codes',
                'attribute1',
                'attribute2',
                'attribute3',
                'attribute4',
                'attribute5',
                'attribute6',
                'start_date_active',
                'end_date_active',
                'footnote',
                'description')


class CommodityCodesForm(forms.ModelForm):
    start_date_active = forms.DateField(
        widget=forms.SelectDateWidget(), input_formats=settings.DATE_INPUT_FORMATS)
    end_date_active = forms.DateField(
        widget=forms.SelectDateWidget(), input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = CmnCommodityCodes
        fields = ccc_field_list

    def __init__(self, *args, **kwargs):
        super(CommodityCodesForm, self).__init__(*args, **kwargs)

        self.fields['active'].initial = 'Y'

        for field in CmnCommodityCodes._meta.fields:
            if field.name in ccc_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in CmnCommodityCodes._meta.fields:
            if field.name in ccc_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
                    # try:
                    #     self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
                    # except:
                    #     print('CommodityCodesForm: Couldnt save:', self.cleaned_data[field.name],'/nField:',field)
        return self.cleaned_data


ccr_field_list = ('ccc_id',
                  'country_code',
                  'duty_rate',
                  'start_date_active',
                  'end_date_active',
                  'description',
                  'attribute1',
                  'attribute2',
                  'attribute3',
                  'attribute4',
                  'attribute5',
                  'attribute6',)

class CommodityRatesForm(forms.ModelForm):

    start_date_active = forms.DateField(
        widget=forms.SelectDateWidget(), input_formats=settings.DATE_INPUT_FORMATS)
    end_date_active = forms.DateField(
        widget=forms.SelectDateWidget(), input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = CmnCommodityRates
        fields = ccr_field_list

    def __init__(self, *args, **kwargs):
        super(CommodityRatesForm, self).__init__(*args, **kwargs)

        for field in CmnCommodityRates._meta.fields:
            if field.name in ccr_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in CmnCommodityRates._meta.fields:
            if field.name in ccr_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
        return self.cleaned_data