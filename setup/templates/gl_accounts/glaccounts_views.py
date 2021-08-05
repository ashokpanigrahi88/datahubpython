from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings

# specific to this view
from common.models import GlCategories, GlSubCategories, GlAccountCodes
from common.sysutil import get_sequenceval
from common.table_gen import formfilter_queryset, general_exclude_list
from common.moduleattributes.table_fields import GL_CATEGORIES, GL_ACCOUNT_CODES

gl_exclude_list = general_exclude_list + ['bu_id','gl_category_id',]

gl_field_list = [field for field in GL_CATEGORIES['fields'] if field not in gl_exclude_list]

gl_field_dict = {x[0]: x[1] for x in list(zip(GL_CATEGORIES['fields'], GL_CATEGORIES['headers'])) if
              x[0] in gl_field_list}

class GlCategoryForm(forms.ModelForm):
    class Meta:
        model = GlCategories
        fields = gl_field_list
        labels = gl_field_dict

    def __init__(self, *args, **kwargs):
        super(GlCategoryForm, self).__init__(*args, **kwargs)
        for field in GlCategories._meta.fields:
            if field.name in gl_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in GlCategories._meta.fields:
            if field.name in gl_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    try:
                        self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
                    except:
                        self.cleaned_data[field.name] = self.cleaned_data[field.name]
        return self.cleaned_data


gl_subcat_exclude_list = general_exclude_list + ['bu_id', 'gl_category_id', ]

gl_subcat_field_list = ['gl_sub_category_name', 'gl_qualifier_code1', 'gl_qualifier_code2', 'active',
                        'gl_sub_category_desc']

gl_subcat_field_dict = {'gl_sub_category_name': 'Sub Category Name', 'gl_qualifier_code1': 'Qualifier Code 1',
                        'gl_qualifier_code2': 'Qualifier Code 2', 'active': 'Active',
                        'gl_sub_category_desc': 'Description'}

class GlSubCategoryForm(forms.ModelForm):
    class Meta:
        model = GlSubCategories
        fields = gl_subcat_field_list
        labels = gl_subcat_field_dict

    def __init__(self, *args, **kwargs):
        super(GlSubCategoryForm, self).__init__(*args, **kwargs)
        for field in GlSubCategories._meta.fields:
            if field.name in gl_subcat_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in GlSubCategories._meta.fields:
            if field.name in gl_subcat_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    try:
                        self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
                    except:
                        self.cleaned_data[field.name] = self.cleaned_data[field.name]
        return self.cleaned_data


APPNAME = 'setup'
URLPREFIX = '/' + APPNAME + '/glcodes{0}/'
TEMPLATE_PREFIX = 'gl_accounts/glcodes-{0}.html'

REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "setup:glcodes_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
             'update': URLPREFIX.format('_update'),
             'delete': URLPREFIX.format('_delete'),
             'list': URLPREFIX.format('_list'),
             'title': 'GL Account Codes',
             # 'findfield': 'Currency Rate',
             }

non_editable_list = [field.name for field in GlAccountCodes._meta.fields if not field.editable]

account_exclude_list = general_exclude_list + non_editable_list + []

account_field_list = [field for field in GL_ACCOUNT_CODES['fields'] if field not in account_exclude_list]

account_field_dict = {x[0]: x[1] for x in list(zip(GL_ACCOUNT_CODES['fields'], GL_ACCOUNT_CODES['headers'])) if
                 x[0] in account_field_list}
#
#
class GlAccountsForm(forms.ModelForm):
    class Meta:
        model = GlAccountCodes
        fields = account_field_list
        labels = account_field_dict

    def __init__(self, *args, **kwargs):
        super(GlAccountsForm, self).__init__(*args, **kwargs)
        for field in GlAccountCodes._meta.fields:
            if field.name in account_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in GlAccountCodes._meta.fields:
            if field.name in account_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    try:
                        self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
                    except:
                        self.cleaned_data[field.name] = self.cleaned_data[field.name]
        return self.cleaned_data
#
class DetailForm(forms.ModelForm):
    class Meta:
        model = GlAccountCodes
        fields = '__all__'
        widgets = {x: forms.TextInput(attrs={'readonly': True, }) for x in account_field_list}


