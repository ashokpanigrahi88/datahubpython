import os
from django.db import connection
from django.conf import settings
import random

# begin List section
from common.translation import VN_C
from common.table_gen import formfilter_queryset, general_exclude_list

AP_SUPPLIER_PROFILES_L = """ SELECT  to_char(sup_profile_ID) ID , sup_profile_name IdValue   from ap_supplier_profiles_v Order By 2"""
CMN_COUNTRIES_L  =  """ SELECT   Country_Code ID , Country_name IdValue  from cmn_countries_v Order By 2"""
CMN_TAX_CODES_L  =  """ SELECT   tax_Code_ID ID , Tax_Code ||'-'||to_char(Tax_rate) IdValue  
           FROM cmn_tax_codes_v Order By 2 """
CMN_CURRENCIES_L  =  """ SELECT   Currency_Code ID , Currency_CODE IdValue  from cmn_currencies_v Order By 2"""
CMN_CURRENCIECOUNTRIES_L  =  """ SELECT   Country_Code ID , Country_CODE IdValue  from cmn_currencies_v Order By 2"""
CMN_CONTAINERS_L  =  """ SELECT to_char(pc_id) ID  , pc_name IdValue  from cmn_containers_v Order By 2"""
CMN_BANKS_l  =  """ SELECT to_Char(bank_id) ID , bank_name IDVALUE  from CMN_BANKS_v Order By 2 """
CMN_BANK_ACCOUNTS_l = """ SELECT   bank_account_ID ID , Branch_acctnumber IDVALUE  from CMN_BANK_ACCOUNTS_v Order By 2  """
CMN_BUSINESS_SECTORS_l  =  """ SELECT  cbs1_id ID , sector_desc IDVALUE from CMN_BUSINESS_SECTORS_v Order By 2 """
CMN_BUSINESS_UNITS_l  =  """ SELECT  bu_id ID ,  bu_name IDVALUE from CMN_BUSINESS_UNITS_v Order By 2 """
CMN_COMPANIES_l  =  """ SELECT  comp_id ID , comp_name IDVALUE from CMN_COMPANIES_v Order By 2 """
CMN_COMMODITYCODES_l  =  """ SELECT  ccc_ID ID , commodity_code IDVALUE from CMN_COMMODITY_CODES_V  Order By 2 """
CMN_FUNCTIONS_l  =  """ SELECT  function_id ID, func_short_name IDVALUE  from CMN_FUNCTIONS_v Order By 2 """
CMN_MENUS_l  =  """ SELECT   menu_id ID  , menu_name IDVALUE from CMN_MENUS_v Order By 2 """
CMN_PAYMENT_METHODS_l = """ SELECT  pmnt_method_id ID , pmnt_method IDVALUE  from CMN_PAYMENT_METHODS_v Order By 2 """
CMN_PAYMENT_TERMS_l  =  """ SELECT  cpt_id ID , terms_name IDVALUE  from CMN_PAYMENT_TERMS_v Order By 2 """
CMN_REASONS_l  =  """ SELECT   reason_code_id ID  , reason_name IDVALUE from CMN_REASONS_v Order By 2 """
CMN_RESPONSIBILITIES_l  =  """ SELECT  resp_id ID , resp_name IDVALUE  from CMN_RESPONSIBILITIES_v Order By 2 """
CMN_SEASONS_l  =  """ SELECT   season_Code_ID ID  , season_code IDVALUE from CMN_SEASONS_v Order By 2 """
INV_MKUPTEMPLATES_l  =  """ SELECT  MkupTemp_ID ID, MkupTemp_Name IDVALUE From  Inv_MkupTemp_Headers Where Active = 'Y' Order by 2"""
CMN_UNIT_OF_MEASUREMENTS_l = """ SELECT  to_Char(uom_id) ID , uom_short_Desc IDVALUE  from CMN_UNIT_OF_MEASUREMENTS_v Order By 2 """ 
CMN_USERS_l  =  """ SELECT   to_Char(user_id) ID , user_name IDVALUE  from CMN_USERS_v Order By 2 """ 
INV_PRICE_TYPES_l = """ SELECT  to_Char(PRICE_TYPE_id) ID  ,  PRICE_TYPE_NAME IDVALUE from INV_PRICE_TYPES_v Order By 2 """ 
INV_ITEM_CATEGORIES_l = """ SELECT  to_Char(CATEGORY_id) ID  , CATEGORY_NAME IDVALUE  from INV_ITEM_CATEGORIES_v Order By 2 """ 
INV_ITEM_SUB_CATEGORIES_l = """ SELECT  to_Char(S.SUB_CATEGORY_id) ID  , S.SUB_CATEGORY_NAME IDVALUE 
                            from INV_ITEM_SUB_CATEGORIES_v S """ 
