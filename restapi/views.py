#-+- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import  Group
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from datetime import date, time, timedelta

from common.models import (CmnUsers, InvItemCategories, InvItemSubCategories, InvItemMasters, CmnBusinessSectors,
                            InvItemSalesUnits,InvItemBarcodes,
                           CmnUnitOfMeasurements, CmnTaxCodes, ArCustomerProfiles, ArCustomers)
from common.submodels import(imp_models, ecomm_models)
from rest_framework import (viewsets, permissions, generics)
from rest_framework.generics import (CreateAPIView, ListAPIView, UpdateAPIView, DestroyAPIView)
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from restapi.serializers import *


TARGET = ""
def init_target():
    global TARGET
    TARGET =""

def assign_target(p_key, p_value):
    global TARGET
    if p_key == 'target':
       TARGET = p_value



def get_target_filterbatch(p_filtercolumn:str = 'ITEM_ID', p_target:str = "", p_queryset = None):
    target_filter = ""
    print('target filter',TARGET)
    if len(p_target) > 0:
        target_filter  = """ {} in (SELECT x.item_id 
                                            FROM inv_item_batches y, inv_item_batch_lines x
                                            WHERE y.batch_id = x.batch_id 
                                            AND   y.batch_name = upper('#{}')
                                            ) """.format(p_filtercolumn, p_target)
    print('targetfilter',target_filter)
    if len(target_filter) > 0:
        return p_queryset.extra(where=[target_filter])
    return p_queryset


def get_target_filter(p_filtercolumn:str = 'ITEM_ID', p_target:str = "", p_queryset = None):
    target_filter = ""
    print('target filter',TARGET)
    if len(p_target) > 0:
        target_filter  = """ {} in (SELECT x.item_id 
                                            FROM  ar_cust_item_uploads x
                                            WHERE x.customer_id  in  ( SELECT y.customer_id 
                                                                        FROM ar_customers y
                                                                        WHERE y.customer_name = upper('{}')
                                                                     )
                                            AND   x.upload_item  = 'Y' 
                                            ) """.format(p_filtercolumn, p_target)
    print('targetfilter',target_filter)
    if len(target_filter) > 0:
        return p_queryset.extra(where=[target_filter])
    return p_queryset


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

def process_params(p_params, p_allowedparams = []):
    inputparams = {}
    try:
        for key,value in p_params:
            if p_allowedparams != []:
                for param in p_allowedparams:
                    if param in key:
                        inputparams[key] = value
            else:
                if key == 'target':
                    TARGET = value
                else:
                    inputparams[key] = value
    except Exception as ex:
        print('process params:',ex)
    finally:
        return inputparams

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = CmnUsers.objects.all().order_by('-creation_date')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class RESTCategoryList(generics.ListCreateAPIView):
    model = InvItemCategories
    queryset = model.objects.none()
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination
    ordering = ('category_name',)
    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        self.inputparams = process_params(p_params=self.request.GET.items(),p_allowedparams=['category_id','category_name','last_update_date'])
        print('categoryapi',self.inputparams)
        if self.inputparams != {}:
            self.queryset = self.model.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)

class RESTCategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    model = InvItemCategories
    queryset = model.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination

class RESTSubcategoryList(generics.ListCreateAPIView):
    model = InvItemSubCategories
    queryset = model.objects.none()
    print('going to Sub cat serializer')
    serializer_class = SubCategorySerializer
    pagination_class = StandardResultsSetPagination
    ordering = ('sub_category_name',)
    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        self.inputparams = process_params(p_params=self.request.GET.items(),p_allowedparams=['sub_category_id','sub_category_name','last_update_date'])
        if self.inputparams != {}:
            self.queryset = self.model.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)

class RESTSubcategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = InvItemSubCategories.objects.all()
    print('going to Sub cat serializer')
    serializer_class = SubCategorySerializer
    pagination_class = StandardResultsSetPagination

class ListBusinessSectorApiView(ListAPIView):
    """This endpoint list all of the available Business Sectors"""
    queryset = CmnBusinessSectors.objects.all()
    serializer_class = BusinessSectorSerializer
    pagination_class = StandardResultsSetPagination


