from django.conf.urls import url
from django.urls import path, re_path

app_name = 'pricing'

from pricing.templates.price_breaks import price_breaks_views

urlpatterns = [
    ### PRICE BREAKS
    path('pricebreaks/', price_breaks_views.PriceBreakHeadersListView.as_view(), name='pricebreaks'),
    path('pricebreakheader_create/', price_breaks_views.PriceBreakHeadersCreateView.as_view(),name='pricebreakheader_create'),
    path('pricebreakheader_update/<str:price_break_id>/', price_breaks_views.PriceBreakHeadersUpdateView.as_view(),
         name='pricebreakheader_update'),
    path('pricebreakheader_delete/<str:price_break_id>/', price_breaks_views.PriceBreakHeadersDeleteView.as_view(),
         name='pricebreakheader_delete'),
    path('pricebreakline_create/', price_breaks_views.PriceBreakLinesCreateView.as_view(),
         name='pricebreakline_create'),
    path('pricebreakline_update/<str:price_break_line_id>/', price_breaks_views.PriceBreakLinesUpdateView.as_view(),
         name='pricebreakline_update'),
    path('pricebreakline_delete/<str:price_break_line_id>/', price_breaks_views.PriceBreakLinesDeleteView.as_view(),
         name='pricebreakline_delete'),
]