AR_CUSTOMER_PROFILES_L = """ SELECT   to_char(cust_profile_ID) ID , cust_profile_name IdValue  from ar_customer_profiles_v Order By 2"""
AP_SUPPLIERS_L  =  """ SELECT  supplier_ID ID  , supplier_name IdValue from ap_suppliers_v Order By 2"""
AP_DEFSUPPLIERS_L  =  """ SELECT  supplier_ID ID  , supplier_name IdValue from ap_suppliers_v Where supplier_name like 'GEN%' Order By 2"""
AR_CUSTOMERS_L  =  """ SELECT  customer_ID ID , customer_name IdValue  
                                from ar_customers_v Order By 2"""
AR_CASHCUSTOMERS_L  =  """ SELECT  customer_ID ID , customer_name IdValue  
                                from ar_customers_v where customer_name like 'CASH%' Order By 2"""
GL_ACCOUNT_CODES_l  =  """ SELECT GL_ACCOUNT_ID ID  ,  GL_ACCOUNT_CODE ||'-'|| DESCRIPTION IdValue 
                                         from GL_ACCOUNT_CODES_v Order By 2 """
GL_ACCOUNT_NAMES_l  =  """ SELECT  to_char(GL_ACCOUNT_ID) ID , SHORT_NAME ||'-'|| GL_ACCOUNT_CODE IdValue 
                            from GL_ACCOUNT_CODES_v Order By 2 """
ITEM_SEARCH_L  =  """ SELECT upper(ID) ID  , IDvalue  from item_search_v Order By 2"""
CMN_PRINTERS_L  =  """ SELECT  to_char(printer_id) ID  , printer_name IDValue  from cmn_printers_v Order By 2"""
PICTURE_TYPES_l  =  """ SELECT   upper(ID) ID  , IDvalue from PICTURE_TYPES_v Order By 2""" 
INV_PRICE_BREAK_HEADERS_L  =  """ SELECT  TO_CHAR(PRICE_BREAK_ID) ID ,  NAME IDvalue 
                                from INV_PRICE_BREAK_HEADERS_v Order By 2""" 
OTHER_ITEM_SEARCH_CRITERIA_l  =  """ SELECT  ID  , IDvalue from OTHER_ITEM_SEARCH_CRITERIA_v Order By 2""" 
ITEM_ORDER_BY_l  =  """ SELECT   ID , IDvalue from ITEM_ORDER_BY_v Order By 2""" 
LOCATION_TYPE_L  =  """ SELECT  upper(ID) ID  , IDvalue  from location_type_v Order By 2"""
INV_WEEE_CHARGES_L  =  """ SELECT   to_char(charge_id) ID , name  IDvalue from inv_weee_charges_v Order By 2"""
INV_LOCATIONS_L  =  """ SELECT to_Char(Location_Id) Id , Location_name IdValue   From Inv_Locations_V Order By 2"""
INV_BILLTOLOCATIONS_L  =  """ SELECT to_Char(Location_Id) Id , Location_name IdValue   From Inv_Locations_V Where BILL_TO = 'Y' Order By 2"""
INV_SHIPTOLOCATIONS_L  =  """ SELECT to_Char(Location_Id) Id , Location_name IdValue   From Inv_Locations_V Where SHIP_TO = 'Y' Order By 2"""
INV_SUBLOCATIONS_L  =  """ SELECT to_Char(Location_Id) Id , Location_name IdValue   From Inv_Locations_V Order By 2"""
REPORT_CATEGORY_l  =  """ SELECT ID , IDvalue    from REPORT_CATEGORY_V Order By 2""" 
CMN_LOOKUP_CODES_L = """ SELECT  Lookup_Code ID  , Lookup_Code IDValue
                        from Cmn_Lookup_Codes 
                        Where CLT_LOOKUP_TYPE = '$LOOKUPTYPE$'
                        Order By sl_no, IdValue """
