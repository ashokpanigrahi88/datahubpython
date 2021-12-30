from django.conf.urls import url
from django.urls import path, re_path

from ecomm.views import (eordsummary)
app_name = 'ecomm'

urlpatterns = [
    #path('moveitem/', moveitem.MoveToPrimaryView.as_view(), name='moveitem'),
    #url(r'^picksalesorder/$', picksalesorder.SalesOrderPickingView.as_view(), name='picksalesorder'),
    ### INVENTORY OPTIONS
    #path('options/', aroptions_views.ArOptionsListView.as_view(), name='aroptions_list'),
    re_path('^ecomordsum/$', eordsummary.EcomOrdSummaryView.as_view(), name='eordsummary'),
]