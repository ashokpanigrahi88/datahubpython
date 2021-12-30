"""oratech URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views
from django.urls import include, path
from rest_framework import routers
from restapi import views as restapiviews

router = routers.DefaultRouter()
router.register(r'users', restapiviews.UserViewSet)
router.register(r'groups', restapiviews.GroupViewSet)

urlpatterns = [
    path(r'common/', include('common.urls', namespace='common'), name='common'),
    path(r'setup/', include('setup.urls', namespace='setup'), name='setup'),
    path(r'mobile/', include('mobile.urls', namespace='mobile'), name='mobile'),
    path(r'enquiry/', include('enquiry.urls', namespace='enquiry'), name='enquiry'),
    path(r'ecomm/', include('ecomm.urls', namespace='ecomm'), name='ecomm'),
    path(r'inventory/', include('inventory.urls', namespace='inventory'), name='inventory'),
    path(r'sales/', include('sales.urls', namespace='sales'), name='sales'),
    path(r'purchase/', include('purchase.urls', namespace='purcahse'), name='purchase'),
    path(r'warehouse/', include('warehouse.urls', namespace='warehouse'), name='warehouse'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/logout/', views.LogoutView.as_view(next_page='/'), name='logout'),
    # path('accounts/profile/', include('common.urls',namespace='common'), name='profile'),
    path(r'admin/', admin.site.urls, name ='admin'),
    #path('restapi/', include(router.urls)),
    #path('restapi/api-auth/', include('rest_framework.urls', namespace='rest_framework'),name='restapi'),
    path(r'rest-api/', include('restapi.urls', namespace='restapi'), name='restapi'),
    path(r'', include('common.urls', namespace='common'), name='main'),
]

