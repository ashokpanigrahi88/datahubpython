from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
# specific to this view
from django.views.generic.edit import ModelFormMixin

from common import (sysutil, commonutil)
# from setup.templates.commodities.commodities_forms import *
from common.models import InvItemSubCategories, InvItemCategories
from django import forms
from django.conf import settings


# @method_decorator(login_required, name='dispatch')
class CategoryForm(forms.ModelForm):
    class Meta:
        model = InvItemCategories
        fields = '__all__'

APPNAME='inventory'
URLPREFIX = '/'+APPNAME+'/category{0}/'
SLUG_FIELD = 'category_id'
SLUG_URL_KWARG = SLUG_FIELD
TEMPLATE_PREFIX = 'inventory/category-{0}.html'
ORDERING = ('category_name')
FORM_CLASS = CategoryForm
MODEL = InvItemCategories
REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "inventory:itemcategory"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
        'update': URLPREFIX.format('_update'),
        'delete': URLPREFIX.format('_delete'),
        'list': URLPREFIX.format('_list'),
        'title' : 'Categories',
        'findfield' : 'Category Name',
             }
MASTER_RECORDS=15
class ParentForm(forms.ModelForm):
    class Meta:
        model = InvItemCategories
        fields = ['category_name','category_code','description','bin_identifier',
                  'category_markup','take_snapshot','key_words','picturename','amazon_percent','ebay_percent','attribute1','attribute2']
        #exclude = ['category_id']

    def __init__(self, *args, **kwargs):
        super(ParentForm, self).__init__(*args, **kwargs)
        #self.fields['take_snapshot'].widget = forms.CheckboxInput()
        for field in MODEL._meta.fields:
            if field.name in self.fields and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in MODEL._meta.fields:
            if field.name in self.fields and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
        return self.cleaned_data

class ChildForm(forms.ModelForm):
    class Meta:
        model = InvItemSubCategories
        fields = ['sub_category_name','sub_category_code',
                  'bin_identifier','sub_category_markup','take_snapshot','key_words','picturename',
                  'amazon_percent','ebay_percent','description','attribute1','attribute2']
        #exclude = ['sub_category_id']

    def __init__(self, *args, **kwargs):
        super(ChildForm, self).__init__(*args, **kwargs)
        #self.fields['take_snapshot'].widget = forms.CheckboxInput()
        for field in MODEL._meta.fields:
            if field.name in self.fields and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in MODEL._meta.fields:
            if field.name in self.fields and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
        return self.cleaned_data

def _get_form(request, formcls, prefix):
    data = request.POST if prefix in request.POST else None
    return formcls(data, prefix=prefix)

