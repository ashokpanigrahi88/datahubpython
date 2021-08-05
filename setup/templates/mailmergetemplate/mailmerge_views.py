from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
from django.db import transaction

# specific to this view
from common.models import CmnMailmergeHeaders, CmnMailmergeLines
from common.sysutil import get_sequenceval
from common.table_gen import filter_queryset, general_exclude_list
from common.moduleattributes.table_fields import CMN_MAILMERGE_HEADERS

MODEL = CmnMailmergeHeaders

non_editable_list = [field.name for field in MODEL._meta.fields if not field.editable]

exclude_list = general_exclude_list + non_editable_list + []

field_list = [field for field in CMN_MAILMERGE_HEADERS['fields'] if field not in exclude_list]

field_dict = {x[0]: x[1] for x in list(zip(CMN_MAILMERGE_HEADERS['fields'], CMN_MAILMERGE_HEADERS['headers'])) if x[0] in field_list}


class MailHeaderForm(forms.ModelForm):
    class Meta:
        model = CmnMailmergeHeaders
        fields = field_list
        labels = field_dict

    def __init__(self, *args, **kwargs):
        super(MailHeaderForm, self).__init__(*args, **kwargs)
        for field in MODEL._meta.fields:
            if field.name in field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in MODEL._meta.fields:
            if field.name in field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
        return self.cleaned_data

class MailLinesForm(forms.ModelForm):
    class Meta:
        model = CmnMailmergeLines
        fields = ['sl_no','active', 'variable', 'identifier', 'line_text']
        widgets = {
            'line_text': forms.Textarea(attrs={'cols': 80, 'rows': 3}),
        }


from django.forms import inlineformset_factory
MailMergeFormset = inlineformset_factory(CmnMailmergeHeaders, CmnMailmergeLines,
                                         MailLinesForm, extra=2)


class DetailForm(forms.ModelForm):
    class Meta:
        model = CmnMailmergeHeaders
        fields = '__all__'
        widgets = {x:forms.TextInput(attrs={'readonly': True,}) for x in field_list}


APPNAME = 'setup'
URLPREFIX = '/' + APPNAME + '/mailmerge{0}/'
TEMPLATE_PREFIX = 'mailmergetemplate/mailmerge-{0}.html'

REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "setup:mailmerge_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
             'update': URLPREFIX.format('_update'),
             'delete': URLPREFIX.format('_delete'),
             'list': URLPREFIX.format('_list'),
             'title': 'Mail Merge Template',
             # 'findfield': 'Currency Rate',
             }
search_field_list = ['identifier', 'table_view_name', ]


@method_decorator(login_required, name='dispatch')
class MailMergeListView(ListView):
    model = CmnMailmergeHeaders
    template_name = TEMPLATE_PREFIX.format('l')
    context_object_name = 'data'
    ordering = ('merge_header_id',)
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(MailMergeListView, self).get_context_data(**kwargs)
        mail_headers = CmnMailmergeHeaders.objects.all().order_by('merge_header_id',)

        context['search_field_dict'] = {x:{'label':field_dict[x],'value':''} for x in search_field_list}
        if 'list_filter' in self.request.GET:
            context, mail_headers = filter_queryset(context, self.request.GET, mail_headers, search_field_list)

        mailheaderpage = self.request.GET.get('page')
        paginator = Paginator(mail_headers, self.paginate_by)
        try:
            mail_headers = paginator.page(mailheaderpage)
        except PageNotAnInteger:
            mail_headers = paginator.page(1)
        except EmptyPage:
            mail_headers = paginator.page(paginator.num_pages)

        context['rows'] = mail_headers
        context['request'] = self.request
        context['MYCONTEXT'] = MYCONTEXT

        return context


@method_decorator(login_required, name='dispatch')
class MailMergeDetailView(DetailView):
    model = CmnMailmergeHeaders
    template_name = TEMPLATE_PREFIX.format('detail')
    context_object_name = 'mail_header'
    slug_field = 'merge_header_id'
    slug_url_kwarg = 'merge_header_id'

    def get_context_data(self, **kwargs):
        context = super(MailMergeDetailView, self).get_context_data(**kwargs)
        print('context -->', context)
        print(context['mail_header'])
        context['details'] = DetailForm(instance=context['mail_header'])
        context['mailmergelines'] = CmnMailmergeLines.objects.filter(merge_header_id=context['mail_header']).order_by('merge_line_id')
        return context


