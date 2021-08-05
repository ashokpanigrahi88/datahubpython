from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from mobile.forms import AddToBatchForm
from inventory import (locationutil, itemutil)
from common import (commonutil, dbfuncs, querydict)


# specific to this view

REVERSE = 'mobile:additemtobatch'

@method_decorator(login_required, name='dispatch')
class AddItemToBatchView(FormView):
    template_name = 'mobile/additemtobatch.html'
    form_class = AddToBatchForm
    context_object_name = 'form'
    rows = None
    MYCONTEXT = {}
    success_url = "/mobile/additemtobatch/"
    batchid  = 1

    def get(self, request, *args, **kwargs):
        return super(AddItemToBatchView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        pass

    def get_initial(self):
        initial =  {'item_number': "",
                    }
        print('inital:', initial)
        return initial

    def get_form_kwargs(self):
        kwargs = super(AddItemToBatchView, self).get_form_kwargs()
        kwargs['hiddenfields'] = []
        if commonutil.hasstrvalue(self.request.POST.get('batch_name')):
            kwargs['hiddenfields'] =  ['batch_name']
        return kwargs

    def get_queryset(self):
        pass

    def get_success_url(self):
        return reverse(REVERSE)

    def get_context_data(self, **kwargs):
        context = super(AddItemToBatchView, self).get_context_data(**kwargs)
        page = self.request.GET.get('page')
        userid = self.request.user.user_id
        businessunit = self.request.user.bu_id
        context['businessunit'] = businessunit
        commonutil.debugmessage('In context','Get batch lines')
        print(self.batchid)
        sql = """ Select Item_Id, Item_Number, Item_Name , Batch_ID
                From Inv_Item_BATCH_LINES_VA
                Where Batch_ID = {}""".format((self.batchid))
        # self.rows = dbfuncs.exec_sql(sql)
        self.rows , self.tableheader, self.tablecolumns = querydict.get_rowset(querydict.Q_GETBATCHITEMS,[self.batchid])
        print(self.batchid, self.rows)
        context['MYCONTEXT'] = self.MYCONTEXT
        context['rows'] = self.rows
        context['rows_tableheader'] = self.tableheader
        context['rows_tablecolumns'] = self.tablecolumns
        return context

    def form_valid(self, form, **kwargs):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # perform a action here
        context = self.get_context_data(**kwargs)
        userid = self.request.user.user_id
        itemnumber = form.cleaned_data['item_number']
        batchname = form.cleaned_data['batch_name']
        self.batchid , message = itemutil.add_itemtobatch(p_batchname=batchname, p_itemnumber=itemnumber,p_userid=userid)
        commonutil.debugmessage(self.batchid,'2a')
        if not commonutil.hasintnonaerovalue(self.batchid):
            self.MYCONTEXT['errormessage'] = message
            self.form_invalid(form)
        else:
            self.MYCONTEXT['successmessage'] = message
        return super().form_invalid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
