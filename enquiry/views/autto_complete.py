from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from common.models import (ApSuppliers)


def autoc_suppliername(request):
    if request.GET.get('q'):
        q = request.GET['q']
        data = ApSuppliers.objects.filter(supplier_name__startswith=q).values_list('supplier_name', flat=True)
        json = list(data)
        return JsonResponse(json, safe=False)
    else:
        HttpResponse("No cookies")