CMN_LOOKUP_CODEDESC_L = """ SELECT  description ID  ,Lookup_Code IDValue
                        from Cmn_Lookup_Codes 
                        Where CLT_LOOKUP_TYPE = '$LOOKUPTYPE$'
                        Order By sl_no, IdValue """
CMN_PERIOD_HEADERS_l = """ SELECT TO_Char(PERIOD_HEADER_ID) ID  , PERIOD_HEADER_NAME IDvalue    
                            from CMN_PERIOD_HEADERS Order By 2"""
INV_ITEM_BATCHES_L  =  """ SELECT BATCH_ID ID  , Name  IDvalue   from INV_ITEM_BATCHES_V Order By 2"""
INV_ITEM_BATCHENAMES_L  =  """ SELECT NAME ID  , Name  IDvalue   from INV_ITEM_BATCHES_V Order By 2"""
INV_PRICEBREAKS_L  =  """ SELECT PRICE_BREAK_ID ID, NAME IDValue FROM INV_PRICE_BREAK_HEADERS_V ORDER BY 2"""
INV_MANF_L  =  """ SELECT manf_id ID,manf_name IDValue FROM inv_manufacturers_v ORDER BY 2"""
REPORT_PREVIEW_MODE_L = """ Select ID,  IDValue from sys_Reportpreviewmode_l Order By 2"""
REPORT_FORMAT_L = """ Select  ID, IDValue from sys_Reportformats_l Order By 2"""
INV_STKTAKE_TYPES_L = """Select Stktake_Type_ID ID , StkTake_Name IdValue From Inv_StkTake_Types  order by 2"""
INV_QUICKCODES_L = """ select QuickCode_ID ID, Quickcode_Name IDVALUE From Inv_QuickCode_headers Order By 2 """
AP_SUPPLIERCODE_L  =  """ SELECT SUPPLIER_NUMBER ID  , SUPPLIER_NAME  IDvalue   from AP_SUPPLIERS_V Order By 2"""
AP_APPROVEDPO_L  =  """ SELECT p.PO_NUMBER ID  , p.PO_NUMBER||':'||s.SUPPLIER_NAME  IDvalue 
                                from PO_HEADERS p,  AP_SUPPLIERS_V s
                                 Where p.sup_supplier_id = s.supplier_id
                                 Order By 2"""
AP_APPROVEDPONOTINGRN_L  =  """ SELECT p.PO_NUMBER ID  , p.PO_NUMBER||':'||s.SUPPLIER_NAME  IDvalue 
                                from PO_HEADERS p,  AP_SUPPLIERS_V s
                                 Where p.sup_supplier_id = s.supplier_id
                                 And   p.Order_Status = 'APPROVED'
                                 and  not Exists (select 1
                                         From PO_GRN_HEADERS x 
                                         Where x.PO_HEADER_ID = p.PO_HEADER_ID)
                                 Order By 2"""
SUGGESTED_QTY_FORMULA_L = """select  upper(id) id , idvalue from suggested_qty_formula_v order by 2"""
# End List Section
# Begin Choices Section
DISPLAY_FIELD_WIDTH = { 'small':{'style': 'width:100px'},
                        'medium':{'style': 'width:125px'},
                        'large':{'style': 'width:175px'},
                        'xlarge':{'style': 'width:225px'},
                        'xxxlarge':{'style': 'width:300px'},
                        'smallval':'width:100px',
                        'mediumval':'width:125px',
                        'largeval':'width:175px',
                        'xlargeval':'width:225px',
                        'xxxlargeval':'width:300px',
                        }

