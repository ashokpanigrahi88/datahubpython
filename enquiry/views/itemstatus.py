from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.forms import ModelForm

from common.models  import (InvItemMasters)
from common import (commonutil, sysutil, dbfuncs)
from django import forms
from enquiry import enquirygrids
from enquiry.forms import FindItemStatusForm

#Create your form here

REP_ITEMSTATUS_QUERY={
'fields':['item_number','item_name','supplier_name','category_name','sub_category_name','item_status','min_qty',
          'max_qty','qty_inorder','last_grn_qty','last_po_qty','last_sold_qty','days_since_last_sold',
          'days_since_po','days_since_last_bought','days_since_created','lead_time','safety_net_days',
          'typical_daily_usage_stat','min_qty_suggested','max_qty_suggested','min_max_cal_type_stat',
          'qty_sold','sal_week1','sal_week2','sal_week3','sal_week4','sal_week5','sal_week6',
          'six_week_sales','avg_week_sales','sal_lastmonth','sal_jan','sal_feb','sal_mar',
          'sal_apr','sal_may','sal_jun','jan_jun_sales','avg_jan_jun_sales','sal_jul','sal_aug',
          'sal_sep','sal_oct','sal_nov','sal_dec','jul_dec_sales','avg_jul_dec_sales','sal_ytd',
          'created_by','creation_date','last_adjust_date','last_sold_date','last_bought_date','last_po_date',
          'bu_id','item_id','sup_supplier_id','iic_category_id','iisc_sub_category_id',
          'group_stock','case_cp','unit_cp','case_unit','stock_value','stockable','valuable',
          'virtual_stock','supplier_number','order_cycle_type','order_cycle','manufacturer','season',
          'qty_returned_to_supplier','qty_returned_from_customer','qty_adjusted','qty_goodsin',
          'qty_reserved','qty_allocated','qty_instock','qty_reserved_invoiced','qty_reserved_grn',
          'qty_reserved_po','qty_reserved_balance','qty_reserved_fulfilled','iwc_charge_id',
          'update_source','ipbh_price_break_id','pallet_qty','item_comment','item_specifications',
          'supplier_notes3','supplier_notes2','supplier_notes1','customer_notes3','customer_notes2',
          'customer_notes1','item_style','item_fitting','item_size','item_colour','goodsin_location_id',
          'sales_location_id','gross_unit_weight','gross_case_weight','gac_gl_account_id','cmc_pc_id',
          'im_manf_id','ctc_tax_code_id','warranty_period','group4','group3','group2','group1','whose_for',
          'sales_location_qty','reservable','net_ingredient','flagindateto','flagindatefrom','flaginwebexport',
          'print_picture','net_case_weight','net_unit_weight','warrantied','serial_numbered','serviceditem',
          'saleable','purchaseable','volume_uomid','weight_uomid','unit_volume','unit_height','unit_width',
          'unit_length','case_volume','case_height','case_width','case_length','similar_item_id','weighed_item',
          'alternate_unit_cp','alternate_case_cp','qtyinstock','short_desc','opening_balance','record_status',
          'last_updated_by','last_update_date','track_usage','supplier_product_code','picturetype','picturename',
          'season_code_id','closing_balance','delete_flag','long_desc','stock_holding_unit','reorder_uomid',
          'reorder_qty','reorder_interval','stock_take_category','item_class_category','item_dimension_type',
          'item_dimension','trading_casecp','trading_unitcp','average_unitcp','last_bought_unitcp','end_date_active',
          'start_date_active','balancesheet_gl_account_id','pnl_gl_account_id','pricevariance_gl_account_id',
          'costofsales_gl_account_id','sales_gl_account_id','inner_qty','freight','take_snapshot','demo_video_file',
          'similar_item_concated','enforce_tax_code','apply_offer','picturename3','picturename2','picturename1',
          'technical_specs_file','technical_specs','freight_price_criteria','enforce_reorder_qty','external_reference',
          'ccc_id','delivery_charges','supplier_unit_cp','supplier_case_cp','min_pb_qty','mkuptemp_id','publish_to_web',
          'default_label_name','replenishment_options','replenished_from_location','key_words','exchange_rate','image_hint',
          'instrunction','item_condition','stp_id','stp_level1_id','stp_level2_id','stp_level3_id','stp_level4_id',
          'stp_level5_id','stp_level6_id','unit_volumetric_weight','case_volumetric_weight','web_expedite_flag',
          'www_parent_sku','www_relationship_type','www_variation_theme','www_package_quantity','www_design_pattern',
          'www_parentage','www_barcode_type','freight_line_id','freight_name',],
'headers':['Item Number','Item Name','Supplier Name','Category Name','Sub Category Name','Item Status','Min Qty','Max Qty',
           'Qty Inorder','Last Grn Qty','Last Po Qty','Last Sold Qty','DaysSince Sold','DaysSince PO','DaysSince GRN','DaysSince Created',
           'Lead Time','SafetyNet','DailyUsage','SuggestedMIN','SuggestedMAX','CurrentMAX','Qty Sold','Week1','Week2',
           'Week3','Week4','Week5','Week6','Six Week','Avg Weekly','Last Month','JAN','FEB','MAR','APR','MAY','JUN',
           'JAN -JUN SALE','Avg JAN -JUN SALES','JUL','AUG','SEP','OCT','NOV','DEC','JUL -DEC SALE','Avg JUL -DEC SALES',
           'Year to date','Created By','Creation Date','Last Adjust Date','Last Sold Date','Last Bought Date','Last Po Date',
           'Bu Id','Item Id','Supplier Id','Category Id','Sub Category Id','In Stock','Case Cp','Unit Cp',
           'Case Unit','Stock Value','STK','VAL','Virtual Stock','Supplier Number','Order Cycle Type',
           'Order Cycle','Manufacturer','Season','Qty Returned To Supplier','Qty Returned From Customer',
           'Qty Adjusted','Qty Goodsin','Qty Reserved','Qty Allocated','Qty Instock','Qty Reserved Invoiced',
           'Qty Reserved Grn','Qty Reserved Po','Qty Reserved Balance','Qty Reserved Fulfilled','Iwc Charge Id',
           'Update Source','Ipbh Price Break Id','Pallet Qty','Item Comment','Item Specifications','Supplier Notes3',
           'Supplier Notes2','Supplier Notes1','Customer Notes3','Customer Notes2','Customer Notes1','Item Style',
           'Item Fitting','Item Size','Item Colour','Goodsin Location Id','Sales Location Id',
           'Gross Unit Weight','Gross Case Weight','Gac Gl Account Id','Cmc Pc Id','Im Manf Id',
           'Ctc Tax Code Id','Warranty Period','Group4','Group3','Group2','Group1','Whose For',
           'Sales Location Qty','Reservable','Net Ingredient','Flagindateto','Flagindatefrom',
           'Flaginwebexport','Print Picture','Net Case Weight','Net Unit Weight','Warrantied',
           'Serial Numbered','Serviceditem','Saleable','Purchaseable','Volume Uomid','Weight Uomid',
           'Unit Volume','Unit Height','Unit Width','Unit Length','Case Volume','Case Height',
           'Case Width','Case Length','Similar Item Id','Weighed Item','Alternate Unit Cp',
           'Alternate Case Cp','Qtyinstock','Short Desc','Opening Balance','Record Status',
           'Last Updated By','Last Update Date','Track Usage','Supplier Product Code','Picturetype',
           'Picturename','Season Code Id','Closing Balance','Delete Flag','Long Desc',
           'Stock Holding Unit','Reorder Uomid','Reorder Qty','Reorder Interval','Stock Take Category',
           'Item Class Category','Item Dimension Type','Item Dimension','Trading Casecp','Trading Unitcp',
           'Average Unitcp','Last Bought Unitcp','End Date Active','Start Date Active',
           'Balancesheet Gl Account Id','Pnl Gl Account Id','Pricevariance Gl Account Id','Costofsales Gl Account Id',
           'Sales Gl Account Id','Inner Qty','Freight','Take Snapshot','Demo Video File',
           'Similar Item Concated','Enforce Tax Code','Apply Offer','Picturename3','Picturename2',
           'Picturename1','Technical Specs File','Technical Specs','Freight Price Criteria',
           'Enforce Reorder Qty','External Reference','Ccc Id','Delivery Charges',
           'Supplier Unit Cp','Supplier Case Cp','Min Pb Qty','Mkuptemp Id','Publish To Web','Default Label Name',
           'Replenishment Options','Replenished From Location','Key Words','Exchange Rate','Image Hint',
           'Instrunction','Item Condition','Stp Id','Stp Level1 Id','Stp Level2 Id','Stp Level3 Id',
           'Stp Level4 Id','Stp Level5 Id','Stp Level6 Id','Unit Volumetric Weight','Case Volumetric Weight',
           'Web Expedite Flag','Www Parent Sku','Www Relationship Type','Www Variation Theme','Www Package Quantity',
           'Www Design Pattern','Www Parentage','Www Barcode Type','Freight Line Id','Freight Name',],
}


