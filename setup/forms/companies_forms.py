from django import forms

from common.models import CmnCompanies, CmnBusinessUnits

companies_field_list = ('comp_name',
                        'comp_trading_name',
                        'comp_slogan',
                        'comp_reg_no',
                        'comp_vat_reg_no',
                        'comp_address_line1',
                        'comp_city',
                        'comp_county',
                        'comp_post_code',
                        'comp_phone1',
                        'comp_phone2',
                        'comp_fax',
                        'comp_email',
                        'url',
                        'orig_system_ref_desc',
                        'orig_system_ref_code',
                        'gl_account_id',
                        'attribute1',
                        'attribute2',
                        'cc1_currency_code',
                        # 'cc1_cur_country',
                        'cco_country_code')

class CompaniesForm(forms.ModelForm):
    class Meta:
        model = CmnCompanies
        fields = companies_field_list

    def __init__(self, *args, **kwargs):
        super(CompaniesForm, self).__init__(*args, **kwargs)

        for field in CmnCompanies._meta.fields:
            if field.name in companies_field_list and field.name not in ['comp_email','url', 'cc1_currency_code','cc1_cur_country','cco_country_code']:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})


class BusinessUnitsForm(forms.ModelForm):
    class Meta:
        model = CmnBusinessUnits
        exclude = ('comp_address_line2','comp_address_line3')