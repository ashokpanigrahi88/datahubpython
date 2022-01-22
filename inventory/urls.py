from django.conf.urls import url
from django.urls import path, re_path
from inventory.views import (category_views, location_views, barcoderep_views, item_search, manufacturer_views)
from inventory.templates.inventory_options import inventoryoptions_views
from inventory.templates.price_type import pricetypes_views
from inventory.templates.manf import manf_views

app_name = 'inventory'

urlpatterns = [
    re_path('^itemcategory/$', category_views.CategorylistView.as_view(), name='itemcategory'),
    path('itemsubcategory_delete/<int:sub_category_id>/', category_views.SubCategoryDeleteView.as_view(), name='itemsubcategory_delete'),
    path('itemcategory_delete/<int:category_id>/', category_views.CategoryDeleteView.as_view(), name='itemcategory_delete'),
    re_path('^locations/$',location_views.LocationlistView.as_view(), name='locations'),
    path('location_delete/<int:location_id>/',location_views.LocationDeleteView.as_view(), name='location_delete'),
    path('sublocation_delete/<int:sub_location_id>/', location_views.SubLocationDeleteView.as_view(), name='sublocation_delete'),
    re_path('^barcoderep/$',barcoderep_views.BarcoderepListView.as_view(), name='barcoderep'),
    path('barcoderep_delete/<int:repository_id>/',barcoderep_views.BarcoderepDeleteView.as_view(), name='barcoderep_delete'),
    path('options/', inventoryoptions_views.InventoryOptionsListView.as_view(), name='inventoryoptions_list'),
    path('options/create/', inventoryoptions_views.InventoryOptionsCreateView.as_view(),
         name='inventoryoptions_create'),
    path('options/update-<str:inv_options_id>/', inventoryoptions_views.InventoryOptionsUpdateView.as_view(),
         name='inventoryoptions_update'),
    re_path('itemsearch/$',item_search.SummaryView.as_view(), name='itemsearch'),
    ### PRICE TYPES
    path('pricetypes/', pricetypes_views.PriceTypeListView.as_view(), name='pricetype_list'),
    path('pricetype_create/', pricetypes_views.PriceTypeCreateView.as_view(), name='pricetype_create'),
    path('pricetype_update/<str:price_type_id>/', pricetypes_views.PriceTypeUpdateView.as_view(),
         name='pricetype_update'),
    path('pricetype_delete/<str:price_type_id>/', pricetypes_views.PriceTypeDeleteView.as_view(),
         name='pricetype_delete'),
    ### MANUFACTURER
    path('manf/', manf_views.ManfListView.as_view(), name='manf_list'),
    path('manf_create/', manf_views.ManfCreateView.as_view(), name='manf_create'),
    path('manf_update/<str:manf_id>/', manf_views.ManfUpdateView.as_view(),
         name='manf_update'),
    re_path('^manf1/$',manufacturer_views.ManfListView.as_view(), name='manf'),
    path('manf_delete/<int:manf_id>/',manufacturer_views.ManfDeleteView.as_view(), name='manf_delete'),
]