from django import forms
from django.conf import settings
from common.sysutil import CHOICES
from common import (dbfuncs, sysutil)


class PriceCheckForm(forms.Form):
    item_number = forms.CharField(max_length=30,label='Item Number / Barcode');
    fuzzy_search = forms.ChoiceField(label='Fuzzy Search',
                                   choices=CHOICES['YES_NO'], initial='N'
                )


class MoveItemToPrimayForm(forms.Form):
    from_sub_location = forms.CharField(max_length=30,label='From Sub Location', required=True)
    item_number = forms.CharField(max_length=30,label='Item Number / Barcode',required=True);
    quantity = forms.IntegerField(max_value=1000,label='Quantity',required=True)
    to_sub_location = forms.CharField(max_length=30,label='Primary/To  Sub Locaion',required=False)


class SalesOrderPickForm(forms.Form):
    order_number = forms.CharField(max_length=30,label='Order Number', required=False)
    picked_item_number = forms.CharField(max_length=30,label='Item Number / Barcode',required=False,initial='');
    quantity = forms.IntegerField(max_value=10000,label='Quantity',required=False)
    line_id = forms.CharField(max_length=30,label='Scan Pick Barcode',required=False)
    box_slno = forms.CharField(max_length=5,label='Box SlNo',required=False,initial='1')
    order_id = forms.CharField(widget=forms.HiddenInput);
    from_sub_location = forms.CharField(max_length=30,label='From Sub Location', required=False,initial='')
    categorystring = forms.CharField(widget=forms.HiddenInput,initial='TWOWAY');
    pickingconfirmation = forms.CharField(widget=forms.HiddenInput,initial='TWOWAY');
    enable_palleting = forms.CharField(widget=forms.HiddenInput,initial='N');


class SalesOrderQueryForm(forms.Form):
    order_number = forms.CharField(max_length=30,label='Order Number', required=False)
    order_status = forms.CharField(max_length=30,label="", required=False,
                                   widget=forms.HiddenInput)
    Line_status = forms.CharField(max_length=30,label='Line Status', required=False)
    Line_phase = forms.CharField(max_length=30,label='Line Phase', required=False)
    delivery_status = forms.CharField(max_length=30,label='Delivery Status', required=False)
    web_order_number = forms.CharField(max_length=30,label='Web Order Number', required=False)


class ExtMovementForm(forms.Form):
    locationid = 0
    from_ext_location = forms.CharField(max_length=30,label='From External Location',
                                        required=True, initial=dbfuncs.get_externallocation())
    item_number = forms.CharField(max_length=30,label='Item Number / Barcode',required=True);
    quantity = forms.IntegerField(max_value=1000,label='Quantity',required=True)
    to_sub_location = forms.CharField(max_length=30,label='To  Sub Locaion',
                                      initial=dbfuncs.get_primarysubloc('PRIMARY GRN',locationid),
                                      required=False)
    movementtype = forms.CharField(widget=forms.HiddenInput, label="", initial="EXTERNALTOINTERNAL")

    def __init__(self, hiddenfields:[],  *args, **kwargs):
        super(ExtMovementForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()


class CreateGRNForm(forms.Form):
    locationid = 0
    supplier_number = forms.CharField(max_length=30,required=False,initial="",
                                    widget=forms.Select(attrs={'style': 'width:200px'},
                                        choices=sysutil.populatelistitem(None,sysutil.AP_SUPPLIERCODE_L)),
                                    )
    """
    po_number = forms.CharField(max_length=30,required=False,initial="",
                                    widget=forms.Select(
                                        choices=sysutil.populatelistitem(None,sysutil.AP_APPROVEDPONOTINGRN_L))
                                    )
    """
    po_number = forms.CharField(max_length=20, label='PO Number',required=False, initial="");
    delivery_reference = forms.CharField(max_length=30, label='Delivery Reference',required=False);
    goodsin_number = forms.CharField(max_length=30, label='GoodsIn Number',required=False)
    sub_location = forms.CharField(max_length=30, label="Sub Location", required=False);
    item_number = forms.CharField(max_length=30, label="Item Number", required=False);
    delivered_qty = forms.IntegerField(max_value=10000, required=False)
    grn_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    supplier_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    po_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def __init__(self, hiddenfields:[],  *args, **kwargs):
        super(CreateGRNForm, self).__init__(*args, **kwargs)
        self.fields['item_number'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()


class AddToBatchForm(forms.Form):
    batch_name  = forms.CharField(max_length=100,required=False,initial="",label='Batch Name',
                                    widget=forms.Select(attrs={'style': 'width:200px'},
                                        choices=sysutil.populatelistitem(None,sysutil.INV_ITEM_BATCHENAMES_L)),
                                    )
    item_number = forms.CharField(max_length=30,label='Item Number / Barcode',required=True);
    batch_id = forms.CharField(widget=forms.HiddenInput,required=False)

    def __init__(self, hiddenfields:[],  *args, **kwargs):
        super(AddToBatchForm, self).__init__(*args, **kwargs)
        self.fields['item_number'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()