@method_decorator(login_required, name='dispatch')
class MailMergeLinesFormsetCreateView(CreateView):
    model = CmnMailmergeHeaders
    template_name = TEMPLATE_PREFIX.format('formset')
    form_class = MailHeaderForm
    success_url = REVERSE

    def get_context_data(self, **kwargs):
        context = super(MailMergeLinesFormsetCreateView, self).get_context_data(**kwargs)

        context['lines_formset'] = MailMergeFormset()
        if self.request.POST:
            context['lines_formset'] = MailMergeFormset(self.request.POST)

        print('context -->', context)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        with transaction.atomic():

            if str(form) == str(MailHeaderForm()):
                return self.render_to_response(self.get_context_data(form=form))

            mail_header = form.save(commit=False)
            mail_header.merge_header_id = get_sequenceval('cmn_mailmerge_headers_s.nextval')
            mail_header.save()

            lines_formset = context['lines_formset']
            if lines_formset.is_valid():
                # print('Lines Instances',lines_formset.save(commit=False))

                for line_form in lines_formset.initial_forms:
                    line_forminstance = line_form.instance

                    # First - Ignore Blank Rows
                    if line_forminstance.merge_line_id is None:
                        print('---- Blank row detected - skipping')
                        continue

                    # Second - Delete Forms
                    if line_form in lines_formset.deleted_forms:
                        print('---- Deleting --->', line_forminstance)
                        line_forminstance.delete()

                    # Third - Update Existing Forms
                    elif line_form.has_changed():
                        print('---- Updating --->', line_forminstance)
                        data = line_form.save(commit=False)
                        # data.client_id = self.request.user.client_id
                        data.save()

                print('New Forms --->')
                for line_form in lines_formset.extra_forms:
                    line_forminstance = line_form.instance

                    # First - Ignore Blank Rows
                    if not line_form.has_changed():
                        print('---- New blank row detected - skipping')
                        continue

                    # Second - Save New Forms
                    print('---- Saving New Item --->', line_forminstance)
                    data = line_form.save(commit=False)
                    data.merge_header_id = mail_header
                    data.merge_line_id = get_sequenceval('cmn_mailmerge_lines_s.nextval')
                    print(data)
                    print(data.merge_header_id)
                    data.save()
                print('---------------------------------------------')

                return redirect('setup:mailmerge_detail', merge_header_id=mail_header.merge_header_id)
            else:
                return self.render_to_response(self.get_context_data(form=form, lines_formset=lines_formset))


@method_decorator(login_required, name='dispatch')
class MailMergeLinesFormsetUpdateView(UpdateView):
    model = CmnMailmergeHeaders
    template_name = TEMPLATE_PREFIX.format('formset')
    form_class = MailHeaderForm
    # context_object_name = 'mail_header_form'
    slug_field = 'merge_header_id'
    slug_url_kwarg = 'merge_header_id'

    def get_context_data(self, **kwargs):
        context = super(MailMergeLinesFormsetUpdateView, self).get_context_data(**kwargs)
        print('CHECKING SELF.OBJECT INSTANCE -->',self.object)
        context['form'] = MailHeaderForm(instance = self.object)
        context['lines_formset'] = MailMergeFormset(instance = self.object)
        if self.request.POST:
            context['form'] = MailHeaderForm(self.request.POST, instance=self.object)
            context['lines_formset'] = MailMergeFormset(self.request.POST, instance=self.object)
        print('get_context_data - CONTEXT -->', context)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        with transaction.atomic():
            mail_header = form.save(commit=False)
            # mail_header.merge_header_id = get_sequenceval('cmn_mailmerge_headers_s.nextval')
            mail_header.save()

            lines_formset = context['lines_formset']
            if lines_formset.is_valid():

                for line_form in lines_formset.initial_forms:
                    line_forminstance = line_form.instance

                    # First - Ignore Blank Rows
                    if line_forminstance.merge_line_id is None:
                        print('---- Blank row detected - skipping')
                        continue

                    # Second - Delete Forms
                    if line_form in lines_formset.deleted_forms:
                        print('---- Deleting --->', line_forminstance)
                        line_forminstance.delete()

                    # Third - Update Existing Forms
                    elif line_form.has_changed():
                        print('---- Updating --->', line_forminstance)
                        data = line_form.save(commit=False)
                        # data.client_id = self.request.user.client_id
                        data.save()

                print('New Forms --->')
                for line_form in lines_formset.extra_forms:
                    line_forminstance = line_form.instance

                    # First - Ignore Blank and Deleted Rows
                    if not line_form.has_changed():
                        print('---- New blank row detected - skipping')
                        continue

                    if line_form.cleaned_data['DELETE']:
                        continue

                    # Second - Save New Forms
                    print('Cleaned Data -->',line_form.cleaned_data)
                    print('---- Form Instance --->', line_form)
                    print('---- Saving New Item --->', line_forminstance)
                    data = line_form.save(commit=False)
                    data.merge_header_id = mail_header
                    data.merge_line_id = get_sequenceval('cmn_mailmerge_lines_s.nextval')
                    print('---- Saving New Item - Model Instance --->', data)
                    data.save()
                # print('---------------------------------------------')

        return redirect('setup:mailmerge_detail', merge_header_id= mail_header.merge_header_id)
        # redirect(, )


@method_decorator(login_required, name='dispatch')
class MailMergeHeaderDeleteView(DeleteView):
    model = CmnMailmergeHeaders
    slug_field = 'merge_header_id'
    slug_url_kwarg = 'merge_header_id'
    template_name = 'mailmergetemplate/mailmergeheader-d.html'

    def get_success_url(self):
        return reverse(REVERSE)