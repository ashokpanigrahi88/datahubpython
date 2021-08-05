from django.db.models import F
from django.http import request, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.http import HttpResponse
from common.models import InvItemMasters, ArInvoiceHeaders
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import TruncMonth

from django import forms

def handle_uploaded_file(f):
    with open('/oratech/local/uploads/uploadedfile.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


time_threshold = timezone.now() - timedelta(days=400)
def get_category_count(request):
    labels = []
    data = []

    queryset = InvItemMasters.objects.annotate(category=F('iic_category_id__category_name')
                                               ).values('category').annotate(totalcount=Count('item_id')
                                                                             ).order_by('-totalcount')[:20]
    for row in queryset:
        labels.append(row['category'][:20])
        data.append(row['totalcount'])

    return labels , data

def get_top_customers(request):
    labels = []
    data = []

    queryset = ArInvoiceHeaders.objects.filter(invoice_status_date__gt=time_threshold).annotate(customer=F('customer_id__customer_name')
                                               ).values('customer').annotate(total=Sum('net_total')
                                                                             ).order_by('-total')[:20]
    for row in queryset:
        labels.append(row['customer'][:20])
        data.append(int(row['total']))

    return labels , data

def get_top_suppliers(request):
    labels = []
    data = []

    queryset = PoGrnHeaders.objects.filter(grn_date__gt=time_threshold).filter(net_total__gt=0).annotate(supplier=F('sup_supplier_id__supplier_name')
                                               ).values('supplier').annotate(total=Sum('net_total')
                                                                             ).order_by('-total')[:20]
    for row in queryset:
        labels.append(row['supplier'][:20])
        data.append(int(row['total']))

    return labels , data

def get_top_items(request):
    labels = []
    data = []

    queryset = ArInvoiceLines.objects.filter(invoice_line_status_date__gt=time_threshold).annotate(item=F('item_name')
                                               ).values('item').annotate(total=Sum('net_total_after_discount')
                                                                             ).order_by('-total')[:20]
    for row in queryset:
        labels.append(row['item'][:20])
        data.append(int(row['total']))

    return labels , data

def get_last12months(request):
    labels = []
    data = []

    queryset = ArInvoiceLines.objects.filter(invoice_line_status_date__gt=time_threshold
                        ).annotate(month=TruncMonth('invoice_line_status_date')
                                   ).values('month').annotate(total=Sum('net_total_after_discount')
                                                                             ).order_by('month')[:20]
    for row in queryset:
        labels.append(row['month'].strftime("%Y-%m"))
        data.append(int(row['total']))

    return labels , data
# specific to this view

from common.forms import *
from common.models import *

app_name = 'common'

# Create your views here.
PUB_PAGE_LINES = 15

def error_404_view(request, exception):
    data = {"name": "Oratech Solutions Limited"}
    return render(request,'common/error_404.html', data)


def index(request):
    return HttpResponse("You're at the Home page of Oratech Solutions Limited: error 404.")

@method_decorator(login_required, name='dispatch')
class MainView(ListView):
    template_name = 'common/main.html'
    context_object_name = 'data'
    fieldheader = """<th>ID</th>
        <th>Name</th>
        <th>Email</th>
        <th>Fullnamne</th>
        <th>Description</th>
        <th>Active</th>
        <th>Actions</th>"""

    def get(self, request, *args, **kwargs):
        request.session['mystring'] = 'Ashok'
        return super(MainView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        orders = ArSalesorderHeaders.objects.all().count()
        return orders

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        businessunit = CmnBusinessUnits.objects.filter(bu_id=self.request.user.bu_id)
        context['fields'] = self.fieldheader
        context['businessunit'] = businessunit
        self.request.session['bu_id'] = businessunit[0].bu_id
        self.request.session['bu_name'] = businessunit[0].bu_name
        location = InvLocations.objects.filter(location_id=self.request.user.location_id)
        context['location'] = location
        context['labels'], context['data'] = get_category_count(self.request)
        context['custlabels'], context['custdata'] = get_top_customers(self.request)
        context['suplabels'], context['supdata'] = get_top_suppliers(self.request)
        context['itemlabels'], context['itemdata'] = get_top_items(self.request)
        context['monthlabels'], context['monthdata'] = get_last12months(self.request)
        context['uploadfile'] = UploadFileForm()
        return context


@method_decorator(login_required, name='dispatch')
class UserListView(ListView):
    model = CmnUsers
    template_name = 'common/list_users.html'
    context_object_name = 'data'
    ordering = ('user_name')
    paginate_by = PUB_PAGE_LINES
    fieldheader = """<th>ID</th>
        <th>Name</th>
        <th>Email</th>
        <th>Fullnamne</th>
        <th>Description</th>
        <th>Active</th>
        <th>Actions</th>"""

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        rows = self.get_queryset()
        f_nm = self.request.GET.get('nm')
        page = self.request.GET.get('page')
        if f_nm is not None:
            rows = rows.filter(user_name__icontains=f_nm)
        paginator = Paginator(rows, self.paginate_by)
        try:
            rows = paginator.page(page)
        except PageNotAnInteger:
            rows = paginator.page(1)
        except EmptyPage:
            rows = paginator.page(paginator.num_pages)
        context['rows'] = rows
        context['request'] = self.request
        context['fields'] = self.fieldheader
        return context


class UserCreateView(CreateView):
    model = CmnUsers
    form_class = UserCreationForm
    template_name = 'common/user-c.html'

    def get_success_url(self):
        return reverse('common:listusers')


class UserDetailView(DetailView):
    model = CmnUsers
    slug_field = "user_id"
    slug_url_kwarg = "user_id"
    fields = CmnUsers.fieldlist()
    template_name = 'common/user-d.html'
    context_object_name = 'form'

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['fields'] = self.fields
        return context

    def get_success_url(self):
        return reverse('common:listusers')

    def get_object(self, queryset=None):
        obj = super(UserDetailView, self).get_object(queryset=queryset)
        return obj


class UserUpdateView(UpdateView):
    model = CmnUsers
    slug_field = "user_id"
    slug_url_kwarg = "user_id"
    fields = CmnUsers.fieldlist()
    template_name = 'common/user-u.html'
    context_object_name = 'form'

    def get_success_url(self):
        return reverse('common:listusers')


class UserDeleteView(DeleteView):
    slug_field = "user_id"
    slug_url_kwarg = "user_id"
    model = CmnUsers
    template_name = 'common/confirm_delete.html'

    def get_success_url(self):
        return reverse('common:listusers')