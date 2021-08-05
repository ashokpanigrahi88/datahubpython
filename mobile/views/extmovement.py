from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from mobile.forms import ExtMovementForm
from inventory import locationutil as locationutil
from common import (sessionfunc, commonutil, dbfuncs)


# specific to this view


REVERSE = 'mobile:extmovement'

@method_decorator(login_required, name='dispatch')
class ExtMovementView(FormView):
    template_name = 'mobile/extmoveitem.html'
    form_class = ExtMovementForm
    context_object_name = 'form'
    itemdict = {}
    success_url = "/mobile/extmovement/"


    def get(self, request, *args, **kwargs):
        return super(ExtMovementView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        return self.form_invalid(form, **kwargs)

    def get_initial(self):
        tosublocation =  dbfuncs.get_primarysubloc('PRIMARY GRN', self.request.user.location_id)
        print('initial')
        return {'to_sub_location': tosublocation}

    def get_form_kwargs(self):
        kwargs = super(ExtMovementView, self).get_form_kwargs()
        kwargs['hiddenfields'] =  ['to_sub_location']
        print('1', kwargs)
        return kwargs

    def get_queryset(self):
        pass

    def get_success_url(self):
        return reverse(REVERSE)

    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        locationid = sessionfunc.getset_sessionval(self.request, 'locationid', None,self.request.user.location_id)
        page = self.request.POST.get('page')
        userid = self.request.user.user_id
        # self.form_class['to_sub_location'].   to_sub_location(initial='GRN STAGING')
        context = super(ExtMovementView , self).get_context_data(**kwargs)
        items = None
        item = None
        businessunit = self.request.user.bu_id
        context['businessunit'] = businessunit
        userid = self.request.user.user_id
        movementtype =  self.request.POST.get('movementtype')
        itemnumber =  self.request.POST.get('item_number')
        fromsublocation =  self.request.POST.get('from_sub_location')
        quantity =  self.request.POST.get('quantity')
        tosublocation =  self.request.POST.get('to_sub_location')
        fromlocationid = sessionfunc.get_location_id(self.request)
        tolocationid = sessionfunc.get_location_id(self.request)
        if commonutil.hasstrvalue(itemnumber):
            if not commonutil.hasstrvalue(tosublocation):
                tosublocation = dbfuncs.get_primarysubloc('PRIMARY GRN', tolocationid)
            message = locationutil.move_item(movementtype,userid, itemnumber,
                                            fromlocationid, fromsublocation,
                                            int(quantity), tolocationid, tosublocation)
            if message == 'OK':
                self.itemdict['successmessage'] = 'Item {0} moved from {1} to {2} successfully {3}'.format(
                    itemnumber, fromsublocation, tosublocation, quantity )
            else:
                self.itemdict['errormessage'] = message
        context['itemdict'] = self.itemdict
        return context

