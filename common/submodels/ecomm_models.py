import datetime
import os
from django.db import models
from django.db.models import Count, Sum, Min, Max
from django.contrib.auth.models import User
from django.urls import reverse
from common.sysutil  import *
from common.translation import  (VN_C, VN_T)
from common import commonutil


class EcommOrderstatusinfo(models.Model):
    orderstatusinfoid = models.BigIntegerField(blank=True, null=True, editable=True, primary_key=True, verbose_name=VN_C('orderstatusinfoid'))
    serialno = models.IntegerField(blank=True, null=True, verbose_name=VN_C('serialno'))
    orderstatus = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('orderstatus'))
    description = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('description'))
    attribute1 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute1'))
    attribute2 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute2'))
    attribute3 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute3'))
    attribute4 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute4'))
    record_status = models.CharField(max_length=1, blank=True, null=True, default='I', editable=True, verbose_name=VN_C('record_status'))
    last_update_date = models.DateTimeField(auto_now=True, blank=True, null=True, editable=True, verbose_name=VN_C('last_update_date'))
    creation_date = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=True, verbose_name=VN_C('creation_date'))
    bu_id = models.IntegerField(blank=True, null=True, default=1, editable=True, verbose_name=VN_C('bu_id'))
    update_source = models.CharField(max_length=30, blank=True, null=True, default='API', editable=True, verbose_name=VN_C('update_source'))
    created_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('created_by'))
    last_updated_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('last_updated_by'))
    delete_flag = models.CharField(max_length=1, blank=True, null=True, default='N', editable=True, verbose_name=VN_C('delete_flag'))
    third_party_source = models.CharField(max_length=30, blank=True, null=True, default='THIS', verbose_name=VN_C('third_party_source'))
    third_party_source_ref = models.CharField(max_length=50, blank=True, null=True, default=-1, verbose_name=VN_C('third_party_source_ref'))
    #tenant_id = models.IntegerField(blank=False, null=False,default=-1)

    class Meta:
        managed = False
        db_table = 'ecomm_orderstatusinfo'
        verbose_name=VN_T('ecomm_orderstatusinfo')

    def __str__(self):
        return self.orderstatus

class EcommOrderinfo(models.Model):
    orderid = models.BigIntegerField(blank=False, null=False, editable=True, primary_key=True, verbose_name=VN_C('orderid'))
    orderdate = models.DateTimeField(blank=False, null=False, verbose_name=VN_C('orderdate'))
    orderno = models.CharField(max_length=100, blank=False, null=False, verbose_name=VN_C('orderno'))
    storeid = models.BigIntegerField(blank=False, null=False, editable=True, verbose_name=VN_C('storeid'))
    paymentstatus = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('paymentstatus'))
    nettotalamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('nettotalamount'))
    taxamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('taxamount'))
    shippingcharges = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('shippingcharges'))
    discountamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('discountamount'))
    grosstotalamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('grosstotalamount'))
    customerid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('customerid'))
    customerfirstname = models.CharField(max_length=200, blank=True, null=True, verbose_name=VN_C('customerfirstname'))
    customerlastname = models.CharField(max_length=200, blank=True, null=True, verbose_name=VN_C('customerlastname'))
    customermobileno = models.CharField(max_length=200, blank=True, null=True, verbose_name=VN_C('customermobileno'))
    customeremail = models.EmailField(max_length=254,blank=True, null=True, verbose_name=VN_C('customeremail'))
    storename = models.CharField(max_length=200, blank=True, null=True, verbose_name=VN_C('storename'))
    deliveryorpickup = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('deliveryorpickup'))
    delpickrequesteddate = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('delpickrequesteddate'))
    delpickrequestedtimeslot = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('delpickrequestedtimeslot'))
    ordertype = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('ordertype'))
    ordernotes = models.CharField(max_length=2000, blank=True, null=True, verbose_name=VN_C('ordernotes'))
    attribute1 = models.CharField(max_length=200, blank=True, null=True, verbose_name=VN_C('attribute1'))
    attribute2 = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('attribute2'))
    attribute3 = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('attribute3'))
    attribute4 = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('attribute4'))
    customer_id = models.BigIntegerField(blank=True, null=True, editable=False, verbose_name=VN_C('customer_id'))
    location_id = models.BigIntegerField(blank=True, null=True, editable=False, verbose_name=VN_C('location_id'))
    status = models.IntegerField(blank=True, null=True, default=1, verbose_name=VN_C('status'))
    row_version = models.IntegerField(blank=True, null=True, verbose_name=VN_C('row_version'))
    record_status = models.CharField(max_length=1, blank=True, null=True, default='I', editable=True, verbose_name=VN_C('record_status'))
    last_update_date = models.DateTimeField(auto_now=True, blank=True, null=True, editable=True, verbose_name=VN_C('last_update_date'))
    creation_date = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=True, verbose_name=VN_C('creation_date'))
    bu_id = models.IntegerField(blank=True, null=True, default=1, editable=True, verbose_name=VN_C('bu_id'))
    update_source = models.CharField(max_length=30, blank=True, null=True, default='API', editable=True, verbose_name=VN_C('update_source'))
    created_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('created_by'))
    last_updated_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('last_updated_by'))
    delete_flag = models.CharField(max_length=1, blank=True, null=True, default='N', editable=True, verbose_name=VN_C('delete_flag'))
    third_party_source = models.CharField(max_length=30, blank=True, null=True, default='THIS', verbose_name=VN_C('third_party_source'))
    third_party_source_ref = models.CharField(max_length=50, blank=True, null=True, default=-1, verbose_name=VN_C('third_party_source_ref'))
    #tenant_id = models.IntegerField(blank=False, null=False,default=-1)
    orderstatusinfoid = models.ForeignKey(EcommOrderstatusinfo, models.DO_NOTHING, blank=True,
                                        null=True, to_field='orderstatusinfoid', db_column='orderstatusinfoid')

    class Meta:
        managed = False
        db_table = 'ecomm_orderinfo'
        verbose_name=VN_T('ecomm_orderinfo')

    def __str__(self):
        return str(self.orderid)


