from __future__ import unicode_literals
from django.conf.urls import include, url
from django.urls import path, re_path
from restapi.views import *
app_name = 'restapi'


urlpatterns = [
    url(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
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
    url(r"^itembatch/$",RESTItemBatchList.as_view(),name="item_batch"),
    url(r"^itembatch/(?P<pk>[0-9]+)/$", RESTItemBatchDetail.as_view(),name="itembatch_detail"),
]

