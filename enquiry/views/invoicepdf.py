#-*- coding: UTF-8 -*-
from __future__ import unicode_literals
try:
    from io import StringIO, BytesIO
except ImportError:
  from io  import StringIO, BytesIO
from xhtml2pdf import pisa
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from common.models import ArInvoiceHeaders, ArInvoiceLines

def invoice_pdf(request , invoiceid):
    header = get_object_or_404(ArInvoiceHeaders,invoice_header_id=invoiceid)
    lines = ArInvoiceLines.objects.filter(invoice_header_id__invoice_header_id=invoiceid)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"]= "attachment: " \
        "filename=%s_%s.pdf" % ('INV', invoiceid)
    print(response)
    html = render_to_string("enquiry/invoice_pdf.html", {
        "header": header,
        "lines": lines,
        "MEDIA_ROOT": settings.MEDIA_ROOT,
        "STATIC_ROOT": settings.STATIC_PATH,
    })
    print(html)
    print(settings.MEDIA_ROOT, settings.STATIC_PATH)
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')),
                            response,
                            encoding="UTF-8",)
    print(pdf)
    return response
