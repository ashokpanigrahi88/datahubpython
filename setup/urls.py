
from django.urls import path, re_path
from setup.views import (cmnlanguages_views, cmnsysoptions_views, lookup_views,
                         lookupcode_views, businessunits_views, banks_views,
                         )
from setup.templates.companies import companies_views
from setup.templates.commodities import commodities_views2 as commodities_views

### AFTER MOVING all views.py files from templates folder to views folder, move the below imports into brackets above
from setup.templates.containers import containers_views
from setup.templates.countries import countries_views
from setup.templates.currencies import currencies_views
from setup.templates.currencyrates import currencyrates_views
from setup.templates.gl_accounts import glaccounts_views
from setup.templates.mailmergetemplate import mailmerge_views
from setup.templates.payment_methods import payment_method_views
from setup.templates.payment_terms import payment_terms_views
from setup.templates.reasons import reasons_views
from setup.templates.tax_codes import tax_codes_views
from setup.templates.terms_conditions import terms_conditions_views
from setup.templates.units_of_measurement import uom_views

app_name = 'setup'

urlpatterns = [
    path('cmnsysoptions_create/', cmnsysoptions_views.CmnSysOptionsCreateView.as_view(), name='cmnsysoptions_create'),
    path('cmnsysoptions_list/', cmnsysoptions_views.CmnSysOptionsListView.as_view(), name='cmnsysoptionslistview'),
    path('cmnsysoptions_detail/<int:sys_options_id>/', cmnsysoptions_views.CmnSysOptionsDetailView.as_view(), name='cmnsysoptions_detail'),
    path('cmnsysoptions_update/<int:sys_options_id>/', cmnsysoptions_views.CmnSysOptionsUpdateView.as_view(), name='cmnsysoption_update'),
    path('cmnsysoptions_delete/<int:sys_options_id>/', cmnsysoptions_views.CmnSysOptionsDeleteView.as_view(), name='cmnsysoption_delete'),
    path('lookup_list/', lookup_views.CmnLookupTypesListView.as_view(), name='lookups_list'),
    path('lookup_create/', lookup_views.CmnLookupTypesCreateView.as_view(), name='cmnsysoption_create'),
    path('lookup_detail/<str:lookup_type>/', lookup_views.CmnLookupTypesDetailView.as_view(), name='lookups_detail'),
    path('lookup_update/<str:lookup_type>/', lookup_views.CmnLookupTypesUpdateView.as_view(), name='lookup_update'),
    path('languages_list/', cmnlanguages_views.LanguagesListView.as_view(), name='languages_list'),
    path('language_update/<str:language_code>/', cmnlanguages_views.LanguagesUpdateView.as_view(), name='language_update'),
    path('language_delete/<str:language_code>/', cmnlanguages_views.LanguagesDeleteView.as_view(), name='language_delete'),
    path('language_create/', cmnlanguages_views.LanguagesCreateView.as_view(), name='language_create'),
    re_path('^lookupcodes_list/$', lookupcode_views.LookupCodeListView.as_view(), name='lookupcodes_list'),
    path('lookupcode_update/<str:lookup_type>/<str:lookup_code>/', lookupcode_views.LookupCodeUpdateView.as_view(), name='lookupcode_update'),
    path('lookupcode_create/', lookupcode_views.LookupCodeCreateView.as_view(), name='lookupcode_create'),
    path('banks_list/', banks_views.BanksListView, name='banks_list'),
    path('banks_delete/<int:bank_id>/', banks_views.BanksDeleteView.as_view(), name='banks_delete'),
    path('bankaccounts_delete/<int:bank_account_id>/', banks_views.BankAccountsDeleteView.as_view(), name='bankaccounts_delete'),
    ### Companies
    path('company_list/', companies_views.CompaniesListView.as_view(), name='companies_list'),
    path('company_create/', companies_views.CompaniesCreateView.as_view(), name='companies_create'),
    path('company_update/<str:comp_id>/', companies_views.CompaniesUpdateView.as_view(), name='companies_update'),
    path('company_delete/<str:comp_id>/', companies_views.CompaniesDeleteView.as_view(), name='companies_delete'),
    ### BusinessUnits
    path('bu_list/', businessunits_views.BusinessUnitsListView.as_view(), name='businessunits_list'),
    path('bu_create/', businessunits_views.BusinessUnitsCreateView.as_view(), name='businessunits_create'),
    path('bu_update/<str:bu_id>/', businessunits_views.BusinessUnitsUpdateView.as_view(), name='businessunits_update'),
    path('bu_delete/<str:bu_id>/', businessunits_views.BusinessUnitsDeleteView.as_view(), name='businessunits_delete'),
    ### COMMODITIES
    path('commcode_list/', commodities_views.CommodityCodesListView.as_view(), name='commoditycodes_list'),
    path('commoditycodes_create/', commodities_views.CommodityCodesCreateView.as_view(), name='commoditycodes_create'),
    path('commoditycodes_update/<str:ccc_id>/', commodities_views.CommodityCodesUpdateView.as_view(), name='commoditycodes_update'),
    path('commoditycodes_delete/<str:ccc_id>/', commodities_views.CommodityCodesDeleteView.as_view(), name='commoditycodes_delete'),
    path('commodityrates_create/', commodities_views.CommodityRatesCreateView.as_view(), name='commodityrates_create'),
    path('commodityrates_update/<str:ccr_id>/', commodities_views.CommodityRatesUpdateView.as_view(), name='commodityrates_update'),
    path('commodityrates_delete/<str:ccr_id>/', commodities_views.CommodityRatesDeleteView.as_view(), name='commodityrates_delete'),
    ### Containers
    path('containers_list/', containers_views.ContainersListView.as_view(), name='containers_list'),
    path('containers_create/', containers_views.ContainersCreateView.as_view(), name='containers_create'),
    path('containers_update/<str:pc_id>/', containers_views.ContainersUpdateView.as_view(), name='containers_update'),
    path('containers_delete/<str:pc_id>/', containers_views.ContainersDeleteView.as_view(), name='containers_delete'),
    ### Countries
    path('countries_list/', countries_views.CountryListView.as_view(), name='countries_list'),
    path('countries_create/', countries_views.CountryCreateView.as_view(), name='countries_create'),
    path('countries_update/<str:country_code>/', countries_views.CountryUpdateView.as_view(), name='countries_update'),
    path('countries_delete/<str:country_code>/', countries_views.CountryDeleteView.as_view(), name='countries_delete'),
    ### Currencies
    path('currencies_list/', currencies_views.CurrencyListView.as_view(), name='currencies_list'),
    path('currencies_create/', currencies_views.CurrencyCreateView.as_view(), name='currencies_create'),
    path('currencies_update/<str:currency_code>/', currencies_views.CurrencyUpdateView.as_view(), name='currencies_update'),
    path('currencies_delete/<str:currency_code>/', currencies_views.CurrencyDeleteView.as_view(), name='currencies_delete'),
    ### CurrencyRates
    path('currencyrates_list/', currencyrates_views.CurrencyRateListView.as_view(), name='currencyrates_list'),
    path('currencyrates_create/', currencyrates_views.CurrencyRateCreateView.as_view(), name='currencyrates_create'),
    path('currencyrates_update/<str:from_currency_code>/<str:to_currency_code>/', currencyrates_views.CurrencyRateUpdateView.as_view(), name='currencyrates_update'),
    path('currencyrates_delete/<str:from_currency_code>/<str:to_currency_code>/', currencyrates_views.CurrencyRateDeleteView.as_view(), name='currencyrates_delete'),
    ### GL Account Codes
    path('glcategories/', glaccounts_views.GlCategoryListView, name='glcategories'),
    path('glcodes_list/', glaccounts_views.GLAccountCodesListView.as_view(), name='glcodes_list'),

    path('glcodes_list/glaccountcode_create/',glaccounts_views.GlAccountCodesCreateView.as_view(), name='glaccountcode_create'),
    path('glaccountcode_update/<str:gl_account_id>/', glaccounts_views.GlAccountCodesUpdateView.as_view(),name='glaccountcode_update'),
    path('glcategory_delete/<str:gl_category_id>/', glaccounts_views.GlCategoryDeleteView.as_view(),name='glcategory_delete'),
    path('glsubcategory_delete/<str:gl_sub_category_id>/', glaccounts_views.GlSubCategoryDeleteView.as_view(), name='glsubcategory_delete'),
    path('glaccountcode_delete/<str:gl_account_id>/', glaccounts_views.GlAccountCodeDeleteView.as_view(), name='glaccountcode_delete'),
    ### MailMergeTemplates
    path('mailmerge_list/', mailmerge_views.MailMergeListView.as_view(), name='mailmerge_list'),
    path('mailmerge/new_header/', mailmerge_views.MailMergeLinesFormsetCreateView.as_view(),name='mailmergelines_create_formset'),
    path('mailmerge_detail/header-<str:merge_header_id>/', mailmerge_views.MailMergeDetailView.as_view(), name='mailmerge_detail'),
    path('mailmerge/header-<str:merge_header_id>/edit/',mailmerge_views.MailMergeLinesFormsetUpdateView.as_view(), name='mailmergelines_update_formset'),
    path('mailmerge/deleteheader-<str:merge_header_id>/', mailmerge_views.MailMergeHeaderDeleteView.as_view(), name='mailmergeheader_delete'),
    ### Payment Methods
    path('pmntmentod_list/', payment_method_views.PaymentMethodsListView.as_view(), name='paymentmethods_list'),
    path('paymentmethods_create/', payment_method_views.PaymentMethodsCreateView.as_view(),
         name='paymentmethods_create'),
    path('paymentmethods_update/<str:pmnt_method_id>/', payment_method_views.PaymentMethodsUpdateView.as_view(),
         name='paymentmethods_update'),
    path('paymentmethods_delete/<str:pmnt_method_id>/', payment_method_views.PaymentMethodsDeleteView.as_view(),
         name='paymentmethods_delete'),
    ### Payemnt Terms
    path('pmntterms_list/', payment_terms_views.PaymentTermsListView.as_view(), name='paymentterms_list'),
    path('paymentterms_create/', payment_terms_views.PaymentTermsCreateView.as_view(),
         name='paymentterms_create'),
    path('paymentterms_update/<str:cpt_id>/', payment_terms_views.PaymentTermsUpdateView.as_view(),
         name='paymentterms_update'),
    path('paymentterms_delete/<str:cpt_id>/', payment_terms_views.PaymentTermsDeleteView.as_view(),
         name='paymentterms_delete'),
    path('paymentterms_breakup_create/', payment_terms_views.PaymentTermBreakupCreateView.as_view(),
         name='paymentterms_breakup_create'),
    path('paymentterms_breakup_update/<str:cpb_id>/', payment_terms_views.PaymentTermBreakupUpdateView.as_view(),
         name='paymentterms_breakup_update'),
    path('paymentterms_breakup_delete/<str:cpb_id>/', payment_terms_views.PaymentTermBreakupDeleteView.as_view(),
         name='paymentterms_breakup_delete'),
    ### Reasons
    path('reasons_list/', reasons_views.ReasonsListView.as_view(), name='reasons_list'),
    path('reasons_create/', reasons_views.ReasonsCreateView.as_view(), name='reasons_create'),
    path('reasons_update/<str:reason_code_id>/', reasons_views.ReasonsUpdateView.as_view(), name='reasons_update'),
    path('reasons_delete/<str:reason_code_id>/', reasons_views.ReasonsDeleteView.as_view(), name='reasons_delete'),
    ### Tax Codes
    path('taxcodes_list/', tax_codes_views.TaxCodesListView.as_view(), name='taxcodes_list'),
    path('taxcodes_create/', tax_codes_views.TaxCodesCreateView.as_view(),
         name='taxcodes_create'),
    path('taxcodes_update/<str:tax_code_id>/', tax_codes_views.TaxCodesUpdateView.as_view(),
         name='taxcodes_update'),
    path('taxcodes_delete/<str:tax_code_id>/', tax_codes_views.TaxCodesDeleteView.as_view(),
         name='taxcodes_delete'),
    path('taxcodes_breakup_create/', tax_codes_views.TaxBreakupsCreateView.as_view(),
         name='taxcodes_breakup_create'),
    path('taxcodes_breakup_update/<str:ctb_id>/', tax_codes_views.TaxBreakupsUpdateView.as_view(),
         name='taxcodes_breakup_update'),
    path('taxcodes_breakup_delete/<str:ctb_id>/', tax_codes_views.TaxBreakupsDeleteView.as_view(),
         name='taxcodes_breakup_delete'),
    ### Terms And Conditions
    path('termcond_list/', terms_conditions_views.TNCListView.as_view(), name='terms_list'),
    path('tnc_create/', terms_conditions_views.TNCCreateView.as_view(), name='terms_create'),
    path('tnc_update/<str:tc_code_id>/', terms_conditions_views.TNCUpdateView.as_view(), name='terms_update'),
    path('tnc_delete/<str:tc_code_id>/', terms_conditions_views.TNCDeleteView.as_view(), name='terms_delete'),
    ### Units of Measurement
    path('uom_list/', uom_views.UoMListView.as_view(), name='uom_list'),
    path('uom_create/', uom_views.UoMCreateView.as_view(), name='uom_create'),
    path('uom_update/<str:uom_id>/', uom_views.UoMUpdateView.as_view(), name='uom_update'),
    path('uom_delete/<str:uom_id>/', uom_views.UoMDeleteView.as_view(), name='uom_delete'),
]