class DetailForm(ModelForm):

    class Meta:
        model = InvItemMasters
        fields = '__all__'
        #exclude = ('customer_id',)


    def __init__(self, *args, **kwargs):
        super(DetailForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True


class FindForm(FindItemStatusForm):

    qty_instock = forms.CharField(max_length=30,label='Qty Instock',required=False,
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                     choices=sysutil.populatelistitem('QTY_FILTER',None)))
    def __init__(self, hiddenfields:[]=[],  *args,**kwargs):
        super(FindForm, self).__init__(*args, **kwargs)
        #self.fields['date_from'].required  = True
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 25
REVERSE = 'enquiry:itemstatus'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class SummaryView(ListView):
    model = InvItemMasters
    template_name = 'enquiry/itemstatus.html'
    paginate_by = PAGE_VAR
    context_object_name = 'rows'
    getvars = {}
    inputparams = {}
    detailform = None
    detailform_raw = None
    queryparams = ""
    child1 = None
    child2 = None

    def get(self, request, *args, **kwargs):
        for key,value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken':
                self.inputparams[key] = value
        self.initial =  self.inputparams
        return super(SummaryView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(SummaryView, self).get_form_kwargs()
        kwargs['hiddenfields'] = []
        return kwargs

    def get_success_url(self):
        print('******* get success url')
        return reverse(REVERSE)

    def form_invalid(self, form, **kwargs):
        print('******* form valid')
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def form_valid(self, form, **kwargs):
        print('******* form valid')
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_queryset(self, *args, **kwargs):
        print('******* get queryset')
        queryset = super().get_queryset()
        self.queryparams = ""
        self.detailform  = None
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'item_number',
                              commonutil.get_key_value(self.inputparams,'item_number'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'item_name',
                              commonutil.get_key_value(self.inputparams,'item_name'),' like ')
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'supplier_name',
                              commonutil.get_key_value(self.inputparams,'supplier_name'),' like ')
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'category',
                              commonutil.get_key_value(self.inputparams,'category_name'),' like ')
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'subcategory',
                              commonutil.get_key_value(self.inputparams,'sub_category_name'),' like ')
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'item_status',
                              commonutil.get_key_value(self.inputparams,'item_status'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'in_stock',
                              commonutil.get_key_value(self.inputparams,'qty_instock'),p_operator="")
        """ 
                self.queryparams =  commonutil.filter_date_range_raw(self.queryparams,'report_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        """
        #REP_ITEMSTATUS_QUERY_V
        print('query params:',self.queryparams)
        if len(self.queryparams) < 10:
            return self.model.objects.none()
        else:
            sql = """Select *
                    From  REP_365DAYSSALESPLUS_V {}  order by item_number """.format(self.queryparams)
            sql = sql.replace(' AND   ','')
            print(sql)
            qs  = dbfuncs.exec_sql(sql, 'dict', columnscase='lower')
        if len(qs) == 1:
            self.detailform_raw = qs[0]
        return qs

    def download_csv(self):
        csvdata = commonutil.download_csv(self.request, self.object_list)
        response = HttpResponse(csvdata, content_type='text/csv')
        return response

    def get_context_data(self, **kwargs):
        print('******* get context')
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        self.form = FindForm(initial=self.initial)
        # Add local context
        context['form'] = self.form
        context['detailform_title'] = 'Details'
        context['detailform_raw'] = self.detailform_raw
        if self.object_list:
            context['rows_tableheader'] ,context['rows_tablecolumns'], _ = enquirygrids.get_grid('ITEMSTATUS')
        return context