@login_required
def GlCategoryListView(request):
    print('REQUEST - GET -->',request.GET)
    print('REQUEST - POST -->', request.POST)
    context = {}
    context['MYCONTEXT'] = MYCONTEXT
    context['gl_categories'] = GlCategories.objects.all()
    context['search_field_list'] = search_field_list

    if 'glcategory' in request.GET:
        glcategoryid = request.GET.get('glcategory')
        gl_category = GlCategories.objects.get(gl_category_id=glcategoryid)
        context['gl_category'] = gl_category
        gl_subcategories = GlSubCategories.objects.filter(gc_gl_category_id=glcategoryid)
        context['gl_subcategories'] = gl_subcategories

    if 'new_glcategory_form' in request.GET:
        context['gl_category_form'] = GlCategoryForm()

    if 'edit_glcategory' in request.GET:
        glcategoryid = request.GET.get('edit_glcategory')
        gl_category = GlCategories.objects.get(gl_category_id=glcategoryid)
        context['gl_category'] = gl_category
        context['gl_category_form'] = GlCategoryForm(instance=gl_category)

    if 'save_glcategory_form' in request.POST:
        gl_category_form = GlCategoryForm(request.POST)
        gl_category_instance = gl_category_form.save(commit=False)
        if request.GET.get('edit_glcategory'):
            gl_category_instance.gl_category_id = request.GET.get('edit_glcategory')
        else:
            gl_category_instance.gl_category_id = get_sequenceval('gl_categories_s.nextval')
        gl_category_instance.save()
        return redirect('/setup/glcategories/?glcategory={0}'.format(gl_category_instance.gl_category_id))

    if 'new_glsubcategory_form' in request.GET:
        glcategoryid = request.GET.get('glcategory')
        gl_category = GlCategories.objects.get(gl_category_id=glcategoryid)
        context['gl_category'] = gl_category
        gl_subcategories = GlSubCategories.objects.filter(gc_gl_category_id=glcategoryid)
        context['gl_subcategories'] = gl_subcategories
        initial_values = {'gc_gl_category_id': gl_category}
        context['gl_subcategory_form'] = GlSubCategoryForm(initial=initial_values)

    if 'edit_glsubcategory' in request.GET:
        glcategoryid = request.GET.get('glcategory')
        gl_category = GlCategories.objects.get(gl_category_id=glcategoryid)
        context['gl_category'] = gl_category
        gl_subcategories = GlSubCategories.objects.filter(gc_gl_category_id=glcategoryid)
        context['gl_subcategories'] = gl_subcategories
        gl_subcategory_id = request.GET.get('edit_glsubcategory')
        gl_subcategory = GlSubCategories.objects.get(gl_sub_category_id=gl_subcategory_id)
        context['gl_subcategory'] = gl_subcategory
        context['gl_subcategory_form'] = GlSubCategoryForm(instance=gl_subcategory)

    if 'save_glsubcategory_form' in request.POST:
        glcategoryid = request.GET.get('glcategory')
        gl_category = GlCategories.objects.get(gl_category_id=glcategoryid)
        context['gl_category'] = gl_category
        gl_subcategories = GlSubCategories.objects.filter(gc_gl_category_id=glcategoryid)
        context['gl_subcategories'] = gl_subcategories
        gl_subcategory_form = GlSubCategoryForm(request.POST)
        gl_subcategory_instance = gl_subcategory_form.save(commit=False)
        print('SubCat Instance -->',gl_subcategory_instance)
        print('SubCat Instance - ID -->', gl_subcategory_instance.gl_sub_category_id)
        if request.GET.get('edit_glsubcategory'):
            gl_subcategory_instance.gl_sub_category_id = request.GET.get('edit_glsubcategory')
        else:
            gl_subcategory_instance.gl_sub_category_id = get_sequenceval('gl_sub_categories_s.nextval')
        gl_subcategory_instance.gc_gl_category_id = gl_category
        gl_subcategory_instance.save()
        return redirect('/setup/glcategories/?glcategory={0}'.format(gl_category.gl_category_id))

    return render(request, TEMPLATE_PREFIX.format('l'), context)


search_field_list = ['gc_gl_category_id', 'gsc_gl_sub_category_id', 'gl_account_code', 'short_name', ]
search_field_dict = {'gc_gl_category_id': 'Category', 'gsc_gl_sub_category_id': 'Sub Category',
                     'gl_account_code': 'Account Code', 'short_name': 'Name', }


class GlCodesSearchForm(forms.ModelForm):
    class Meta:
        model = GlAccountCodes
        fields = search_field_list
        labels = search_field_dict

    def __init__(self, *args, **kwargs):
        super(GlCodesSearchForm, self).__init__(*args, **kwargs)
        for field in search_field_list:
            self.fields[field].required = False