class EcommOrderaddress(models.Model):
    orderaddressid = models.BigIntegerField(blank=False, null=False, editable=True, primary_key=True, verbose_name=VN_C('orderaddressid'))
    billingaddressid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('billingaddressid'))
    billingaddress = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('billingaddress'))
    billingcity = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('billingcity'))
    billingcounty = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('billingcounty'))
    billingpostcode = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('billingpostcode'))
    billingcountry = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('billingcountry'))
    shippingaddressid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('shippingaddressid'))
    shippingaddress = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('shippingaddress'))
    shippingcity = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('shippingcity'))
    shippingcounty = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('shippingcounty'))
    shippingpostcode = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('shippingpostcode'))
    shippingcountry = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('shippingcountry'))
    storeaddressid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('storeaddressid'))
    storeaddress = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('storeaddress'))
    storecity = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('storecity'))
    storecounty = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('storecounty'))
    storepostcode = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('storepostcode'))
    storecountry = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('storecountry'))
    otheraddressid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('otheraddressid'))
    otheraddress = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('otheraddress'))
    othercity = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('othercity'))
    othercounty = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('othercounty'))
    otherpostcode = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('otherpostcode'))
    othercountry = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('othercountry'))
    attribute1 = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('attribute1'))
    attribute2 = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('attribute2'))
    attribute3 = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('attribute3'))
    attribute4 = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('attribute4'))
    status = models.IntegerField(blank=True, null=True, default=1, verbose_name=VN_C('status'))
    row_version = models.IntegerField(blank=True, null=True, verbose_name=VN_C('row_version'))
    record_status = models.CharField(max_length=1, blank=True, null=True, default='I', editable=True, verbose_name=VN_C('record_status'))
    last_update_date = models.DateTimeField(auto_now=True, blank=True, null=True, editable=True, verbose_name=VN_C('last_update_date'))
    creation_date = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=True, verbose_name=VN_C('creation_date'))
    bu_id = models.IntegerField(blank=True, null=True, default=1, editable=True, verbose_name=VN_C('bu_id'))
    update_source = models.CharField(max_length=30, blank=True, null=True, default='API', editable=True, verbose_name=VN_C('update_source'))
    created_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('created_by'))
    last_updated_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('last_updated_by'))
    delete_flag = models.CharField(max_length=1, blank=True, null=True, default='N', editable=True, verbose_name=VN_C('delete_flag'))
    third_party_source = models.CharField(max_length=30, blank=True, null=True, default='THIS', verbose_name=VN_C('third_party_source'))
    third_party_source_ref = models.CharField(max_length=50, blank=True, null=True, default=-1, verbose_name=VN_C('third_party_source_ref'))
    #tenant_id = models.IntegerField(blank=False, null=False,default=-1)
    orderid = models.ForeignKey(EcommOrderinfo, models.DO_NOTHING, blank=True,
                                        null=True, to_field='orderid', db_column='orderid', verbose_name=VN_C('orderid'))

    class Meta:
        managed = False
        db_table = 'ecomm_orderaddress'
        verbose_name=VN_T('ecomm_orderaddress')

    def __str__(self):
        return str(self.orderaddressid)


