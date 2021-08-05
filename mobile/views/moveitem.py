from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from mobile.forms import MoveItemToPrimayForm
from inventory import locationutil as locationutil


# specific to this view


@method_decorator(login_required, name='dispatch')
class MoveToPrimaryView(FormView):
    template_name = 'mobile/moveitem.html'
    form_class = MoveItemToPrimayForm
    context_object_name = 'form'
    initial_dict = {
        "title": "My New Title",
        "description": " A New Description",
        "available": True,
        "email": "abc@gmail.com"
    }
    itemdict = {}
    success_url = "/mobile/moveitem/"

    def get(self, request, *args, **kwargs):
        return super(MoveToPrimaryView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        pass

    def get_context_data(self, **kwargs):
        context = super(MoveToPrimaryView, self).get_context_data(**kwargs)
        page = self.request.GET.get('page')
        userid = self.request.user.user_id
        items = None
        item = None
        businessunit = self.request.user.bu_id
        context['businessunit'] = businessunit
        context['itemdict'] = self.itemdict
        context['rows'] = items
        context['item'] = item
        return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # perform a action here
        context = self.get_context_data(**kwargs)
        userid = self.request.user.user_id
        movementtype = 'INTERNALTOINTERNAL'
        itemnumber = form.cleaned_data['item_number']
        fromsublocation = form.cleaned_data['from_sub_location']
        quantity = form.cleaned_data['quantity']
        tosublocation = form.cleaned_data['to_sub_location']
        fromlocationid = sessionfunc.get_location_id(self.request)
        tolocationid = sessionfunc.get_location_id(self.request)
        message = locationutil.move_item(movementtype,userid, itemnumber,
                                        fromlocationid, fromsublocation,
                                        quantity, tolocationid, tosublocation)
        if message == 'OK':
            self.itemdict['successmessage'] = 'Item {0} moved from {1} to {2} successfully {3}'.format(
                itemnumber, fromsublocation, tosublocation, quantity )
        else:
            self.itemdict['errormessage'] = message
            self.form_invalid(form)
        context['itemdict'] = self.itemdict
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