CHOICES = {
'BLANK_CHOICE' : (('', ''),),
'ALL_CHOICE' : (('', 'All'),),
'TRUE_FALSE': ((1, True),(0, False)),
'BARCODE_QTY_HINT': (('BARCODEQTY', 'Barcode Qty'),('BARCODEQTYTIMESSU', 'Barcode Qty * Sales Unit')),
'CREDIT_LIMIT_CRITERIA' : (('NOACTION', 'No Action'),('ALERTUSERONCE', 'Alert User Once Per Transaction'),
                           ('ALERTUSER', 'Alert User'),('STOPTRANSACTION','Stop Transaction')),
'DEFAULT_ITEM_FILTER': (('ALL', 'All Items'),('INSTOCKONLY', 'In Stock Only')),
'ITEM_SUB_LOCATION_HINT': (('DEFAULT', 'Default'),('UNIQUE', 'Unique')),
'DATA_SOURCE': (('CONSTANT', 'CONSTANT'),('SQL QUERY', 'SQL Query')),
'PMNT_TYPE': (('STANDARDT', 'Standard'),('ADDITIONALCHARGE', 'Additional Charrges')),
'BARCODE_REPOSITORY_STATUS': (('NEW', 'New'),('AVAILABLE', 'Available'),('INUSE', 'In Use'),('DELETED', 'Deleted'),
                           ('NOTAVAILABLE', 'Not Available'),('OBSOLETE', 'Obsolete')),
'VALUE_PERCENTAGE': (('VALUE', 'Value'),('PERCENTAGE', 'Percentage')),
'PRICE_TYPE': (('VALUE', 'Value'),('PERCENTAGE', 'Percentage'),('SELLINGPRICE', 'Sellingprice')),
'YES_NO' : (('Y', 'Yes'),('N', 'No')),
'CURRENCY_RATE_TYPE' : (('MANUAL', 'Manual'),('ONEOFF', 'Oneoff'),('AUTOMATIC', 'Automatic')),
'COST_PRICE_FORMULA' : (('LASTBOUGHTPRICE', 'Last Bought Price'),('AVERAGEPRICE', 'Average Price'),('USERMAINTAINED', 'User Maintained')),
'INVOICE_MATCHING_OPTION' : (('2WAY', '2 Way (Must have PO)'),('3WAY', '3 Way (Must have GRN)'),('1WAY', '1 Way (No PO , No GRN)')),
'PO_PRICE_SELECTION' : (('POPRICE', 'PO Price)'),('BASEPRICE', 'Base Cost Price'),
                             ('LASTBOUGHTPRICE', 'Last Bought Price'),('SUPPLIERPRICE', 'Supplier Price'),('FOB', 'FOB/FC Unit Cost')),
'PO_PRINT_NOTE_CRITERIA' : (('PO', 'Purchase Order)'),('GRN', 'Goods Receipt'),('ALL', 'All')),
'ITEM_RECEIPT_TYPE' : (('INCASESIZE', 'In Cases)'),('INUNITS', 'In Units)'),),
'STOCK_TAKE_TYPE' : (('ANNUAL', 'Annual'),('ADHOC', 'Ad-hoc'),('INITIAL', 'Initial')),
'ITEM_COUNT_METHOD' : (('AUTOMATIC', 'Automatic'),('MANUAL', 'Manual')),
'ITEM_NUMBERING' : (('AUTOMATIC', 'Automatic'),('MANUAL', 'Manual')),
'PRICE_CHECK_HINT' : (('NOSTOCK', 'Hide Stock in Price Check'),('SHOWSTOCK', 'Show Stock in Price Check')),
'PRIMARY_SUBLOC_HINT' : (('PRIMARY', 'Get Primary Sub Location'),('NEXTAVAILABLE', 'Get Next Available Sub Location'),
                         ('DEFAULT', 'Default'),('NEXTAVAILABLESALES', 'Get Next Available SALES Location')),
'ITEM_COUNT_PICK_METHOD' : (('ALL', 'All'),('MANUAL', 'Manual'),('RANDOM', 'Random'),('SEQUENTIAL','Sequential')),
'INV_REQUISITION_HINT': (('NONE', 'None'),('AUTOMATIC', 'Auto Create Requisition From Sales Order')),
'MARKUP_TYPE' : (('C', 'Markup'),('M', 'Margin'),('R', 'Profit on Return')),
'PRICE_BREAK_CRITERIA' : (('ITEM', 'By Item'),('FORMULA', 'By Formula')),
'PRICE_BASIS' : (('VAT', 'Including VAT/Tax'),('NOVAT', 'Excluding VAT/Tax')),
'POPULATE_STOCK_HISTORY' : (('NONE', 'None'),('DYNAMIC', 'Dynamic')),
'REPORT_PREVIEW_MODE' : (('CACHE', 'Preview'),('CACHE,PRINTER', 'Preview,Print'),('PRINTER','Print'),('FILE','File'),
                          ('CACHE,PRINTER,FILE', 'Preview,Print,File'),('PREVIEW,FILE', 'Preview,File'), ),
'REPORT_OUTPUT_FORMAT' : (('PDF', 'PDF'),('HTML', 'HTML'),('MAIL','email'),('CSV','csv'), ),
'REPORT_EXECUTION_MODE' : (('SERVER', 'Server'),('URL', 'url')),
'QTY_FORMAT' : (('FM999999999999.99', 'with Decimal'),('FM999999999999', 'No Decimnal')),
'MERGE_TYPE' : (('HTML', 'HTML'),('XML', 'XML'),('PLAIN', 'Text')),
'RECORD_OWNER' : (('SYSTEM', 'System'),('USER', 'User Defined'),('ANY', 'Any')),
'REPLENISHMENT_OPTIONS' : (('CENTRALLYREPLENISHED', 'Centrally Replenished'),
                           ('LOCALLYREPLENISHED', 'Locally Replenished'),('NOTDEFINED', 'Not Defined')),
'INVOICE_STATUS' : (('NEW', 'New'),('APPROVED', 'Approved'),('CANCELLED','Cancelled'),('CLOSED','Closed')),
'REQUISITION_STATUS' : (('NEW', 'New'),('APPROVED', 'Approved'),('PICKED','Picked'),('FULFILLED','Fulfilled'),
                        ('RECEIVED','Received'),('CANCELLED','Cancelled'),('CLOSED','Closed')),
'MOVEMENT_STATUS' : (('NEW', 'New'),('APPROVED', 'Approved'),('TRANSFERRED','Transferred'),('INTRANSIT','In Transit'),
                        ('RECEIVED','Received'),('CANCELLED','Cancelled'),('CLOSED','Closed')),
'MOVEMENT_TYPE' : (('INTERNALTOINTERNAL', 'Internal to Innternal'),('INTEROFFICE', 'Location to Location'),
                   ('EXTERNALTOINTERNAL','External to Internal'),('INTERNALTOEXTERNAL','Internal to External'),),
'INVOICE_TYPE' : (('INVOICE', 'Invoice'),('STANDARD', 'Standard'),('CREDIT NOTE', 'Credit Note')),
'ORDER_TYPE' : (('SALESORDER', 'Sales Order'),('BLANKETORDER', 'Blanket Order'),('RESERVEORDER', 'Reserve Order'),('SALESCREDIT', 'Sales Credit'),
                ('QUOTATION', 'Quotation')),
'INVOICE_TRANS' : (('Invoice', 'Invoice'),('LINES', 'Lines/Items'), ('Payments','Payments')),
'DISPATCH_TYPE' : (('OUTBOUND', 'Outbound'),('INBOUND', 'Inbound'), ('DISPATCH','Dispatch')),
'CASHING_TYPE' : (('LOCATION', 'Location'),('TERMINAL', 'Terminal'), ('USER','User')),
'SECURITY_LEVEL' : (('USER', 'User'),('SYSTEM', 'System')),
'SPECIAL_OFFER_HINT' : (('NOOFFERONPRICEBREAK', 'No Offer on Price Break'),('APPLYOFFERONPRICEBREAK', 'Apply Offer on Price Break'),
                        ('PRICEBREAKONLY', 'Price Break Only'),('SPECIALOFFERONLY', 'Special Offer Only'),
                ('APPLYSPPBONCUSTPRICE', 'Apply Offer/PB On Customer Price'), ('NONE', 'None') ),
'QTY_FILTER' : (('> 0', 'Positive'),('= 0','Zero'), ('< 0','Negative'),),
'MODULES' : (('ALL', 'All'),('RECEIVABLE', 'Receivable'),('PAYABLE','Payable')),
'CASETYPE' : (('MIXED' , 'MiXeD' ), ('UPPER','UPPER' ), ('INITCAP','Initcap' ),('LOWER','lower')),
'BRANCH_USED_FOR' : (('SUPPLIER' , 'Supplier' ), ('CUSTOMER','Customer' ), ('EMLPYEE','Employee' ),('INTERNAL','Internal')),

'PRICE_TYPE_GROUP_CODE' : (('SELLINGPRICE' , 'Selling Price' ), ('OFFERPRICE','Offer Price' ),
                           ('RRP','RRP' ),('COST','Cost') ,('RETAILPRICE','Retail Price')),
'BUSINESS_TYPE': (('WHOLESALE','WHOLESALE'), ('RETAIL','RETAIL'),('FASHION','FASHION'),
                 ('FASCILITY', 'FASCILITY MANAGEMENT'),
	             ('MANUFACTURING','MANUFACTURING'), ('LOGISTICS','LOGISTICS'),
                 ('DISTRIBUTORS','DISTRIBUTORS'), ('E-COMMERCE','E-COMMERCE')),
'ITEM_STATUS': (('ACTIVE','Active'), ('DISCONTINUED','Discontinued'),('FAULTY','Faulty'),
                 ('DONOTUSE', 'Do Not Use'),
	             ('DELETED','Deleted'), ('TEMPLATE','Template'),),
'IMAGE_HINT': (('AVAILABLE','Available'), ('NOTAVAILABLE','Not Available'),('WAITING','Waiting'),
                 ('WIP', 'Work in Progress'),
	             ('NOTREQUIRED','Not Required'), ('GETLATESTCOPY','Get Latest Copy'),)
    }
