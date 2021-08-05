from django.urls import path
from common.views import *
from restapi.views import *


urlpatterns = [
    path('createuser/', UserCreateView.as_view(), name='createuser'),
    path('listusers/', UserListView.as_view(), name='listusers'),
    path('edituser/<int:user_id>/', UserUpdateView.as_view(), name='edituser'),
    path('detailuser/<int:user_id>/', UserDetailView.as_view(), name='detailusser'),
    path('deleteuser/<int:user_id>/', UserDeleteView.as_view(),name='deleteuser'),
    path('listbs/', ListBusinessSectorApiView.as_view(),name='listbs'),
    path('', MainView.as_view(), name='main'),
]


handler404 = 'common.views.error_404_view'