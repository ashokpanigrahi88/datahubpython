from django.conf.urls import url
from django.urls import path, re_path
from enquiry.views import ( iteminsubloc, iteminloc, apinvsummary,
                            arinvsummary, costpricehist, customerdrilldown, dbnotesum, salesinvoicelines,
                            salesorderlines,salesordersum, salesorderpicklist, posum, grnsum, intratradesum,
                            reqsum, sagequery, itemcategory, itemtranshist, itemadjustment,
                            itemmovements, stktakesum, itemstatus, supplierdrilldown,invoicepdf, autto_complete)
app_name = 'enquiry'


urlpatterns = [
    re_path('^iteminsubloc/$', iteminsubloc.IteminSubLocationView.as_view(), name='iteminsublocation'),
    re_path('^iteminloc/$', iteminloc.IteminLocationView.as_view(), name='iteminlocation'),
    re_path('^apinvoicesum/$', apinvsummary.ApInvSummaryView.as_view(), name='apinvoicesum'),
    re_path('^arinvoicesum/$', arinvsummary.ArInvSummaryView.as_view(), name='arinvoicesum'),
    re_path('^costpricehist/$', costpricehist.ItemPriceHistoryView.as_view(), name='costpricehistory'),
    re_path('^customerdrilldown/$', customerdrilldown.ArCustDrilldownView.as_view(), name='customerdrilldown'),
    re_path('^dbnotesum/$', dbnotesum.ApDbnoteSumView.as_view(), name='dbnotesum'),
    re_path('^salesinvoicelines/$', salesinvoicelines.ArInvLinesView.as_view(), name='salesinvoicelines'),
    re_path('^salesorderlines/$', salesorderlines.ArOrderLinesView.as_view(), name='salesorderlines'),
    re_path('^salesordersum/$', salesordersum.ArOrderView.as_view(), name='salesordersum'),
    re_path('^salesorderpicklist/$', salesorderpicklist.ArOrderPickView.as_view(), name='salesorderpicklist'),
    re_path('^posum/$', posum.PoSumView.as_view(), name='posum'),
    re_path('^grnsum/$',grnsum.GrnSumView.as_view(), name='grnsum'),
    re_path('^intratradesum/$',intratradesum.IntraTradeSumView.as_view(), name='intratradesum'),
    re_path('^reqsum/$',reqsum.SummaryView.as_view(), name='reqsum'),
    re_path('^sagequery/$',sagequery.SummaryView.as_view(), name='sagequery'),
    re_path('^itemcategory/$',itemcategory.SummaryView.as_view(), name='itemcategory'),
    re_path('^itemtranshist/$',itemtranshist.SummmaryView.as_view(), name='itemtranshist'),
    re_path('^itemadjustment/$',itemadjustment.SummmaryView.as_view(), name='itemadjustment'),
    re_path('^itemmovements/$',itemmovements.SummaryView.as_view(), name='itemmovements'),
    re_path('^stktakesum/$',stktakesum.SummaryView.as_view(), name='stktakesum'),
    re_path('^itemstatus/$',itemstatus.SummaryView.as_view(), name='itemstatus'),
    re_path('^supplierdrilldown/$',supplierdrilldown.DrilldownView.as_view(), name='supplierdrilldown'),
    re_path('^supplierdrilldown/$',supplierdrilldown.DrilldownView.as_view(), name='supplierdrilldown'),
    url(r'^(?P<invoiceid>\d+)/pdf/$',invoicepdf.invoice_pdf,name="invoice_pdf"),
    re_path('^autoc_suppliername/$',autto_complete.autoc_suppliername, name='autoc_suppliername'),
    #url(r'^picksalesorder/$', apinvoicesum.AP.as_view(), name='picksalesorder'),
]
