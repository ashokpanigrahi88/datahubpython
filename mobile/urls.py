from django.conf.urls import url
from django.urls import path, re_path
from mobile.views import (pricecheck , moveitem , picksalesorder ,
                           salesorderquery, extmovement, newgrn,additemtobatch)
app_name = 'mobile'


urlpatterns = [
    path('pricecheck/', pricecheck.PriceCheckView.as_view(), name='pricecheck'),
    path('moveitem/', moveitem.MoveToPrimaryView.as_view(), name='moveitem'),
    url(r'^picksalesorder/$', picksalesorder.SalesOrderPickingView.as_view(), name='picksalesorder'),
    url(r'^salesorderquery/$', salesorderquery.SalesOrderQueryView.as_view(), name='salesorderquery'),
    url(r'^extmovement/$', extmovement.ExtMovementView.as_view(), name='extmovement'),
    url(r'^creategrn/$', newgrn.CreateGRNView.as_view(), name='creategrn'),
    url(r'^additemtobatch/$', additemtobatch.AddItemToBatchView.as_view(), name='additemtobatch'),
]