@method_decorator(login_required, name='dispatch')
class GLAccountCodesListView(ListView):
    model = GlSubCategories
    template_name = TEMPLATE_PREFIX.format('glsubcategory_codeslist')

    def get_context_data(self, **kwargs):
        print('REQUEST - GET --->',self.request.GET)
        print('REQUEST - POST --->', self.request.POST)
        context = super(GLAccountCodesListView, self).get_context_data(**kwargs)
        glcodes_list = GlAccountCodes.objects.all().order_by('gl_account_code')
        print('Full QUERY SET - ', len(glcodes_list))
        context['glcodes_search_form'] = GlCodesSearchForm()

        if 'list_filter' in self.request.GET or any([self.request.GET.get(x) for x in search_field_list]):
            glcodes_list = formfilter_queryset(self.request.GET, glcodes_list, search_field_list, show_matches=True)
            context['glcodes_search_form'] = GlCodesSearchForm(self.request.GET)
            context['glcodes_list'] = glcodes_list
            print('Filtering QUERY SET - ', len(glcodes_list))

        if len(glcodes_list) == 1:
            print('Only 1 account code found ----------')
            context['glcodes_list'] = glcodes_list
            context['details'] = DetailForm(instance=glcodes_list[0])
            context['paginated'] = False

        elif self.kwargs.get('gl_account_code'):
            print('Particular account requested ----------')
            glaccount = GlAccountCodes.objects.filter(gl_account_code=self.kwargs.get('gl_account_code'))
            context['details'] = DetailForm(instance=glaccount[0])
            context['glcodes_list'] = glaccount
            context['paginated'] = False

        if len(glcodes_list) >= REC_IN_PAGE:
            print('Multiple accounts found ----------')
            glaccountcodespage = self.request.GET.get('glaccountcodespage')
            glcodes_paginator = Paginator(glcodes_list, REC_IN_PAGE)

            try:
                glcodes_list = glcodes_paginator.page(glaccountcodespage)
            except PageNotAnInteger:
                glcodes_list = glcodes_paginator.page(1)
            except EmptyPage:
                glcodes_list = glcodes_paginator.page(glcodes_paginator.num_pages)
            context['glcodes_list'] = glcodes_list
            context['paginated'] = True

        print('CONTEXT - check account_code -',context)

        return context


@method_decorator(login_required, name='dispatch')
class GlAccountCodesCreateView(CreateView):
    # model = MODEL
    form_class = GlAccountsForm
    template_name = TEMPLATE_PREFIX.format('glaccountcode_create')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.gl_account_id = get_sequenceval('gl_account_codes_s.nextval')
        instance.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class GlAccountCodesUpdateView(UpdateView):
    model = GlAccountCodes
    form_class = GlAccountsForm
    template_name = TEMPLATE_PREFIX.format('glaccountcode_create')
    slug_field = 'gl_account_id'
    slug_url_kwarg = 'gl_account_id'

    def get_context_data(self, **kwargs):
        context = super(GlAccountCodesUpdateView, self).get_context_data(**kwargs)
        context['gl_account_code'] = self.object.gl_account_code
        print('CONTEXT', context)
        return context

    def get_success_url(self):
        context = self.get_context_data()
        return '/setup/glcodes_list/?gl_account_code={0}'.format(context['gl_account_code'])


@method_decorator(login_required, name='dispatch')
class GlCategoryDeleteView(DeleteView):
    model = GlCategories
    slug_field = 'gl_category_id'
    slug_url_kwarg = 'gl_category_id'
    template_name = TEMPLATE_PREFIX.format('glcategory_delete')

    def get_success_url(self):
        return reverse('setup:glcategories')


@method_decorator(login_required, name='dispatch')
class GlSubCategoryDeleteView(DeleteView):
    model = GlSubCategories
    slug_field = 'gl_sub_category_id'
    slug_url_kwarg = 'gl_sub_category_id'
    template_name = TEMPLATE_PREFIX.format('glsubcategory_delete')

    def get_context_data(self, **kwargs):
        context = super(GlSubCategoryDeleteView, self).get_context_data(**kwargs)
        context['gl_category_id'] = self.object.gc_gl_category_id.gl_category_id
        print('Context -->', context)
        return context

    def get_success_url(self):
        context = self.get_context_data()
        return '/setup/glcategories/?glcategory={0}'.format(context['gl_category_id'])


@method_decorator(login_required, name='dispatch')
class GlAccountCodeDeleteView(DeleteView):
    model = GlAccountCodes
    slug_field = 'gl_account_id'
    slug_url_kwarg = 'gl_account_id'
    template_name = TEMPLATE_PREFIX.format('glaccountcode_delete')
    success_url = '/setup/glcodes_list/'

    # def get_context_data(self, **kwargs):
    #     context = super(GlAccountCodeDeleteView, self).get_context_data(**kwargs)
    #     context['gl_subcategory_id'] = self.object.gsc_gl_sub_category_id.gl_sub_category_id
    #     print('Context -->', context)
    #     return context

    # def get_success_url(self):
    #     context = self.get_context_data()
    #     return '/setup/glcodes_list/'
