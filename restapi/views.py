#-+- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import  Group
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from common.models import (CmnUsers, InvItemCategories, InvItemSubCategories, InvItemMasters, CmnBusinessSectors,
                            InvItemSalesUnits,InvItemBarcodes,
                           CmnUnitOfMeasurements, CmnTaxCodes, ArCustomerProfiles, ArCustomers)
from common.submodels import(imp_models, ecomm_models)
from rest_framework import (viewsets, permissions, generics)
from rest_framework.generics import (CreateAPIView, ListAPIView, UpdateAPIView, DestroyAPIView)
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from restapi.serializers import *

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
    for key,value in p_params:
        if p_allowedparams != []:
            if key in p_allowedparams:
                inputparams[key] = value
        else:
            inputparams[key] = value
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
    queryset = model.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination
    ordering = ('category_name',)
    def get(self, request, *args, **kwargs):
        self.inputparams = process_params(p_params=self.request.GET.items(),p_allowedparams=['category_id','category_name'])
        if self.inputparams != {}:
            self.queryset = self.model.objects.filter(**self.inputparams)
        return self.list(request, *args, **kwargs)

class RESTCategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = InvItemCategories.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination

class RESTSubcategoryList(generics.ListCreateAPIView):
    queryset = InvItemSubCategories.objects.all()
    print('going to Sub cat serializer')
    serializer_class = SubCategorySerializer
    pagination_class = StandardResultsSetPagination

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
    queryset = InvItemMasters.objects.all()
    serializer_class = ItemSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['item_number','item_name','last_update_date','last_update_date__gt','last_update_date__lt'
                ,'item_name__startswith']


class RESTItemList(generics.ListCreateAPIView):
    lookup_field = 'item_number'
    queryset = InvItemMasters.objects.none()
    serializer_class = ItemSerializer
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'item_name' in key or 'item_number' in key or 'last_update_date' in key:
                self.inputparams[key] = value
        if self.inputparams != {}:
            self.queryset = InvItemMasters.objects.filter(**self.inputparams)
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
    pagination_class = StandardResultsSetPagination
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if 'format' not in key and 'page' not in key:
                self.inputparams[key] = value
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