#End Choices Section

def get_sequenceval(p_sequence):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT "  + p_sequence +" val From Dual")
            row = cursor.fetchone()
            print(row)
            return row[0]
    except Exception as ex:
        return None

def random_string():
    return str(random.randint(1, 99999999))

def images_path():
    return os.path.join(settings.LOCAL_FILE_DIR, 'images')


def uploads_path():
    return os.path.join(settings.LOCAL_FILE_DIR, 'uploads')

columnname_dict = {
    'country_code_english': 'Country Code',
    'country_name_english': 'Country Name',
}

tablename_dict = {
    'client_english': 'Clients',
    'user_english': 'Users',
}
PUB_PAGE_LINES = 15
verbose_dict = {**columnname_dict, **tablename_dict}


def VN_Cold(p_column, p_language = 'english'):
    verbosekey = p_column+'_'+p_language
    if verbosekey not in verbose_dict:
        return p_column.capitalize().replace('_', ' ')
    return verbose_dict[verbosekey]

def VN_Told(p_table, p_language = 'english'):
    return VN_C(p_column=p_table, p_language=p_language)


def populatelistitem(choicename:str = None ,
                     list_sql:str = """ SELECT ''  IDVALUE , Null ID from Dual""",
                     lookp_type:str = '', p_addblank:bool = True):
    try:
        if choicename is not None and  choicename != "":
            if p_addblank:
                return CHOICES['BLANK_CHOICE'] + CHOICES[choicename]
            else:
                return CHOICES['ALL_CHOICE'] + CHOICES[choicename]

        if not list_sql:
            return CHOICES['BLANK_CHOICE']
        if list_sql.replace(' ', '').upper().startswith('SELECT'):
            sql = list_sql.replace('$LOOKUPTYPE$',lookp_type)
        else:
            sql = 'SELECT  ID , IDVALU FROM '+list_sql
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = list(cursor.fetchall())
            if rows:
                choices = list(CHOICES['BLANK_CHOICE'])
                rows.append(choices[0])
                return rows
            return CHOICES['BLANK_CHOICE']
    except:
        return CHOICES['BLANK_CHOICE']


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def get_form_context(p_model, p_tablefields):
    MODEL = p_model
    PK_NAME = MODEL._meta.pk.name
    MODEL_FIELD_LIST = p_tablefields
    non_editable_list = [field.name for field in MODEL._meta.fields if not field.editable]
    exclude_list = general_exclude_list + non_editable_list
    form_field_list = [field for field in MODEL_FIELD_LIST['fields'] if field not in exclude_list]
    form_field_dict = {x[0]: x[1] for x in list(zip(MODEL_FIELD_LIST['fields'], MODEL_FIELD_LIST['headers'])) if
                       x[0] in form_field_list}
    return PK_NAME, non_editable_list, exclude_list,form_field_list,form_field_dict