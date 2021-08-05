from django import forms

from common.models import CmnBusinessUnits

bu_field_list = ('cc_comp_id',
                 'bu_name',
                 'bu_short_name',
                 'orig_system_ref_char',
                 'orig_system_ref_num',
                 'bu_address_line1',
                 'bu_city',
                 'bu_county',
                 'bu_post_code',
                 'cco_country_code',
                 'bu_phone',
                 'bu_fax',
                 'eori_number',
                 'email',
                 'url',
                 'gl_account_id',
                 'cc1_currency_code',
                 # 'cc1_cur_country',
                 )

class BusinessUnitsForm(forms.ModelForm):
    class Meta:
        model = CmnBusinessUnits
        fields = bu_field_list

    def __init__(self, *args, **kwargs):
        super(BusinessUnitsForm, self).__init__(*args, **kwargs)

        for field in CmnBusinessUnits._meta.fields:
            if field.name in bu_field_list and field.name not in ['email','url', 'cc1_currency_code','cc1_cur_country','cco_country_code']:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})
