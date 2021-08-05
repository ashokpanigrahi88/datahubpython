from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView
from django.core.paginator import Paginator

# specific to this view
from common.sysutil import get_sequenceval
from setup.forms.banks_forms import *
from common.models import CmnBanks, CmnBankAccounts, GlAccountCodes

APPNAME = 'setup'
URLPREFIX = '/' + APPNAME + '/banks{0}/'
SLUG_FIELD = 'bank_id'
SLUG_URL_KWARG = 'bank_id'
TEMPLATE_PREFIX = 'setup/cmnbanks-{0}.html'
ORDERING = ('bank_id',)
# FORM_CLASS = LookupCodeForm
MODEL = CmnBanks
# REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "setup:banks_list"
MYCONTEXT = {
    'create': URLPREFIX.format('_create'),
    'update': URLPREFIX.format('_update'),
    'delete': URLPREFIX.format('_delete'),
    'list': URLPREFIX.format('_list'),
    'title': 'Banks List',
    'findfield': 'Bank Name',
             }


@login_required
def BanksListView(request):
    print('REQUEST - GET --->', request.GET)
    print('REQUEST - POST --->',request.POST)
    context={}
    context['MYCONTEXT'] = MYCONTEXT
    context['rows'] = CmnBanks.objects.all()
    account_field_list = ['bank_account_id', 'branch_acctname', 'currency_code', 'bank_branch_city', 'country_code', 'branch_post_code', 'gac_gl_account_id']
    context['account_field_list'] = account_field_list


    ### PAGINATION
    if len(context['rows'])>6:
        paginator = Paginator(context['rows'], 6)  # Show 25 contacts per page.
        page_number = request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)

    if request.GET.get('bank_id'):
        # print('DETAIL POST REQUEST ---------->', request.GET)
        bank_id = request.GET.get('bank_id')
        account_details = CmnBankAccounts.objects.filter(cb_bank_id=bank_id)
        context['account_details'] = account_details

    elif 'add_new_bank' in request.GET:
        context['banks_form'] = BanksForm()
        # context['bankaccounts_form'] = BankAccountsForm()

    elif 'edit_bank_id' in request.GET:
        bank_id = request.GET.get('edit_bank_id')
        bank = get_object_or_404(CmnBanks, bank_id=bank_id)
        banks_form = BanksForm(instance=bank)
        context['banks_form'] = banks_form

    if 'save_bank_form' in request.POST:
        print('BANK FORM POSTREQUEST ---------->',request.POST)

        if 'edit_bank_id' in request.GET:
            bank_id = request.GET.get('edit_bank_id')
            bank = CmnBanks.objects.get(bank_id=bank_id)
            banks_form = BanksForm(request.POST, instance=bank)
            banks_form.save()
            return redirect('/setup/banks_list/?bank_id={0}'.format(bank_id))

        else:
            bank_form_instance = BanksForm(request.POST)
            bank_instance = bank_form_instance.save(commit=False)
            bank_instance.bank_id = get_sequenceval('cmn_banks_s.nextval')
            print('Bank Instance - ', bank_instance)
            bank_instance.save()

            return redirect('/setup/banks_list/?bank_id={0}'.format(bank_instance.bank_id))

    if 'add_new_bank_account' in request.GET:
        bank_id = request.GET.get('bank_id')
        bank = CmnBanks.objects.get(bank_id=bank_id)
        initial_values = {'cb_bank_id':bank}
        context['bankaccounts_form'] = BankAccountsForm(initial=initial_values)

    if 'edit_bank_account_id' in request.GET:
        bank_id = request.GET.get('bank_id')
        bank = CmnBanks.objects.get(bank_id=bank_id)
        bank_account_id = request.GET.get('edit_bank_account_id')
        bank_account = get_object_or_404(CmnBankAccounts, bank_account_id=bank_account_id)
        bankaccounts_form = BankAccountsForm(instance=bank_account)
        context['bankaccounts_form'] = bankaccounts_form

    if 'save_bankaccount_form' in request.POST:
        print('BANK FORM POSTREQUEST ---------->', request.POST)

        if 'edit_bank_account_id' in request.GET:
            account_id = request.GET.get('edit_bank_account_id')
            bank_account = get_object_or_404(CmnBankAccounts, bank_account_id=account_id)
            bankaccount_form = BankAccountsForm(request.POST, instance=bank_account)
            bankaccount_form.save()
            return redirect('/setup/banks_list/?bank_id={0}'.format(bank_account.cb_bank_id.bank_id))

        else:
            bank_id = request.GET.get('bank_id')
            bank = CmnBanks.objects.get(bank_id=bank_id)
            bankaccount_form_instance = BankAccountsForm(request.POST)
            bankaccount_instance = bankaccount_form_instance.save(commit=False)
            bankaccount_instance.cb_bank_id = bank
            bankaccount_instance.bank_id = get_sequenceval('cmn_bank_accounts_s.nextval')
            bankaccount_instance.save()
            return redirect('/setup/banks_list/?bank_id={0}'.format(bank_id))

    return render(request, TEMPLATE_PREFIX.format('l'), context)


@method_decorator(login_required, name='dispatch')
class BanksDeleteView(DeleteView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    template_name = TEMPLATE_PREFIX.format('del')
    context_object_name = 'object'

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class BankAccountsDeleteView(DeleteView):
    model = CmnBankAccounts
    slug_field = 'bank_account_id'
    slug_url_kwarg = 'bank_account_id'
    template_name = 'setup/cmnbankaccounts-del.html'
    context_object_name = 'object'

    def get_success_url(self):
        return reverse(REVERSE)
