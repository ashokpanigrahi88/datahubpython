from django import forms
from common import (sysutil, commonutil)



class FindOrderForm(forms.Form):
    orderno = forms.CharField(max_length=30,label='Order Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    date_from = forms.DateField(label="From Date", required=True,
        widget=forms.DateInput(attrs={
            'class': 'datepicker',
            'data-target': '#datetimepicker1',
            'style': sysutil.DISPLAY_FIELD_WIDTH['small']['style']
                             }))
    date_to = forms.DateField(label="To Date", required=False,
        widget=forms.DateInput(attrs={
            'class': 'datepicker',
            'data-target': '#datetimepicker1',
            'style': sysutil.DISPLAY_FIELD_WIDTH['small']['style']
                             }))

    storename = forms.CharField(max_length=30,label='Store Name',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem(None,sysutil.INV_LOCATIONS_L)))

    orderid = forms.IntegerField(label="", widget=forms.HiddenInput)

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindOrderForm, self).__init__(*args, **kwargs)
        self.fields['orderno'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