class EcommOrderdetailsinfo(models.Model):
    tax_rate = models.DecimalField(max_digits=7, decimal_places=3,blank=True, null=True, verbose_name=VN_C('tax_rate'))
    item_id = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('item_id'))
    bom_id = models.IntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('bom_id'))
    record_status = models.CharField(max_length=1, blank=True, null=True, default='I', editable=True, verbose_name=VN_C('record_status'))
    last_update_date = models.DateTimeField(auto_now=True, blank=True, null=True, editable=True, verbose_name=VN_C('last_update_date'))
    creation_date = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=True, verbose_name=VN_C('creation_date'))
    bu_id = models.IntegerField(blank=True, null=True, default=1, editable=True, verbose_name=VN_C('bu_id'))
    update_source = models.CharField(max_length=30, blank=True, null=True, default='API', editable=True, verbose_name=VN_C('update_source'))
    created_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('created_by'))
    last_updated_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('last_updated_by'))
    delete_flag = models.CharField(max_length=1, blank=True, null=True, default='N', editable=True, verbose_name=VN_C('delete_flag'))
    third_party_source = models.CharField(max_length=30, blank=True, null=True, default='THIS', verbose_name=VN_C('third_party_source'))
    third_party_source_ref = models.CharField(max_length=50, blank=True, null=True, default=-1, verbose_name=VN_C('third_party_source_ref'))
    orderdetailsinfoid = models.BigIntegerField(blank=False, null=False, editable=True, primary_key=True,  verbose_name=VN_C('orderdetailsinfoid'))
    orderid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('orderid'))
    serialno = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('serialno'))
    kitid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('kitid'))
    kitname = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('kitname'))
    kitimageurl = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('kitimageurl'))
    kitbaseprice = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('kitbaseprice'))
    kitqtytype = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('kitqtytype'))
    kitqtystep = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('kitqtystep'))
    kitsubtotal = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('kitsubtotal'))
    kittaxamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('kittaxamount'))
    productid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('productid'))
    productname = models.CharField(max_length=200, blank=True, null=True, verbose_name=VN_C('productname'))
    productimageurl = models.CharField(max_length=200, blank=True, null=True, verbose_name=VN_C('productimageurl'))
    productbaseprice = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('productbaseprice'))
    productqtytype = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('productqtytype'))
    productqtystep = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('productqtystep'))
    productsubtotal = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('productsubtotal'))
    producttaxamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('producttaxamount'))
    attribute1 = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('attribute1'))
    attribute2 = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('attribute2'))
    attribute3 = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('attribute3'))
    attribute4 = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('attribute4'))
    status = models.IntegerField(blank=True, null=True, default=1, verbose_name=VN_C('status'))
    row_version = models.IntegerField(blank=True, null=True, verbose_name=VN_C('row_version'))
    tax_code_id = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('tax_code_id'))
    kitfinalamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('kitfinalamount'))
    kitoffertext = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('kitoffertext'))
    kitpromotionid = models.BigIntegerField(blank=True, null=True, editable=False, verbose_name=VN_C('kitpromotionid'))
    kitpromotiondetails = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('kitpromotiondetails'))
    kitdeliverytype = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('kitdeliverytype'))
    offerkitid = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, editable=False, verbose_name=VN_C('offerkitid'))
    offerkitquantity = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('offerkitquantity'))
    offerkitname = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('offerkitname'))
    offerkitimageurl = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('offerkitimageurl'))
    sku = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('sku'))
    productdiscount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('productdiscount'))
    productfinalamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('productfinalamount'))
    productoffertext = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('productoffertext'))
    productpromotionid = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, editable=False, verbose_name=VN_C('productpromotionid'))
    productpromotiondetails = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('productpromotiondetails'))
    productvariantid = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, editable=False, verbose_name=VN_C('productvariantid'))
    productvariantamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('productvariantamount'))
    productvariantquantity = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('productvariantquantity'))
    variantdetails = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('variantdetails'))
    uomdetails = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('uomdetails'))
    productdeliverytype = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('productdeliverytype'))
    offerproductid = models.BigIntegerField(blank=True, null=True, editable=False, verbose_name=VN_C('offerproductid'))
    offerproductvariantid = models.BigIntegerField(blank=True, null=True, editable=False, verbose_name=VN_C('offerproductvariantid'))
    offerproductquantity = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('offerproductquantity'))
    offerproductname = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('offerproductname'))
    offerproductimageurl = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('offerproductimageurl'))
    packagingstatus = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('packagingstatus'))
    packingstoreid = models.BigIntegerField(blank=True, null=True, editable=False, verbose_name=VN_C('packingstoreid'))
    packingassignedto = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('packingassignedto'))
    packedon = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('packedon'))
    packingverifiedby = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('packingverifiedby'))
    packingverifiedon = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('packingverifiedon'))
    deliverystatus = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('deliverystatus'))
    deliverassignedto = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('deliverassignedto'))
    deliveredon = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('deliveredon'))
    deliveryverifiedby = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('deliveryverifiedby'))
    deliveryverifiedon = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('deliveryverifiedon'))
    refunditeminitiated = models.IntegerField(blank=True, null=True, verbose_name=VN_C('refunditeminitiated'))
    refunditeminitiateddate = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('refunditeminitiateddate'))
    refunditemreceived = models.IntegerField(blank=True, null=True, verbose_name=VN_C('refunditemreceived'))
    refunditemreceiveddate = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('refunditemreceiveddate'))
    refundapproved = models.IntegerField(blank=True, null=True, verbose_name=VN_C('refundapproved'))
    refundapproveddate = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('refundapproveddate'))
    refundapprovedby = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('refundapprovedby'))
    refundamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('refundamount'))
    kitdiscount = models.DecimalField(max_digits=20, decimal_places=3, blank=True, null=True,
                                      verbose_name=VN_C('Kit Discount'))
    kitpromotionid = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('Kit Promotion Id'))
    offerkitid = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('Offer Kit Id '))
    productpromotionid = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('Product Promotion Id '))
    productvariantid = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('Product Variant Id'))
    offerproductid = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('Offer Product Id '))
    offerproductvariantid = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('Offer Product Variant ID'))
    packingstoreid = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('Picking Store ID'))
    returncustomernotes = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('Return Customer Notes'))
    returnimage = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('Return Image'))
    taxdetail = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('Tax Detail'))
    #tenant_id = models.IntegerField(blank=False, null=False,default=-1)
    orderid = models.ForeignKey(EcommOrderinfo, models.DO_NOTHING, blank=True,
                                        null=True, to_field='orderid', db_column='orderid', verbose_name=VN_C('orderid'))


    class Meta:
        managed = False
        db_table = 'ecomm_orderdetailsinfo'
        verbose_name=VN_T('ecomm_orderdetailsinfo')

    def __str__(self):
        return str(self.orderdetailsinfoid)