class ListBsAPIView(ListAPIView):
    """This endpoint list all of the available Business Sectors"""
    queryset = CmnBusinessSectors.objects.all()
    serializer_class = BusinessSectorSerializer
    pagination_class = StandardResultsSetPagination

class CreateBsAPIView(CreateAPIView):
    """This endpoint allows for creation of a Business Sector"""
    queryset = CmnBusinessSectors.objects.all()
    serializer_class = BusinessSectorSerializer
    pagination_class = StandardResultsSetPagination

class UpdateBsAPIView(generics.RetrieveUpdateDestroyAPIView):
    """This endpoint allows for updating a specific Business Sectorby passing in the id of the todo to update"""
    queryset = CmnBusinessSectors.objects.all()
    serializer_class = BusinessSectorSerializer
    pagination_class = StandardResultsSetPagination

class DeleteBsAPIView(DestroyAPIView):
    """This endpoint allows for deletion of a specific Business Sector from the database"""
    queryset = CmnBusinessSectors.objects.all()
    serializer_class = BusinessSectorSerializer
    pagination_class = StandardResultsSetPagination

class ItemFilter(django_filters.FilterSet):
    class Meta:
        model = InvItemMasters
        fields = {'item_name': ['icontains'],
		          'item_number': ['exact'],
                  'last_update_date': ['gt','lt'],
                 }

class RESTItemList2(generics.ListCreateAPIView):
    #lookup_field = 'item_number'

    def get_queryset(self):
        queryset = InvItemMasters.objects.all()
        return queryset


    serializer_class = ItemSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['item_number','item_name','last_update_date','last_update_date__gt','last_update_date__lt'
                ,'item_name__startswith']


class RESTItemList(generics.ListCreateAPIView):
    lookup_field = 'item_number'
    serializer_class = ItemSerializer
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get_queryset_old(self):
        queryset = InvItemMasters.objects.none()
        return queryset

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        self.additional_where = ""
        init_target()
        for key,value in self.request.GET.items():
            if 'item_name' in key or 'item_number' in key or 'last_update_date' in key:
                self.inputparams[key] = value
            assign_target(key, value)
        if self.inputparams != {}:
            self.queryset = InvItemMasters.objects.filter(**self.inputparams)
            self.queryset = get_target_filter(p_target=TARGET,p_queryset=self.queryset)
        return self.list(request, *args, **kwargs)


class RESTSalesUnitList(generics.ListCreateAPIView):
    lookup_field = 'sales_unit'
    queryset = InvItemSalesUnits.objects.none()
    serializer_class = SalesUnitsSerializer
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'iim_item_id' in key or 'sales_unit' in key or 'last_update_date' in key:
                self.inputparams[key] = value
        if self.inputparams != {}:
            self.queryset = InvItemSalesUnits.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)


class RESTBarcodeList(generics.ListCreateAPIView):
    lookup_field = 'barcode'
    queryset = InvItemBarcodes.objects.none()
    serializer_class = BarcodesSerializer
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'iim_item_id' in key or 'iisu_su_id' in key\
                    or 'last_update_date' in key or 'barcode' in key:
                self.inputparams[key] = value
        if self.inputparams != {}:
            self.queryset = InvItemBarcodes.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)


class RESTItemDetail(generics.RetrieveUpdateDestroyAPIView):
    def get_serializer_context(self):
        context = super().get_serializer_context()
        print('context', context)
        return context

    def get(self, request, *args, **kwargs):
        for key,value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken':
                self.inputparams[key] = value
        print('params', self.inputparams)
        if self.inputparams != {}:
            self.queryset = InvItemMasters.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)

    queryset = InvItemMasters.objects.all()
    serializer_class = ItemSerializer
    pagination_class = StandardResultsSetPagination


class RESTItemBatchList(generics.ListCreateAPIView):
    lookup_field = 'batch_name'
    model = InvItemBatches
    queryset = model.objects.all()
    serializer_class = ItemBatchSerialized
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'batch_name' in key or 'name' in key or 'item_batch_category' in key:
                self.inputparams[key] = value
        self.queryset = self.model.objects.filter(**self.inputparams)
        print(self.queryset.query)
        return self.list(request, *args, **kwargs)

