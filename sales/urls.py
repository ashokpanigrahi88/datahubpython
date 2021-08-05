from django.conf.urls import url
from django.urls import path, re_path

from sales.templates.ar_options import aroptions_views

app_name = 'sales'

urlpatterns = [
    #path('moveitem/', moveitem.MoveToPrimaryView.as_view(), name='moveitem'),
    #url(r'^picksalesorder/$', picksalesorder.SalesOrderPickingView.as_view(), name='picksalesorder'),
    ### INVENTORY OPTIONS
    path('options/', aroptions_views.ArOptionsListView.as_view(), name='aroptions_list'),
    path('aroptions/create/', aroptions_views.ArOptionsCreateView.as_view(),
         name='aroptions_create'),
    path('aroptions/update-<str:ar_option_id>/', aroptions_views.ArOptionsUpdateView.as_view(),
         name='aroptions_update'),
]