class EcommOrderkitproducts(models.Model):
    orderkitproductsid = models.BigIntegerField(blank=False, null=False, editable=True, primary_key=True, verbose_name=VN_C('orderkitproductsid'))
    kitid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('kitid'))
    productid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('productid'))
    productname = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('productname'))
    productimageurl = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('productimageurl'))
    productprice = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('productprice'))
    productqtytype = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('productqtytype'))
    productqtystep = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('productqtystep'))
    sku = models.CharField(max_length=50, blank=True, null=True, verbose_name=VN_C('sku'))
    productvariantid = models.BigIntegerField(blank=True, null=True, editable=True,
                                               verbose_name=VN_C('productvariantid'))
    productvariantamount = models.DecimalField(max_digits=20, decimal_places=3, blank=True, null=True,
                                                verbose_name=VN_C('productvariantamount'))
    productvariantquantity = models.DecimalField(max_digits=12, decimal_places=3, blank=True, null=True,
                                                  verbose_name=VN_C('productvariantquantity'))
    variantdetails = models.CharField(max_length=4000, blank=True, null=True, verbose_name=VN_C('variantdetails'))
    uomdetails = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('uomdetails'))
    attribute1 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute1'))
    attribute2 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute2'))
    attribute3 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute3'))
    attribute4 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute4'))
    status = models.IntegerField(blank=True, null=True, default=1, verbose_name=VN_C('status'))
    row_version = models.IntegerField(blank=True, null=True, verbose_name=VN_C('row_version'))
    item_id = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('item_id'))
    bom_id = models.IntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('bom_id'))
    record_status = models.CharField(max_length=1, blank=True, null=True, default='I', editable=True, verbose_name=VN_C('record_status'))
    last_update_date = models.DateTimeField(auto_now=True, blank=True, null=True, editable=True, verbose_name=VN_C('last_update_date'))
    creation_date = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=True, verbose_name=VN_C('creation_date'))
    bu_id = models.IntegerField(blank=True, null=True, default=1, editable=True, verbose_name=VN_C('bu_id'))
    update_source = models.CharField(max_length=30, blank=True, null=True, default='API', editable=True, verbose_name=VN_C('update_source'))
    created_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('created_by'))
    last_updated_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('last_updated_by'))
    delete_flag = models.CharField(max_length=1, blank=True, null=True, default='N', editable=True, verbose_name=VN_C('delete_flag'))
    third_party_source = models.CharField(max_length=30, blank=True, null=True, default='THIS', verbose_name=VN_C('third_party_source'))
    third_party_source_ref = models.CharField(max_length=50, blank=True, null=True, default=-1, verbose_name=VN_C('third_party_source_ref'))
    #tenant_id = models.IntegerField(blank=False, null=False,default=-1)
    orderid = models.ForeignKey(EcommOrderinfo, models.DO_NOTHING, blank=True,
                                        null=True, to_field='orderid', db_column='orderid', verbose_name=VN_C('orderid'))


    class Meta:
        managed = False
        db_table = 'ecomm_orderkitproducts'
        verbose_name=VN_T('ecomm_orderkitproducts')

    def __str__(self):
        return str(self.orderkitproductsid)


