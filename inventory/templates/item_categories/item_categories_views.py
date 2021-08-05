# Django Imports
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings

# Custom Imports
from common.sysutil import get_sequenceval
from common.table_gen import filter_queryset, general_exclude_list

# View specific Imports
from common.models import InvItemCategories, InvItemSubCategories, InvItemMasters
from common.moduleattributes.table_fields import INV_ITEM_CATEGORIES, INV_ITEM_SUB_CATEGORIES, INV_ITEM_MASTERS

# Categories Field Lists
categories_non_editable_list = [field.name for field in InvItemCategories._meta.fields if not field.editable]
categories_exclude_list = general_exclude_list + categories_non_editable_list
#
categories_form_field_list = [field for field in INV_ITEM_CATEGORIES['fields'] if field not in categories_exclude_list]
categories_form_field_dict = {x[0]: x[1] for x in list(zip(INV_ITEM_CATEGORIES['fields'], INV_ITEM_CATEGORIES['headers'])) if
                   x[0] in categories_form_field_list}

# categories_search_field_list =

categories_listview_filed_list = ['cpt_id', 'terms_name', 'terms_days', 'terms_type']
categories_listview_filed_dict = {x[0]: x[1] for x in list(zip(
                                    INV_ITEM_CATEGORIES['fields'], INV_ITEM_CATEGORIES['headers'],
                                )) if all([x[0] in categories_form_field_list, x[0] not in []])}

# Categories Field Lists
subcategories_non_editable_list = [field.name for field in InvItemCategories._meta.fields if not field.editable]
subcategories_exclude_list = general_exclude_list + subcategories_non_editable_list
#
subcategories_form_field_list = [field for field in INV_ITEM_SUB_CATEGORIES['fields'] if field not in subcategories_exclude_list]
subcategories_form_field_dict = {x[0]: x[1] for x in
                              list(zip(INV_ITEM_SUB_CATEGORIES['fields'], INV_ITEM_SUB_CATEGORIES['headers'])) if
                              x[0] in subcategories_form_field_list}

subcategories_listview_filed_list = ['cpt_id', 'terms_name', 'terms_days', 'terms_type']
subcategories_listview_filed_dict = {x[0]: x[1] for x in list(zip(
    INV_ITEM_SUB_CATEGORIES['fields'], INV_ITEM_SUB_CATEGORIES['headers'],
)) if all([x[0] in subcategories_form_field_list, x[0] not in []])}

# class SearchForm(forms.ModelForm):
#     class Meta:
#         model = MODEL
#         fields = search_field_list
#         labels = form_field_dict
#         widgets = {x: forms.TextInput(attrs={'required': False, }) for x in search_field_list}
#
#     def __init__(self, *args, **kwargs):
#         super(SearchForm, self).__init__(*args, **kwargs)
#         for field in search_field_list:
#             self.fields[field].required = False

class DetailForm(forms.ModelForm):
    class Meta:
        model = InvItemCategories
        fields = '__all__'
        widgets = {x.name: forms.TextInput(attrs={'readonly': True, }) for x in InvItemCategories._meta.fields}

@login_required
def ItemCategoriesListView(request):
    print('REQUEST - GET -->', request.GET)
    print('REQUEST - POST -->', request.POST)
    context = {}
    context['categories_list'] = InvItemCategories.objects.all().order_by('category_name')

    category_id = request.GET.get('category_id')
    if category_id:
        category = InvItemCategories.objects.get(category_id=category_id)
        context['category'] = category
        context['category_details'] = DetailForm(instance=category)

        # Subcategory Lists
        context['subcategories_list'] = InvItemSubCategories.objects.filter(iic_category_id=category)
        context['subcategories_listview_filed_dict'] = subcategories_listview_filed_dict

    # print('FINAL CONTEXT --->',context)
    return render(request, 'item_categories/itemcategories_list.html', context)