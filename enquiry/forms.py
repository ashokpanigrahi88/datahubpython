from django import forms
from common import (dbfuncs, sysutil,commonutil)



class IteminLocationForm(forms.Form):
    location = forms.CharField(max_length=30,required=False,initial="",label="Location",
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem(None,sysutil.INV_LOCATIONS_L)))
    sub_location = forms.CharField(max_length=30,label='Sub Location', required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    sub_location_group = forms.CharField(max_length=30,required=False,initial="",
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem(None,sysutil.CMN_LOOKUP_CODES_L,
                                                                         'SUB_LOCATION_GROUP_CODE')))
    sub_location_type = forms.CharField(max_length=30,required=False,initial="",
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem(None,sysutil.CMN_LOOKUP_CODES_L,
                                                                         'SUB_LOCATION_TYPES')))
    item_number = forms.CharField(max_length=30,label='Item Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    item_name = forms.CharField(max_length=30,label='Item Name ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    qty_filter = forms.CharField(max_length=10,label='Qty Filter',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['large'],
                                        choices=sysutil.populatelistitem('QTY_FILTER',None)))
    item_id = forms.IntegerField(label="", widget=forms.HiddenInput)

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(IteminLocationForm, self).__init__(*args, **kwargs)
        self.fields['item_number'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

#ItemInLocationFormSet =  formset_factory(IteminLocationForm)


class FindInvoiceForm(forms.Form):
    invoice_number = forms.CharField(max_length=30,label='Invoice Number',required=False,
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
    batch_name = forms.CharField(max_length=30,label='Batch Name', required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))

    invoice_type = forms.CharField(max_length=30,label='Invoice Type',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem('INVOICE_TYPE',None)))
    invoice_status = forms.CharField(max_length=30,label='Invoice Status',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem('INVOICE_STATUS',None)))
    balance_total = forms.CharField(max_length=30,label='Balance Total',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                     choices=sysutil.populatelistitem('QTY_FILTER',None)))
    invoice_id = forms.IntegerField(label="", widget=forms.HiddenInput)
    invoice_header_id = forms.IntegerField(label="", widget=forms.HiddenInput)

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindInvoiceForm, self).__init__(*args, **kwargs)
        self.fields['invoice_number'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()



class FindItemForm(forms.Form):
    item_number = forms.CharField(max_length=30,label='Item Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    item_name = forms.CharField(max_length=30,label='Item Name ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    item_id = forms.IntegerField(label="", widget=forms.HiddenInput)

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindItemForm, self).__init__(*args, **kwargs)
        self.fields['item_number'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()


class FindItemStatusForm(forms.Form):
    item_number = forms.CharField(max_length=30,label='Item Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    item_name = forms.CharField(max_length=30,label='Item Name ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    supplier_name  = forms.CharField(max_length=30,label='Supplier Name ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    category_name = forms.CharField(max_length=30,label='Category',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    sub_category_name = forms.CharField(max_length=30,label='Sub Category ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    item_status = forms.CharField(max_length=30,label='Item Status ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    item_id = forms.IntegerField(label="", widget=forms.HiddenInput)
    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindItemStatusForm, self).__init__(*args, **kwargs)
        self.fields['item_number'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

class FindDateForm(forms.Form):
    date_from = forms.DateField(label="Date From", required=True,
        widget=forms.DateInput(attrs={
            'class': 'datepicker',
            'data-target': '#datetimepicker1',
            'style' :sysutil.DISPLAY_FIELD_WIDTH['small']['style']
                        }))
    date_to = forms.DateField(label="Date To", required=False,
        widget=forms.DateInput(attrs={
            'class': 'datepicker',
            'data-target': '#datetimepicker1',
            'style' :sysutil.DISPLAY_FIELD_WIDTH['small']['style']
                             }))

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindDateForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()


class FindCustomerForm(forms.Form):
    customer_number = forms.CharField(max_length=30,label='Cust Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    customer_name = forms.CharField(max_length=30,label='Customer Name ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    billto_address_line1 = forms.CharField(max_length=30,label='BillTo Address ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))
    billto_post_code = forms.CharField(max_length=30,label='BillTo Post Code ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    shipto_address_line1 = forms.CharField(max_length=30,label='BillTo Address ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))
    shipto_post_code = forms.CharField(max_length=30,label='Shipto Post Code ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    email  = forms.CharField(max_length=100,label='email ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))
    phone1 = forms.CharField(max_length=30,label='Phone ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))
    customer_id = forms.IntegerField(label="", widget=forms.HiddenInput)
    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindCustomerForm, self).__init__(*args, **kwargs)
        self.fields['customer_name'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()


class FindSupplierForm(forms.Form):
    supplier_number = forms.CharField(max_length=30,label='Supplier Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    supplier_name = forms.CharField(max_length=30,label='Supplier Name ',required=False,
                                   widget=forms.TextInput(
                                       attrs={
                                            'style': sysutil.DISPLAY_FIELD_WIDTH['mediumval'],
                                            'class': "basicAutoComplete",
                                            'data-url': "/enquiry/autoc_suppliername/"}
                                           ))
    address_line1 = forms.CharField(max_length=30,label='Address ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))
    post_code = forms.CharField(max_length=30,label='Post Code ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    email  = forms.CharField(max_length=100,label='email ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))
    phone1 = forms.CharField(max_length=30,label='Phone ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))
    supplier_id = forms.IntegerField(label="", widget=forms.HiddenInput)

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindSupplierForm, self).__init__(*args, **kwargs)
        self.fields['supplier_name'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

class ModelFieldsForm(forms.Form):
    model = None
    available_fields = forms.CharField(max_length=30,required=False,initial="",label='Available Fields',
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['large'],
                                        choices=commonutil.choice_modelcharfields(model)))

    field_contains = forms.CharField(max_length=30,label='Field Contanis',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))

    def __init__(self,hiddenfields:[]=[] , modelobject=None , *args, **kwargs):
        super(ModelFieldsForm, self).__init__(*args, **kwargs)
        if not modelobject:
            print('kwargs******',modelobject)
            self.model = modelobject
            self.fields['available_fields'].widget = forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['large'],
                                        choices=commonutil.choice_modelcharfields(self.model))
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()


class SupplierForm(forms.Form):
    supp_number = forms.CharField(max_length=30,label='Supplier Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],))
    supplier = forms.CharField(max_length=30,required=False,initial="",
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['large'],
                                        choices=sysutil.populatelistitem(None,sysutil.AP_SUPPLIERS_L
                                                                         )))
    supplier_id = forms.IntegerField(label="", widget=forms.HiddenInput)

    def __init__(self, hiddenfields:[]=[],  modelobject=None ,  *args, **kwargs):
        super(SupplierForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()


class SupplierTransForm(SupplierForm):
    po_number  = forms.CharField(max_length=30,label='PO Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],))
    goodsin_number  = forms.CharField(max_length=30,label='GoodsIn Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],))
    status   = forms.CharField(max_length=30,label='Status',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],))
    po_header_id = forms.IntegerField(label="", widget=forms.HiddenInput)
    grn_id = forms.IntegerField(label="", widget=forms.HiddenInput)
    def __init__(self, hiddenfields:[]=[],  modelobject=None ,   *args, **kwargs):
        super(SupplierTransForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()
# Create your views here.


class DispatchFindForm(forms.Form):
    dispatch_number = forms.CharField(max_length=30, label='Dispatch Numberr', required=False,
                                widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'], ))
    veihcle_registration = forms.CharField(max_length=30, label='Registration', required=False,
                                     widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'], ))
    driver_name = forms.CharField(max_length=30, label='Driver Name', required=False,
                                     widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'], ))
    contact_name = forms.CharField(max_length=30, label='Contact Name', required=False,
                                     widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'], ))


    def __init__(self, hiddenfields: [] = [], modelobject=None, *args, **kwargs):
        super(DispatchFindForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()
# Create your views here.

class FindSalesOrderForm(FindDateForm):
    customer = forms.CharField(max_length=30,label='Customer',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                                        ))
    order_number = forms.CharField(max_length=30,label='Order Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    batch_name = forms.CharField(max_length=30,label='Batch Name', required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    order_type = forms.CharField(max_length=30,label='Order Type',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem('ORDER_TYPE',None)))
    order_status = forms.CharField(max_length=30,label='Order Status',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem('INVOICE_STATUS',None)))
    order_source = forms.CharField(max_length=30,label='Order Source',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem(None,sysutil.CMN_LOOKUP_CODES_L,'SALES_ORDER_SOURCE')))
    order_category = forms.CharField(max_length=30,label='Order Category',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem(None,sysutil.CMN_LOOKUP_CODES_L,'SALES_ORDER_CATEGORY_CODE')))
    order_header_id = forms.IntegerField(label="", widget=forms.HiddenInput)
    customer_id = forms.IntegerField(label="", widget=forms.HiddenInput)

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindSalesOrderForm, self).__init__(*args, **kwargs)
        self.fields['order_number'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()


class FindReqForm(FindDateForm):

    picked_location = forms.CharField(max_length=30,required=False,initial="",label="Picked Location",
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem(None,sysutil.INV_LOCATIONS_L)))
    received_location = forms.CharField(max_length=30,required=False,initial="",label="Requested Location",
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem(None,sysutil.INV_LOCATIONS_L)))
    requisition_number = forms.CharField(max_length=30,label='Requisition Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    req_status = forms.CharField(max_length=30,label='Status',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem('REQUISITION_STATUS',None)))
    """     req_type = forms.CharField(max_length=30,label='Type',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem(None,sysutil.CMN_LOOKUP_CODES_L,'INV_REQUISITION_TYPE')))
                                        """
    req_category = forms.CharField(max_length=30,label='Category',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem(None,sysutil.CMN_LOOKUP_CODES_L,'INV_REQUISITION_CATEGORY')))
    requisition_id = forms.IntegerField(label="", widget=forms.HiddenInput)

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindReqForm, self).__init__(*args, **kwargs)
        self.fields['requisition_number'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()


class FindReqLinesForm(FindReqForm):

    picked_sub_location = forms.CharField(max_length=30,label='Picked Sub Location', required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    received_sub_location = forms.CharField(max_length=30,label='Requested Sub Location', required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    item_number = forms.CharField(max_length=30,label='Item Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    item_name = forms.CharField(max_length=30,label='Item Name ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    qty_filter = forms.CharField(max_length=10,label='Qty Filter',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['large'],
                                        choices=sysutil.populatelistitem('QTY_FILTER',None)))
    requisition_id = forms.IntegerField(label="", widget=forms.HiddenInput)
    item_id = forms.IntegerField(label="", widget=forms.HiddenInput)
    requisition_line_id = forms.IntegerField(label="", widget=forms.HiddenInput)

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindReqLinesForm, self).__init__(*args, **kwargs)
        self.fields['item_number'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()


class FindCategoryForm(forms.Form):
    category_name = forms.CharField(max_length=30,label='Category Name',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    sub_category_name = forms.CharField(max_length=30,label='Sub Category  Name ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    category_id = forms.IntegerField(label="",widget=forms.HiddenInput)
    sub_category_id = forms.IntegerField(label="",widget=forms.HiddenInput)

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        print('******* hiddenfields', hiddenfields)
        super(FindCategoryForm, self).__init__(*args, **kwargs)
        self.fields['category_name'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            print('******* hiddenfields', hiddenfields)
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()
                self.fields[hf].initial = ""


class FindMovementForm(FindDateForm):
    from_location = forms.CharField(max_length=30,required=False,initial="",label="From  Location",
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem(None,sysutil.INV_LOCATIONS_L)))
    from_sub_location = forms.CharField(max_length=30,label='From Sub Location',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    to_location = forms.CharField(max_length=30,required=False,initial="",label="To Location",
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem(None,sysutil.INV_LOCATIONS_L)))
    to_sub_location = forms.CharField(max_length=30,label='To Sub Location',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    batch_name = forms.CharField(max_length=30,label='Batch',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))

    movement_type = forms.CharField(max_length=30,label='Movement Type',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem('MOVEMENT_TYPE',None)))
    movement_status = forms.CharField(max_length=30,label='Movement Status',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem('MOVEMENT_STATUS',None)))
    item_number = forms.CharField(max_length=30,label='Item Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    item_name  = forms.CharField(max_length=30,label='Item Name',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    item_id = forms.IntegerField(label="", widget=forms.HiddenInput)
    movement_id = forms.IntegerField(label="", widget=forms.HiddenInput)
    iim_movement_header_id = forms.IntegerField(label="", widget=forms.HiddenInput)

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindMovementForm, self).__init__(*args, **kwargs)
        self.fields['item_number'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()


class FindStkTakeForm(FindDateForm):
    location = forms.CharField(max_length=30,required=False,initial="",label="Location",
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem(None,sysutil.INV_LOCATIONS_L)))
    sub_location = forms.CharField(max_length=30,label='Sub Location',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    batch_name = forms.CharField(max_length=30,label='Batch',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))

    stktake_type = forms.CharField(max_length=30,label='Stock Take Type',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem(None,sysutil.INV_STKTAKE_TYPES_L)))

    stktake_status = forms.CharField(max_length=30,label='Status',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem('INVOICE_STATUS',None)))
    item_number = forms.CharField(max_length=30,label='Item Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    item_name  = forms.CharField(max_length=30,label='Item Name',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    item_count_header_id  = forms.IntegerField(label='',required=False,
                                   widget=forms.HiddenInput)
    item_id = forms.IntegerField(label="", widget=forms.HiddenInput)
    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindStkTakeForm, self).__init__(*args, **kwargs)
        self.fields['item_number'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

class ItemSearchForm(FindDateForm):
    supplier =  forms.CharField(max_length=30,label='Supplier',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    category = forms.CharField(max_length=30,label='Category',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem(None,sysutil.INV_ITEM_CATEGORIES_l)))
    sub_category = forms.CharField(max_length=30,label='Category',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem(None,sysutil.INV_ITEM_SUB_CATEGORIES_l)))
    qty_filter = forms.CharField(max_length=10,label='In Stock',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['large'],
                                        choices=sysutil.populatelistitem('QTY_FILTER',None)))
    advanced = forms.CharField(max_length=30,label='Advanced Search',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem(None,sysutil.OTHER_ITEM_SEARCH_CRITERIA_l)))
    location = forms.CharField(max_length=30,required=False,initial="",label="Location",
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem(None,sysutil.INV_LOCATIONS_L)))
    manufacturer = forms.CharField(max_length=30,label='Manufacturer',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem(None,sysutil.INV_MANF_L)))
    season = forms.CharField(max_length=30,label='Season',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem(None,sysutil.CMN_SEASONS_l)))
    item_batch = forms.CharField(max_length=30,label='Item Batch',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem(None,sysutil.INV_ITEM_BATCHES_L)))

    tax_code = forms.CharField(max_length=30,label='Tax Code',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem(None,sysutil.CMN_TAX_CODES_L)))

    item_status = forms.CharField(max_length=30,label='Item Status',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem('ITEM_STATUS')))
    item_number  = forms.CharField(max_length=30,label='Item Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    item_name  = forms.CharField(max_length=30,label='Item Name',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))
    item_id = forms.IntegerField(label="", widget=forms.HiddenInput)

    item_condition = forms.CharField(max_length=30,label='Item Condition',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem(None,sysutil.CMN_LOOKUP_CODES_L,'ITEM_CONDITION')))

    image_hint = forms.CharField(max_length=30,label='Image Hint',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem('IMAGE_HINT')))
    instruction  = forms.CharField(max_length=30,label='Instructione',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))

    price_break =  forms.CharField(max_length=30,label='Instructione',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))

    user_query = forms.CharField(max_length=30,label='Item Condition',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                    choices=sysutil.populatelistitem(None,sysutil.CMN_LOOKUP_CODEDESC_L,'ITEM_SEARCH_QUERIES')))

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(ItemSearchForm, self).__init__(*args, **kwargs)
        self.fields['item_number'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()