class EcommOrderpaymentinfo(models.Model):
    paymentrefid = models.CharField(max_length=100,blank=True,null=True, editable=True, verbose_name=VN_C('paymentrefid'))
    paymentamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('paymentamount'))
    paymentcurrencyid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('paymentcurrencyid'))
    paymentcurrency = models.CharField(max_length=10, blank=True, null=True, verbose_name=VN_C('paymentcurrency'))
    refundrefid = models.CharField(max_length=100, blank=True, null=True, editable=True, verbose_name=VN_C('refundrefid'))
    refundamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('refundamount'))
    refundcurrencyid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('refundcurrencyid'))
    refundcurrency = models.CharField(max_length=10, blank=True, null=True, verbose_name=VN_C('refundcurrency'))
    pointsredeemed = models.DecimalField(max_digits=20, decimal_places=0,blank=True, null=True, verbose_name=VN_C('pointsredeemed'))
    redeemedamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('redeemedamount'))
    loyaltytransid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('loyaltytransid'))
    loyaltycardno = models.CharField(max_length=100, blank=True, null=True, editable=True, verbose_name=VN_C('loyaltycardno'))
    receivedcash  = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('receivedcash'))
    attribute1 = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('attribute1'))
    attribute2 = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('attribute2'))
    attribute3 = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('attribute3'))
    attribute4 = models.CharField(max_length=400, blank=True, null=True, verbose_name=VN_C('attribute4'))
    status = models.IntegerField(blank=True, null=True, default=1, verbose_name=VN_C('status'))
    row_version = models.IntegerField(blank=True, null=True, verbose_name=VN_C('row_version'))
    record_status = models.CharField(max_length=1, blank=True, null=True, default='I', editable=True, verbose_name=VN_C('record_status'))
    last_update_date = models.DateTimeField(auto_now=True, blank=True, null=True, editable=True, verbose_name=VN_C('last_update_date'))
    creation_date = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=True, verbose_name=VN_C('creation_date'))
    bu_id = models.IntegerField(blank=True, null=True, default=1, editable=True, verbose_name=VN_C('bu_id'))
    update_source = models.CharField(max_length=30, blank=True, null=True, default='API', editable=True, verbose_name=VN_C('update_source'))
    created_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('created_by'))
    last_updated_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('last_updated_by'))
    delete_flag = models.CharField(max_length=1, blank=True, null=True, default='N', editable=True, verbose_name=VN_C('delete_flag'))
    third_party_source = models.CharField(max_length=30, blank=True, null=True, default='THIS', verbose_name=VN_C('third_party_source'))
    third_party_source_ref = models.CharField(max_length=50, blank=True, null=True, default=-1, verbose_name=VN_C('third_party_source_ref'))
    orderpaymentinfoid = models.BigIntegerField(blank=False, null=False, editable=True, primary_key=True,verbose_name=VN_C('orderpaymentinfoid'))
    paymentmethod = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('paymentmethod'))
    orderrefid = models.CharField(max_length=100, blank=True, null=True, editable=True, verbose_name=VN_C('orderrefid'))
    orderamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('orderamount'))
    servicecharges = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('servicecharges'))
    paymentcurrencyname = models.CharField(max_length=30, blank=True, null=True, default='THIS', verbose_name=VN_C('payment currency name'))
    refundcurrencyname	 = models.CharField(max_length=30, blank=True, null=True, default='THIS', verbose_name=VN_C('refund currency name'))
    loyaltypointsredeemed	= models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('loyalty points redeemed'))
    loyaltyredeemedamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('loyalty redeemed amount'))
    loyaltytransid	= models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('loyalt trans id'))
    loyaltyconversionrate	= models.DecimalField(max_digits=20, decimal_places=6,blank=True, null=True, verbose_name=VN_C('loyalty conversion rate'))
    refundloyaltypoints	= models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('refund loyalty points'))
    refundloyaltyamount	= models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('refund loyalty amount'))
    refundloyaltytransid	= models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('refund loyalty trans id'))
    customervoucherid	= models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('customer voucher id'))
    voucherno	= models.CharField(max_length=30, blank=True, null=True, default='THIS', verbose_name=VN_C('voucher no'))
    voucheramount	= models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('voucher amount'))
    refundvoucher	= models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('refund voucher'))
    refundvoucherid	= models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('refund voucher id'))
    refundvoucheramount	= models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('refund voucher amount'))
    #tenant_id = models.IntegerField(blank=False, null=False,default=-1)
    orderid = models.ForeignKey(EcommOrderinfo, models.DO_NOTHING, blank=True,
                                        null=True, to_field='orderid', db_column='orderid', verbose_name=VN_C('orderid'))

    class Meta:
        managed = False
        db_table = 'ecomm_orderpaymentinfo'
        verbose_name=VN_T('ecomm_orderpaymentinfo')

    def __str__(self):
        return str(self.orderpaymentinfoid)



