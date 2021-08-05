from django import forms
from django.forms import modelformset_factory, inlineformset_factory

from common.models import CmnBanks, CmnBankAccounts
from django.forms import BaseModelFormSet

class UpperCharField(forms.CharField):
    def to_python(self, value):
        return value.upper()


class BanksForm(forms.ModelForm):
    class Meta:
        model = CmnBanks
        fields = ('bank_name','credit_amount','debit_amount')


class BankAccountsForm(forms.ModelForm):
    branch_acctname = UpperCharField()
    class Meta:
        model = CmnBankAccounts
        fields = ('branch_acctname','branch_used_for','swift','iban','bic','currency_code','branch_used_for',
                  'branch_address_line1','bank_branch_city','bank_branch_county','branch_post_code',
                  'country_code', 'branch_phone', 'branch_allow_payin','branch_allow_payout')
        #exclude = ('cb_bank_id','gac_gl_account_id','branch_address_line2','branch_address_line3')
        widgets = {
            'branch_address_line1' : forms.Textarea(attrs={'cols': 22, 'rows': 3}),
        }