@method_decorator(login_required, name='dispatch')
class CategorylistView(ListView, ModelFormMixin):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    form_class = ParentForm
    MYCONTEXT = {}
    context_object_name = 'data'
    ordering = ORDERING
    #paginate_by = REC_IN_PAGE
    parentid = childid = nm = ""
    currentoperation = '_find'
    operation = ''
    lastoperation = ''

    def get(self, request, *args, **kwargs):
        print('In Get')
        self.parentid = self.request.GET.get('parentid')
        self.childid = self.request.GET.get('childid')
        self.nm = self.request.GET.get('nm',"")
        self.childnm = self.request.GET.get('childnm',"")
        self.lastoperation = self.request.GET.get('lop')
        self.operation = self.request.GET.get('operation')
        page = self.request.GET.get('page')
        self.object = None
        self.form = self.get_form(self.form_class)
        return ListView.get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.MYCONTEXT['errormessage'] = request.POST
        self.parentid = self.request.POST.get('parentid')
        self.childid = self.request.POST.get('childid')
        self.nm = self.request.POST.get('nm',"")
        self.childnm = self.request.POST.get('childnm',"")
        self.lastoperation = self.request.POST.get('lop')
        self.operation = self.request.POST.get('operation')
        if 'parent' in request.POST:
            try:
                if commonutil.hasintvalue(self.parentid):
                    parent_inst = InvItemCategories.objects.get(category_id=self.parentid)
                    parentform = ParentForm(self.request.POST, instance=parent_inst)
                    if parentform.is_valid():
                        parentform.save()
                else:
                    parentform = ParentForm(self.request.POST)
                    parent_inst = parentform.save(commit=False)
                    parent_inst.category_id = sysutil.get_sequenceval('inv_item_categories_s.nextval')
                    parentform.save()
            except Exception as ex:
                self.MYCONTEXT['errormessage'] = ex

        if 'child' in request.POST:
            try:
                if commonutil.hasintvalue(self.childid):
                    child_inst = InvItemSubCategories.objects.get(sub_category_id=self.childid)
                    self.MYCONTEXT['SAVINGPARENTINST'] = child_inst
                    childform = ChildForm(self.request.POST, instance=child_inst)
                    self.MYCONTEXT['SAVINGchild'] = childform
                    if childform.is_valid():
                        childform.save()
                else:
                    childform = ChildForm(self.request.POST)
                    child_inst = childform.save(commit=False)
                    parent_inst = InvItemCategories.objects.get(category_id=self.parentid)
                    child_inst.sub_category_id = sysutil.get_sequenceval('inv_item_sub_categories_s.nextval')
                    child_inst.iic_category_id = parent_inst
                    childform.save()
            except Exception as ex:
                self.MYCONTEXT['errormessage'] = ex

        return  self.get(self, request, *args, **kwargs)

    def get_success_url(self):
        return REVERSE

    def get_queryset(self):
        qs = self.model.objects.all()
        return qs

    def get_context_data(self, **kwargs):
        self.MYCONTEXT['errormessage'] = self.request.POST
        print('In context')
        context = super(CategorylistView, self).get_context_data(**kwargs)
        childrows = {}
        rows = self.get_queryset().order_by('category_name')
        if commonutil.hasstrvalue(self.nm):
            rows = rows.filter(category_name__icontains=self.nm)
        if commonutil.hasintvalue(self.parentid):
            rows = rows.filter(category_id=self.parentid)
        context['parentrows'] = rows[:MASTER_RECORDS]
        if len(rows) == 1:
            self.parentid = rows[0].category_id
            childrows = InvItemSubCategories.objects.filter(iic_category_id__category_id=self.parentid).order_by('sub_category_name')
            if commonutil.hasstrvalue(self.childnm):
                childrows = childrows.filter(sub_category_name__icontains=self.childnm)
        context['childrows'] = childrows
        parentform = {}
        childform = {}
        if commonutil.nvl(self.operation,'none') == 'parent_new':
            self.parentid = ""
            self.childid = ""
            parentform = ParentForm()
            context['parentform'] = parentform
            context['parentform_title'] = 'New Category'

        if commonutil.nvl(self.operation,'none') == 'child_new':
            self.childid = ""
            childform= ChildForm()
            context['childform'] = childform
            context['childform_title'] = 'New Sub Category'

        if commonutil.hasintvalue(self.parentid):
            parentrow = InvItemCategories.objects.get(category_id=self.parentid)
            parentform = ParentForm(instance=parentrow)
            context['parentform'] = parentform
            context['parentform_title'] = 'Category'

        if commonutil.hasintvalue(self.childid):
            childrow = InvItemSubCategories.objects.get(sub_category_id=self.childid)
            childform = ChildForm(instance=childrow)
            context['childform_title'] = 'Sub Category'
            context['childform'] = childform

        context['MYCONTEXT'] = self.MYCONTEXT
        context['operation'] = self.operation
        context['parentid'] = self.parentid
        context['childid'] = self.childid
        context['nm'] = self.nm
        context['chilnm'] = self.childnm
        context['parentlabel'] = 'Cat'
        context['childlabel'] = 'Sub Cat'

        return context



class SubCategoryDeleteView(DeleteView):
    model = InvItemSubCategories
    slug_field = 'sub_category_id'
    slug_url_kwarg = 'sub_category_id'
    template_name = 'common/confirm_delete.html'
    context_object_name = 'object'

    def get_success_url(self):
        return reverse(REVERSE)


class CategoryDeleteView(DeleteView):
    model = InvItemCategories
    slug_field = 'category_id'
    slug_url_kwarg = 'category_id'
    template_name = 'common/confirm_delete.html'
    context_object_name = 'object'

    def get_success_url(self):
        return reverse(REVERSE)