class EcommOrdervariants(models.Model):
    ordervariantsid = models.BigIntegerField(blank=False, null=False, editable=True, primary_key=True,  verbose_name=VN_C('ordervariantsid'))
    orderdetailsinfoid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('orderdetailsinfoid'))
    productid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('productid'))
    serialno = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('serialno'))
    variantid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('variantid'))
    variantamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('variantamount'))
    taxamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('taxamount'))
    packagingstatus = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('packagingstatus'))
    packingstoreid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('packingstoreid'))
    packingassignedto = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('packingassignedto'))
    packedon = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('packedon'))
    packingverifiedby = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('packingverifiedby'))
    packingverifiedon = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('packingverifiedon'))
    deliverystatus = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('deliverystatus'))
    deliverassignedto = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('deliverassignedto'))
    deliveredon = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('deliveredon'))
    deliveryverifiedby = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('deliveryverifiedby'))
    deliveryverifiedon = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('deliveryverifiedon'))
    refunditeminitiated = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('refunditeminitiated'))
    refunditeminitiateddate = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('refunditeminitiateddate'))
    refunditemreceived = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('refunditemreceived'))
    refunditemreceiveddate = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('refunditemreceiveddate'))
    refundapproved = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('refundapproved'))
    refundapproveddate = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('refundapproveddate'))
    refundapprovedby = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('refundapprovedby'))
    refundamount = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True, verbose_name=VN_C('refundamount'))
    variantdetails = models.CharField(max_length=2000, blank=True, null=True, verbose_name=VN_C('variantdetails'))
    uomdetails = models.CharField(max_length=2000, blank=True, null=True, verbose_name=VN_C('uomdetails'))
    attribute1 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute1'))
    attribute2 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute2'))
    attribute3 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute3'))
    attribute4 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute4'))
    status = models.IntegerField(blank=True, null=True, default=1, verbose_name=VN_C('status'))
    row_version = models.IntegerField(blank=True, null=True, verbose_name=VN_C('row_version'))
    item_id = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('item_id'))
    bom_id = models.IntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('bom_id'))
    variant_id = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('variant_id'))
    record_status = models.CharField(max_length=1, blank=True, null=True, default='I', editable=True, verbose_name=VN_C('record_status'))
    last_update_date = models.DateTimeField(auto_now=True, blank=True, null=True, editable=True, verbose_name=VN_C('last_update_date'))
    creation_date = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=True, verbose_name=VN_C('creation_date'))
    bu_id = models.IntegerField(blank=True, null=True, default=1, editable=True, verbose_name=VN_C('bu_id'))
    update_source = models.CharField(max_length=30, blank=True, null=True, default='API', editable=True, verbose_name=VN_C('update_source'))
    created_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('created_by'))
    last_updated_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('last_updated_by'))
    delete_flag = models.CharField(max_length=1, blank=True, null=True, default='N', editable=True, verbose_name=VN_C('delete_flag'))
    third_party_source = models.CharField(max_length=30, blank=True, null=True, default='THIS', verbose_name=VN_C('third_party_source'))
    third_party_source_ref = models.CharField(max_length=50, blank=True, null=True, default=-1, verbose_name=VN_C('third_party_source_ref'))
    #tenant_id = models.IntegerField(blank=False, null=False,default=-1)
    orderid = models.ForeignKey(EcommOrderinfo, models.DO_NOTHING, blank=True,
                                        null=True, to_field='orderid', db_column='orderid', verbose_name=VN_C('orderid'))


    class Meta:
        managed = False
        db_table = 'ecomm_ordervariants'
        verbose_name=VN_T('ecomm_ordervariants')

    def __str__(self):
        return str(self.ordervariantsid)


class EcommOrderstatusupdatehistory(models.Model):
    attribute1 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute1'))
    attribute2 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute2'))
    attribute3 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute3'))
    attribute4 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute4'))
    status = models.IntegerField(blank=True, null=True, default=1, verbose_name=VN_C('status'))
    row_version = models.IntegerField(blank=True, null=True, verbose_name=VN_C('row_version'))
    record_status = models.CharField(max_length=1, blank=True, null=True, default='I', editable=False, verbose_name=VN_C('record_status'))
    last_update_date = models.DateTimeField(auto_now=True, blank=True, null=True, editable=False, verbose_name=VN_C('last_update_date'))
    creation_date = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False, verbose_name=VN_C('creation_date'))
    bu_id = models.IntegerField(blank=True, null=True, default=1, editable=False, verbose_name=VN_C('bu_id'))
    update_source = models.CharField(max_length=30, blank=True, null=True, default='API', editable=False, verbose_name=VN_C('update_source'))
    created_by = models.IntegerField(blank=True, null=True, default=-1, editable=False, verbose_name=VN_C('created_by'))
    last_updated_by = models.IntegerField(blank=True, null=True, default=-1, editable=False, verbose_name=VN_C('last_updated_by'))
    delete_flag = models.CharField(max_length=1, blank=True, null=True, default='N', editable=False, verbose_name=VN_C('delete_flag'))
    third_party_source = models.CharField(max_length=30, blank=True, null=True, default='THIS', verbose_name=VN_C('third_party_source'))
    third_party_source_ref = models.CharField(max_length=50, blank=True, null=True, default=-1, verbose_name=VN_C('third_party_source_ref'))
    #tenant_id = models.IntegerField(blank=False, null=False,default=-1)
    orderstatusupdatehistoryid = models.BigAutoField(blank=False, null=False, editable=False, verbose_name=VN_C('orderstatusupdatehistoryid'), primary_key=True)
    orderid = models.ForeignKey(EcommOrderinfo, models.DO_NOTHING, blank=True, null=True, to_field='orderid', db_column='orderid')

    class Meta:
        managed = False
        db_table = 'ecomm_orderstatusupdatehistory'
        verbose_name=VN_T('ecomm_orderstatusupdatehistory')

    def __str__(self):
        return str(self.ORDERSTATUSUPDATEHISTORYID)