class RESTItemBatchDetail(generics.RetrieveUpdateDestroyAPIView):
    model = InvItemBatches
    inputparams = {}

    def get(self, request, *args, **kwargs):
        for key,value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken':
                self.inputparams[key] = value
        print('params', self.inputparams)
        if self.inputparams != {}:
            self.queryset = self.model.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)

    queryset = model.objects.all()
    serializer_class = ItemSerializer
    pagination_class = StandardResultsSetPagination


class RESTItemBatchLines(generics.ListCreateAPIView):
    lookup_field = 'item_id'
    model = InvItemBatchLines
    queryset = model.objects.all()
    serializer_class = ItemBatchLinesSerialized
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'batch_name' in key or 'name' in key or 'item_batch_category' in key:
                self.inputparams[key] = value
        self.queryset = self.model.objects.filter(**self.inputparams)
        print(self.queryset.query)
        return self.list(request, *args, **kwargs)


class RESTUOMList(generics.ListCreateAPIView):
    lookup_field = 'short_desc'
    queryset = CmnUnitOfMeasurements.objects.none()
    serializer_class = UOMSerialized
    pagination_class = StandardResultsSetPagination
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = CmnUnitOfMeasurements.objects.filter()
        return self.list(request, *args, **kwargs)

class RESTTaxCodesList(generics.ListCreateAPIView):
    lookup_field = 'tax_code'
    queryset = CmnTaxCodes.objects.all()
    serializer_class = TaxcCodesSerialized
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get1(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = CmnTaxCodes.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)


class RESTCustomersList(generics.ListCreateAPIView):
    lookup_field = 'customer_id'
    queryset = ArCustomers.objects.none()
    serializer_class = CustomersSerialized
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if key not in ['format','page']:
                self.inputparams[key] = value
        print('customer',self.inputparams)
        self.queryset = ArCustomers.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)


class RESTCustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ArCustomers.objects.all()
    serializer_class = CustomersSerialized
    pagination_class = StandardResultsSetPagination

class RESTManfList(generics.ListCreateAPIView):
    lookup_field = 'manf_id'
    queryset = InvManufacturers.objects.none()
    serializer_class = ManfSerialized
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = InvManufacturers.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)


class RESTStoreList(generics.ListCreateAPIView):
    lookup_field = 'location_id'
    queryset = InvLocations.objects.none()
    serializer_class = StoreSerialized
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = InvLocations.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)


class RESTLocationStockList(generics.ListCreateAPIView):
    lookup_field = 'location_id'
    queryset = InvItemLocations.objects.none()
    serializer_class = LocationStockSerialized
    pagination_class  = LargeResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        dayschanged = 2
        full = False
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'full' in key:
                full = True
            if 'days' in key:
                dayschanged = int(value)
            if 'format' not in key and 'page' not in key and 'full' not in key and 'days' not in key:
                self.inputparams[key] = value
        if not full:
            self.queryset = InvItemLocations.objects.filter(last_update_date__gt=date.today()-timedelta(days=dayschanged)).filter(**self.inputparams)
        else:
            self.queryset = InvItemLocations.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)



class RESTEcommOrderStatusCreate(generics.ListCreateAPIView):
    lookup_field = 'orderid'
    queryset = ecomm_models.EcommOrderstatusinfo.objects.none()
    serializer_class = EcommOrderStatInfoSerializer
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = ecomm_models.EcommOrderstatusinfo.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)



class RESTEcommOrderInfoCreate(generics.ListCreateAPIView):
    lookup_field = 'orderid'
    queryset = ecomm_models.EcommOrderinfo.objects.none()
    serializer_class = EcommOrderInfoSerializer
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = ecomm_models.EcommOrderinfo.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print('initial',serializer.initial_data)
        serializer.is_valid(raise_exception=True)
        print('validated',serializer.validated_data)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RESTEcommOrderDetailInfoCreate(generics.ListCreateAPIView):
    lookup_field = 'orderid'
    queryset = ecomm_models.EcommOrderdetailsinfo.objects.none()
    serializer_class = EcommOrderDetailInfoSerializer
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = ecomm_models.EcommOrderdetailsinfo.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)


class RESTEcommOrderAddressCreate(generics.ListCreateAPIView):
    lookup_field = 'orderid'
    queryset = ecomm_models.EcommOrderaddress.objects.none()
    serializer_class = EcommOrderAddressSerializer
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = ecomm_models.EcommOrderaddress.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)



