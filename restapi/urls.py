from __future__ import unicode_literals
from django.conf.urls import include, url
from django.urls import path, re_path
from restapi.views import *
app_name = 'restapi'


urlpatterns = [
    #url(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    url(r"^subcategory/$",RESTSubcategoryList.as_view(),name="subcategory"),
    url(r"^subcategory/(?P<pk>[0-9]+)/$", RESTSubcategoryDetail.as_view(),name="subcategory_detail"),
    url(r"^listbs/$", ListBsAPIView.as_view(),name="listbs"),
    path("createbs/",CreateBsAPIView.as_view(),name="bs_create"),
    path("updatebs/<int:pk>/",UpdateBsAPIView.as_view(),name="update_bs"),
    path("deletebs/<int:pk>/",DeleteBsAPIView.as_view(),name="delete_bs"),
    url(r"^category/$",RESTCategoryList.as_view(),name="category"),
    url(r"^category/(?P<pk>[0-9]+)/$", RESTCategoryDetail.as_view(),name="category_detail"),
    url(r"^item/$",RESTItemList.as_view(),name="item"),
    url(r"^item/(?P<pk>[0-9]+)/$", RESTItemDetail.as_view(),name="item_detail"),
    path("itemsearch/<str:item_number>/", RESTItemDetail.as_view(),name="item_search"),
    url(r"^itembatchline/$",RESTItemBatchLines.as_view(),name="item_batch_lines"),
    url(r"^itembatch/$",RESTItemBatchList.as_view(),name="item_batch"),
    url(r"^itembatch/(?P<pk>[0-9]+)/$", RESTItemBatchDetail.as_view(),name="itembatch_detail"),
    url(r"^salesunit/$", RESTSalesUnitList.as_view(),name="sales_unit_list"),
    url(r"^barcode/$", RESTBarcodeList.as_view(),name="barcode_list"),
    url(r"^salesunit/(?P<pk>[0-9]+)/$", RESTSalesUnitList.as_view(),name="sales_unit"),
    url(r"^uom/$", RESTUOMList.as_view(),name="uom_list"),
    url(r"^taxcode/$", RESTTaxCodesList.as_view(),name="taxcode_list"),
    url(r"^customer/$", RESTCustomersList.as_view(),name="customer_list"),
    url(r"^customer/(?P<pk>[0-9]+)/$", RESTCustomerDetail.as_view(),name="customer_detail"),
    url(r"^manf/$", RESTManfList.as_view(),name="manf_list"),
    url(r"^store/$", RESTStoreList.as_view(),name="store_list"),
    url(r"^locationstock/$", RESTLocationStockList.as_view(),name="locationstock_list"),
    url(r"^ecommorderinfo/$",RESTEcommOrderInfoCreate.as_view(),name="ecommorderinfo_list"),
    url(r"^ecommorderdetailinfo/$",RESTEcommOrderDetailInfoCreate.as_view(),name="ecommorderdetailinfo_list"),
    url(r"^ecommorderaddress/$",RESTEcommOrderAddressCreate.as_view(),name="ecommorderaddress_list"),
    url(r"^ecommorderpayment/$",RESTEcommOrderPaymentInfoCreate.as_view(),name="ecommorderpayment_list"),
    url(r"^ecommorderstatus/$",RESTEcommOrderStatusCreate.as_view(),name="ecommorderstatus_list"),
    url(r"^ecommorderstatushist/$",RESTEcommOrderStatusHistCreate.as_view(),name="ecommorderstatushist_list"),
    url(r"^ecommorderkit/$",RESTEcommOrderKitCreate.as_view(),name="ecommorderkit_list"),
    url(r"^itemofferline/$",RESTItemOfferLines.as_view(),name="item_offer_lines"),
    url(r"^loyaltycard/$",RESTCards.as_view(),name="cmn_cards"),
    url(r"^loyaltycardassignment/$",RESTCardAssignments.as_view(),name="cmn_card_assignments"),
    url(r"^loyaltycardtrans/$",RESTCardTrans.as_view(),name="cmn_card_trans"),
    url(r"^loyaltycardsummary/$",RESTCardLoyaltySummary.as_view(),name="cmn_loyalty_summary"),
    url(r"^ecommvouchers/$",RESTVouchers.as_view(),name="ecommvouchers_list"),
    url(r"^similaritems/$",RESTSimilarItems.as_view(),name="similar_items"),
    url(r"^kits/$",RESTBOM.as_view(),name="bom_items"),
    url(r"^ecommvoucher/(?P<pk>[0-9]+)/$", RESTVoucherDetail.as_view(),name="voucher_detail"),
    url(r"^tpstocks/$",RESTTpStocksCreate.as_view(),name="tpstocks_list"),
]