class EcommVouchers(models.Model):
    customerid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('customerid'))
    voucherno = models.CharField(max_length=50, blank=True, null=True, verbose_name=VN_C('voucherno'))
    vouchergeneratedon = models.DateTimeField(blank=True, null=True, verbose_name=VN_C('vouchergeneratedon'))
    voucherstatus = models.IntegerField(blank=True, null=True, verbose_name=VN_C('voucherstatus'))
    vouchersource = models.CharField(max_length=30, blank=True, null=True, verbose_name=VN_C('vouchersource'))
    sourcecustomervoucherid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('sourcecustomervoucherid'))
    vouchergiftfromcustomerid = models.BigIntegerField(blank=True, null=True, editable=True, verbose_name=VN_C('vouchergiftfromcustomerid'))
    voucheramount = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('voucheramount'))
    redeemedpoints = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('redeemedpoints'))
    conversionrate = models.BigIntegerField(blank=True, null=True, verbose_name=VN_C('conversionrate'))
    attribute1 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute1'))
    attribute2 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute2'))
    attribute3 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute3'))
    attribute4 = models.CharField(max_length=100, blank=True, null=True, verbose_name=VN_C('attribute4'))
    status = models.IntegerField(blank=True, null=True, default=1, verbose_name=VN_C('status'))
    row_version = models.IntegerField(blank=True, null=True, verbose_name=VN_C('row_version'))
    record_status = models.CharField(max_length=1, blank=True, null=True, default='I', editable=False, verbose_name=VN_C('record_status'))
    last_update_date = models.DateTimeField(auto_now=True, blank=True, null=True, editable=False, verbose_name=VN_C('last_update_date'))
    creation_date = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False, verbose_name=VN_C('creation_date'))
    bu_id = models.IntegerField(blank=True, null=True, default=1, editable=False, verbose_name=VN_C('bu_id'))
    update_source = models.CharField(max_length=30, blank=True, null=True, default='API', editable=False, verbose_name=VN_C('update_source'))
    created_by = models.IntegerField(blank=True, null=True, default=-1, editable=False, verbose_name=VN_C('created_by'))
    last_updated_by = models.IntegerField(blank=True, null=True, default=-1, editable=False, verbose_name=VN_C('last_updated_by'))
    delete_flag = models.CharField(max_length=1, blank=True, null=True, default='N', editable=False, verbose_name=VN_C('delete_flag'))
    third_party_source = models.CharField(max_length=30, blank=True, null=True, default='THIS', verbose_name=VN_C('third_party_source'))
    third_party_source_ref = models.CharField(max_length=50, blank=True, null=True, default=-1, verbose_name=VN_C('third_party_source_ref'))
    #tenant_id = models.IntegerField(blank=False, null=False,default=-1)
    customervoucherid = models.BigAutoField(blank=False, null=False, editable=True, verbose_name=VN_C('customervoucherid'), primary_key=True)

    class Meta:
        managed = False
        db_table = 'ecomm_vouchers'
        verbose_name=VN_T('ecomm_vouchers')

    def __str__(self):
        return str(self.CUSTOMERVOUCHERID)


