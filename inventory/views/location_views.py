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
from common.models import InvLocations, InvSubLocations
from django import forms
from django.conf import settings


# @method_decorator(login_required, name='dispatch')
class LocationForm(forms.ModelForm):
    class Meta:
        model = InvLocations
        fields = '__all__'

APPNAME='inventory'
URLPREFIX = '/'+APPNAME+'/location{0}/'
SLUG_FIELD = 'location_id'
SLUG_URL_KWARG = SLUG_FIELD
TEMPLATE_PREFIX = 'inventory/location-{0}.html'
ORDERING = ('location_name')
FORM_CLASS = LocationForm
MODEL = InvLocations
REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "inventory:locations"
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
        model = InvLocations
        fields = '__all__'
        #exclude = ['location_id']

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
                    try:
                        self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
                    except:
                        pass
        return self.cleaned_data

class ChildForm(forms.ModelForm):
    class Meta:
        model = InvSubLocations
        fields ='__all__'
        #exclude = ['sub_location_id']

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
                    try:
                        self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
                    except:
                        pass
        return self.cleaned_data

def _get_form(request, formcls, prefix):
    data = request.POST if prefix in request.POST else None
    return formcls(data, prefix=prefix)

@method_decorator(login_required, name='dispatch')
class LocationlistView(ListView, ModelFormMixin):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    form_class = ParentForm
    MYCONTEXT = {}
    context_object_name = 'data'
    ordering = ORDERING
    #paginate_by = REC_IN_PAGE
    parentid = childid = nm = childnm =""
    currentoperation = '_find'
    operation = ''
    lastoperation = ''

    def get(self, request, *args, **kwargs):
        print('In Get')
        self.parentid = self.request.GET.get('parentid')
        self.childid = self.request.GET.get('childid')
        self.nm = self.request.GET.get('nm', "")
        self.childnm = self.request.GET.get('childnm', "")
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
        self.nm = self.request.POST.get('nm')
        self.childnm = self.request.POST.get('childnm',"")
        self.lastoperation = self.request.POST.get('lop')
        self.operation = self.request.POST.get('operation')
        if 'parent' in request.POST:
            try:
                self.MYCONTEXT['IN_PARENT_SAVE'] = request.POST
                if commonutil.hasintvalue(self.parentid):
                    parent_inst = InvLocations.objects.get(location_id=self.parentid)
                    parentform = ParentForm(self.request.POST, instance=parent_inst)
                    if parentform.is_valid():
                        parentform.save()
                else:
                    parentform = ParentForm(self.request.POST)
                    parent_inst = parentform.save(commit=False)
                    parent_inst.location_id = sysutil.get_sequenceval('inv_locations_s.nextval')
                    parentform.save()
            except Exception as ex:
                self.MYCONTEXT['ERROR_PARENT_SAVE'] = ex

        if 'child' in request.POST:
            try:
                if commonutil.hasintvalue(self.childid):
                    child_inst = InvSubLocations.objects.get(sub_location_id=self.childid)
                    self.MYCONTEXT['SAVINGCHILDINST'] = child_inst
                    childform = ChildForm(self.request.POST, instance=child_inst)
                    self.MYCONTEXT['SAVINGchild'] = childform
                    if childform.is_valid():
                        childform.save()
                else:
                    childform = ChildForm(self.request.POST)
                    child_inst = childform.save(commit=False)
                    parent_inst = InvLocations.objects.get(location_id=self.parentid)
                    child_inst.sub_location_id = sysutil.get_sequenceval('inv_sub_locations_s.nextval')
                    child_inst.il_location_id = parent_inst
                    childform.save()
            except Exception as ex:
                self.MYCONTEXT['ERROR_SAVE_SHILD'] = str(ex)

        return  self.get(self, request, *args, **kwargs)

    def get_success_url(self):
        return REVERSE

    def get_queryset(self):
        qs = self.model.objects.all()
        return qs

    def get_context_data(self, **kwargs):
        self.MYCONTEXT['errormessage'] = self.request.POST
        print('In context')
        context = super(LocationlistView, self).get_context_data(**kwargs)
        childrows = {}
        rows = self.get_queryset().order_by('location_name')
        if commonutil.hasstrvalue(self.nm):
            rows = rows.filter(location_name__icontains=self.nm)
        if commonutil.hasintvalue(self.parentid):
            rows = rows.filter(location_id=self.parentid)
        context['parentrows'] = rows[:MASTER_RECORDS]
        if len(rows) == 1:
            self.parentid = rows[0].location_id
            childrows = InvSubLocations.objects.filter(il_location_id__location_id=self.parentid).order_by('sub_location')
            if commonutil.hasstrvalue(self.childnm):
                childrows = childrows.filter(sub_location__icontains=self.childnm)
            childrows = childrows[:MASTER_RECORDS]
        context['childrows'] = childrows
        parentform = {}
        childform = {}
        if commonutil.nvl(self.operation,'none') == 'parent_new':
            self.parentid = ""
            self.childid = ""
            parentform = ParentForm()
            context['parentform'] = parentform
            context['parentform_title'] = 'New Location'

        if commonutil.nvl(self.operation,'none') == 'child_new':
            self.childid = ""
            childform= ChildForm()
            context['childform'] = childform
            context['childform_title'] = 'New Sub Location'

        if commonutil.hasintvalue(self.parentid):
            parentrow = InvLocations.objects.get(location_id=self.parentid)
            parentform = ParentForm(instance=parentrow)
            context['parentform'] = parentform
            context['parentform_title'] = 'Location'

        if commonutil.hasintvalue(self.childid):
            childrow = InvSubLocations.objects.get(sub_location_id=self.childid)
            childform = ChildForm(instance=childrow)
            context['childform_title'] = 'Sub Location'
            context['childform'] = childform

        context['MYCONTEXT'] = self.MYCONTEXT
        context['operation'] = self.operation
        context['parentid'] = self.parentid
        context['childid'] = self.childid
        context['nm'] = self.nm
        context['childnm'] = self.childnm
        context['parentlabel'] = 'Loc'
        context['childlabel'] = 'Sub Loc'

        return context



class SubLocationDeleteView(DeleteView):
    model = InvSubLocations
    slug_field = 'sub_location_id'
    slug_url_kwarg = 'sub_location_id'
    template_name = 'common/confirm_delete.html'
    context_object_name = 'object'

    def get_success_url(self):
        return reverse(REVERSE)


class LocationDeleteView(DeleteView):
    model = InvLocations
    slug_field = 'location_id'
    slug_url_kwarg = 'location_id'
    template_name = 'common/confirm_delete.html'
    context_object_name = 'object'

    def get_success_url(self):
        return reverse(REVERSE)