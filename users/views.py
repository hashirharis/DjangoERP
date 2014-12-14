# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.conf import settings

from django.contrib.auth.decorators import login_required
from brutils.generic.views import JSONUpdateView, JSONDeleteView, JSONCreateView, LoginAndAdminPrivelege, JSONFormView, BRListView
from users.forms import *
from pos.forms import PaymentMethodForm
from b2b.forms import StorePaymentForm
from pos.models import PaymentMethod
from users.models import Store, StoreProfile, Staff

import json

@login_required()
def sessionConnect(request):
    if request.method == "POST":
        if 'name' in request.POST and len(request.POST['name'].strip()):
            username = request.POST['name']
            request.session['staff_id'] = Staff.objects.get(username=username, store=request.store).id
        return HttpResponse(json.dumps({'success': True}))

@login_required()
def clearSession(request):
    del request.session['staff_id']
    return HttpResponseRedirect(reverse('core:home'))

class AdminHomeView(LoginAndAdminPrivelege, TemplateView):
    template_name = "admin/settings/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(AdminHomeView, self).get_context_data(**kwargs)
        context['form'] = PaymentMethodForm(store=self.request.store)
        context['accountMethods'] = PaymentMethod.objects.all().filterReadAll(self.request.store).filter(parentMethod__pk=settings.ACCOUNTS_ID)
        context['creditCardMethods'] = PaymentMethod.objects.all().filterReadAll(self.request.store).filter(parentMethod__pk=settings.CARD_ID)
        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

#store regular CRUD
class StoreSearchView(LoginAndAdminPrivelege, BRListView):
    model = Store
    template_name = 'admin/stores/search.html'
    paginate_by = 30

    def get_queryset(self):
        from lib.queries import get_query
        #dynamic filter based on request.POST or request.GET
        stores = Store.objects.all()
        #search by simple query
        q = self.request.GET.get('q') or self.request.POST.get('q') or ''
        if len(q.strip()):
            stores = stores.filter(get_query(q, ['name', 'code']))
        self.context_append['q'] = q
        self.context_append['updateURL'] = reverse('admin:changeStoreDetails', args=[1])
        return stores.order_by('name')

    def get_context_data(self, **kwargs):
        context = super(StoreSearchView, self).get_context_data(**kwargs)
        context['form'] = StoreForm()
        context['paymentform'] = StorePaymentForm()
        return context

class StoreUpdateView(LoginAndAdminPrivelege, JSONUpdateView):
    model = Store
    form_class = StoreForm
    template_name = 'admin/settings/updateStore.html'

    def get_object(self, *args, **kwargs):
        if self.request.store.isHead:
            return super(StoreUpdateView, self).get_object(*args, **kwargs)
        else:
            return self.request.store

class StoreFinancialsUpdateView(LoginAndAdminPrivelege, JSONUpdateView):
    model = Store
    form_class = FinancialsForm
    template_name = 'admin/settings/updateStoreFinancials.html'

    def get_object(self, *args, **kwargs):
        if self.request.store.isHead:
            return super(StoreFinancialsUpdateView, self).get_object(*args, **kwargs)
        else:
            return self.request.store

    def form_valid(self, form):
        m = form.save()
        m.updateOpenToBuy()
        return HttpResponse(json.dumps({'success': True, }))
#end of store crud

#Update Store Settings
class StoreSettingsUpdateView(LoginAndAdminPrivelege, JSONUpdateView):
    model = StoreProfile
    form_class = SalesSettingsForm
    template_name = 'admin/settings/updateSaleSettings.html'

    def get_object(self, *args, **kwargs):
        return self.request.store.user.profile

#Update Privelege Settings
class StorePrivelegesUpdateView(LoginAndAdminPrivelege, JSONUpdateView):
    model = StoreProfile
    form_class = PrivelegeLevelsForm
    template_name = 'admin/settings/updatePrivelegeSettings.html'

    def get_object(self, *args, **kwargs):
        return self.request.store.user.profile

#Staff Read
class StaffListView(LoginAndAdminPrivelege, BRListView):
    model = Staff
    template_name = 'admin/staff/list.html'
    context_object_name = 'staff_list'

    def get_context_data(self, **kwargs):
        context = super(StaffListView, self).get_context_data(**kwargs)
        context['form'] = StaffForm(instance=Staff(store=self.request.store))
        return context

    def get_queryset(self):
        return Staff.objects.filter(store=self.request.store)

#Update edit (create, update, delete)
class StaffCreateView(LoginAndAdminPrivelege, JSONUpdateView):
    model = Staff
    form_class = StaffForm

    def get_object(self, *args, **kwargs):
        return Staff(store=self.request.store)

class StaffUpdateView(LoginAndAdminPrivelege, JSONUpdateView):
    model = Staff
    form_class = StaffForm
    template_name = 'admin/staff/update.html'

#Update Staff Password
class StaffResetPasswordView(LoginAndAdminPrivelege, JSONFormView):
    model = StoreProfile
    form_class = ResetPasswordForm
    template_name = 'admin/staff/changePassword.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super(StaffResetPasswordView, self).get_context_data(**kwargs)
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        context['staff'] = Staff.objects.get(pk=pk)
        return context

    def form_valid(self, form):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        staff = Staff.objects.get(pk=pk)
        staff.password = form.cleaned_data['newPassword']
        staff.save()
        return HttpResponse(json.dumps({'success': True, }))

class StaffDeleteView(LoginAndAdminPrivelege, JSONDeleteView):
    model = Staff

    def delete(self, request, *args, **kwargs):
        #called on post
        self.object = self.get_object()
        self.object.privelegeLevel = 0
        self.object.save()
        return HttpResponse(json.dumps({'success': True, }))
#Staff CRUD