class TpStocks(models.Model):
    tp_stock_id = models.BigIntegerField(blank=True, null=True, editable=False, primary_key=True, verbose_name=VN_C('ID'))
    status = models.CharField(max_length=30, blank=True, null=True, verbose_name=VN_C('status'))
    productGUID = models.CharField(max_length=100, blank=True, null=True, db_column='productguid', verbose_name=VN_C('product guid'))
    storeGUID = models.CharField(max_length=100, blank=True, null=True,db_column='storeguid', verbose_name=VN_C('store guid'))
    productName = models.CharField(max_length=150, blank=True, null=True,db_column='productname', verbose_name=VN_C('product name'))
    storeName = models.CharField(max_length=150, blank=True, null=True, db_column='storename',verbose_name=VN_C('store name'))
    internalReferenceCode = models.CharField(max_length=150, blank=True,db_column='internalreferencecode', null=True, verbose_name=VN_C('internal reference'))
    integrationValue = models.BigIntegerField(blank=True,db_column='integrationvalue', null=True, verbose_name=VN_C('Location Id'))
    quantity = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True,  editable=True, verbose_name=VN_C('quantity'))
    lastUpdatedDate = models.DateTimeField(auto_now=True, blank=True, null=True, editable=True,db_column='lastupdateddate', verbose_name=VN_C('last_update_date'))
    record_status = models.CharField(max_length=1, blank=True, null=True, default='I', editable=True, verbose_name=VN_C('record_status'))
    last_update_date = models.DateTimeField(auto_now=True, blank=True, null=True, editable=True, verbose_name=VN_C('last_update_date'))
    creation_date = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=True, verbose_name=VN_C('creation_date'))
    bu_id = models.IntegerField(blank=True, null=True, default=1, editable=True, verbose_name=VN_C('bu_id'))
    update_source = models.CharField(max_length=30, blank=True, null=True, default='API', editable=True, verbose_name=VN_C('update_source'))
    created_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('created_by'))
    last_updated_by = models.IntegerField(blank=True, null=True, default=-1, editable=True, verbose_name=VN_C('last_updated_by'))
    delete_flag = models.CharField(max_length=1, blank=True, null=True, default='N', editable=True, verbose_name=VN_C('delete_flag'))
    third_party_source = models.CharField(max_length=30, blank=True, null=True, default='THIS', verbose_name=VN_C('third_party_source'))
    third_party_source_ref = models.CharField(max_length=50, blank=True, null=True, default=-1, verbose_name=VN_C('third_party_source_ref'))
    #tenant_id = models.IntegerField(blank=False, null=False,default=-1)

    class Meta:
        managed = False
        db_table = 'tp_stocks'
        verbose_name=VN_T('tp_stocks')

    def __str__(self):
        return str(self.tp_stock_id)

class WwwStockPercent(models.Model):
    delivery = models.CharField(max_length=1, blank=True, null=True, verbose_name=VN_C('delivery'))
    in_store = models.CharField(max_length=1, blank=True, null=True, verbose_name=VN_C('in_store'))
    click_and_collect = models.CharField(max_length=1, blank=True, null=True, verbose_name=VN_C('click_and_collect'))
    record_status = models.CharField(max_length=10, blank=True, null=True, default='I', editable=False, verbose_name=VN_C('record_status'))
    update_source = models.CharField(max_length=30, blank=True, null=True, default='API', editable=False, verbose_name=VN_C('update_source'))
    delete_flag = models.CharField(max_length=1, blank=True, null=True, default='N', editable=False, verbose_name=VN_C('delete_flag'))
    bu_id = models.IntegerField(blank=True, null=True, default=1, editable=False, verbose_name=VN_C('bu_id'))
    created_by = models.BigIntegerField(blank=True, null=True, default=-1, editable=False, verbose_name=VN_C('created_by'))
    creation_date = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False, verbose_name=VN_C('creation_date'))
    last_updated_by = models.BigIntegerField(blank=True, null=True, default=-1, editable=False, verbose_name=VN_C('last_updated_by'))
    last_update_date = models.DateTimeField(auto_now=True, blank=True, null=True, editable=False, verbose_name=VN_C('last_update_date'))
    stock_percent = models.DecimalField(max_digits=4, decimal_places=3,blank=True, null=True, default=.80, verbose_name=VN_C('stock_percent'))
    third_party_source = models.CharField(max_length=30, blank=True, null=True, default='THIS', verbose_name=VN_C('third_party_source'))
    third_party_source_ref = models.CharField(max_length=50, blank=True, null=True, default=-1, verbose_name=VN_C('third_party_source_ref'))
    #tenant_id = models.IntegerField(blank=False, null=False,default=-1)
    #category_id = models.ForeignKey(InvItemCategories, models.DO_NOTHING, blank=True, null=True, to_field='category_id', db_column='category_id')
    #sub_category_id = models.ForeignKey(InvItemSubCategories, models.DO_NOTHING, blank=True, null=True, to_field='sub_category_id', db_column='sub_category_id')
    #item_id = models.ForeignKey(InvItemMasters, models.DO_NOTHING, blank=True, null=True, to_field='item_id', db_column='item_id')
    #location_id = models.ForeignKey(InvLocations, models.DO_NOTHING, blank=True, null=True, to_field='location_id', db_column='location_id')
    category_id = models.BigIntegerField(blank=True, null=True,  editable=True, verbose_name=VN_C('category_id'))
    sub_category_id = models.BigIntegerField(blank=True, null=True,  editable=True, verbose_name=VN_C('sub_category_id'))
    item_id = models.BigIntegerField(blank=True, null=True,  editable=True, verbose_name=VN_C('item_id'))
    location_id = models.BigIntegerField(blank=True, null=True,  editable=True, verbose_name=VN_C('location_id'))
    www_stock_percent_id = models.BigIntegerField(blank=False, null=False, primary_key=True, editable=False, verbose_name=VN_C('ID'))

    class Meta:
        managed = False
        db_table = 'www_stock_percent'
        verbose_name=VN_T('www_stock_percent')

    def __str__(self):
        return str(self.www_stock_percent_id)