class RESTEcommOrderPaymentInfoCreate(generics.ListCreateAPIView):
    lookup_field = 'orderid'
    queryset = ecomm_models.EcommOrderpaymentinfo.objects.none()
    serializer_class = EcommOrderPaymentInfoSerializer
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = ecomm_models.EcommOrderpaymentinfo.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)


class RESTEcommOrderKitCreate(generics.ListCreateAPIView):
    lookup_field = 'orderid'
    queryset = ecomm_models.EcommOrderkitproducts.objects.none()
    serializer_class = EcommOrderKitSerializer
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = ecomm_models.EcommOrderkitproducts.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)


class RESTEcommOrderStatusHistCreate(generics.ListCreateAPIView):
    lookup_field = 'orderid'
    queryset = ecomm_models.EcommOrderstatusupdatehistory.objects.none()
    serializer_class = EcommOrderStatHistSerializer
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = ecomm_models.EcommOrderstatusupdatehistory.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)

class RESTItemOfferLines(generics.ListCreateAPIView):
    lookup_field = 'offer_header_od'
    model = InvItemOfferLines
    queryset = model.objects.all()
    serializer_class = ItemOfferLinesSerialized
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = self.model.objects.filter(**self.inputparams)
        print(self.queryset.query)
        return self.list(request, *args, **kwargs)


class RESTCards(generics.ListCreateAPIView):
    lookup_field = 'card_number'
    model = CmnCards
    queryset = model.objects.all()
    serializer_class = CardsSerialized
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = self.model.objects.filter(**self.inputparams)
        print(self.queryset.query)
        return self.list(request, *args, **kwargs)


class RESTCardAssignments(generics.ListCreateAPIView):
    lookup_field = 'card_number'
    model = CmnCardAssignments
    queryset = model.objects.all()
    serializer_class = CardAssignmentsSerialized
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = self.model.objects.filter(**self.inputparams)
        print(self.queryset.query)
        return self.list(request, *args, **kwargs)


class RESTCardTrans(generics.ListCreateAPIView):
    lookup_field = 'trans_id'
    model = CmnCardTrans
    queryset = model.objects.all()
    serializer_class = CardTransSerialized
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = self.model.objects.filter(**self.inputparams)
        print(self.queryset.query)
        return self.list(request, *args, **kwargs)


class RESTCardLoyaltySummary(generics.ListCreateAPIView):
    lookup_field = 'trans_id'
    model = CmnLoyaltySummary
    queryset = model.objects.all()
    serializer_class = CardLoyaltySummaryialized
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = self.model.objects.filter(**self.inputparams)
        print(self.queryset.query)
        return self.list(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = self.model.objects.filter(**self.inputparams)
        print(self.queryset.query)
        return self.list(request, *args, **kwargs)


class RESTVouchers(generics.ListCreateAPIView):
    lookup_field = 'trans_id'
    model = ecomm_models.EcommVouchers
    queryset = model.objects.all()
    serializer_class = VoucherSerialized
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = self.model.objects.filter(**self.inputparams)
        print(self.queryset.query)
        return self.list(request, *args, **kwargs)


class RESTSimilarItems(generics.ListCreateAPIView):
    lookup_field = 'item_number'
    model = InvSimilarItems
    queryset = model.objects.all()
    serializer_class = SimilarItemsSerialized
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = self.model.objects.filter(**self.inputparams)
        print(self.queryset.query)
        return self.list(request, *args, **kwargs)


class RESTBOM(generics.ListCreateAPIView):
    lookup_field = 'level0_item_id'
    model = InvBom
    queryset = model.objects.all()
    serializer_class = BOMSerialized
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = self.model.objects.filter(**self.inputparams)
        print(self.queryset.query)
        return self.list(request, *args, **kwargs)


class RESTVoucherDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ecomm_models.EcommVouchers.objects.all()
    serializer_class = VoucherSerialized
    pagination_class = StandardResultsSetPagination


class RESTTpStocksCreate(generics.ListCreateAPIView):
    lookup_field = 'tp_stock_id'
    queryset = ecomm_models.TpStocks.objects.none()
    serializer_class = TpStockSerialized
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
        self.queryset = ecomm_models.TpStocks.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print('initial',serializer.initial_data)
        serializer.is_valid(raise_exception=True)
        print('validated',serializer.validated_data)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


