from django.conf.urls import url
from django.urls import path, re_path
app_name = 'sales'


urlpatterns = [
    path('moveitem/', moveitem.MoveToPrimaryView.as_view(), name='moveitem'),
    url(r'^picksalesorder/$', picksalesorder.SalesOrderPickingView.as_view(), name='picksalesorder'),
]
