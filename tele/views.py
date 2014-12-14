from brutils.generic.views import LoginRequiredMixin, BRListView, StoreLevelObjectMixin
from django.views.generic import TemplateView, DetailView
from core.models import Brand
from users.models import Store
from django.views.generic import CreateView, UpdateView
from tele.models import AddressbookContact, BrandAddressbookContact
from tele.forms import ContactForm, BrandContactForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from users.models import Staff
from django.shortcuts import get_object_or_404


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "tele/teledexHome.html"


class StoreSearchMixin(object):
    def doSearchFilters(self, stores):
        params = {}
        q = self.request.GET.get('q') or self.request.POST.get('q') or ''
        if len(q.strip()):
            stores = stores.search(['name'], q)
        params['q'] = q
        self.context_append['params'] = params
        return stores.order_by('name')[:300]

    def doLocalContactsSearchFilters(self, contacts):
        params = {}
        q = self.request.GET.get('q') or self.request.POST.get('q') or ''
        if len(q.strip()):
            contacts = contacts.search(['name'], q)
        params['q'] = q
        self.context_append['params'] = params
        return contacts.order_by('name')[:300]

    def doBrandSearchFilters(self, brands):
        params = {}
        q = self.request.GET.get('q') or self.request.POST.get('q') or ''
        if len(q.strip()):
            brands = brands.search(['brand'], q)
        params['q'] = q
        self.context_append['params'] = params

        if self.request.GET.getlist('individualAccount') or self.request.POST.getlist('individualAccount') or []:
            individualAccount = self.request.GET.getlist('individualAccount') or self.request.POST.getlist('individualAccount') or []
            brands = brands.filter(purchaser__in=individualAccount)
        if self.request.GET.getlist('headOfficePreferred') or self.request.POST.getlist('headOfficePreferred') or []:
            headOfficePreferred = self.request.GET.getlist('headOfficePreferred') or self.request.POST.getlist('headOfficePreferred') or []
            brands = brands.filter(isHOPreferred__in=headOfficePreferred)
        return brands.order_by('brand')[:300]


class BrandLookupView(LoginRequiredMixin, BRListView, StoreSearchMixin):
    model = Brand
    template_name = 'tele/search.html'
    #paginate_by = 30
    context_object_name = 'searchResults'
    queryset = Brand.objects.all()

    def get_queryset(self):
        #dynamic filter based on request.POST or request.GET
        brands = Brand.objects.filter()
        return super(BrandLookupView, self).doBrandSearchFilters(brands)

    def get_context_data(self, **kwargs):
        context = super(BrandLookupView, self).get_context_data(**kwargs)
        context['brandSearch'] = True
        return context


class BrandDetailView(LoginRequiredMixin, DetailView):
    model = Brand
    template_name = 'tele/view.html'

    def get_context_data(self, **kwargs):
        context = super(BrandDetailView, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk') or self.request.GET.get('pk') or self.request.POST.get('pk') or ''
        brandAddressbookContact = BrandAddressbookContact.objects.all().filterReadAll(self.request.store).filter(isShared=False, brand_id=pk)
        context['brandAddressbookContact'] = brandAddressbookContact
        context['isBrand'] = True
        brand_obj = Brand.objects.filter(pk=pk)  # get related brands
        distributors = Brand.objects.filter(distributor=brand_obj[0].distributor)
        context['distributors'] = distributors
        return context


class StoreLookupView(LoginRequiredMixin, BRListView, StoreSearchMixin):
    model = Store
    template_name = 'tele/search.html'
    #paginate_by = 30
    context_object_name = 'searchResults'
    queryset = Store.objects.all()

    def get_queryset(self):
        #dynamic filter based on request.POST or request.GET
        stores = Store.objects.filter()
        #paginatedStores = paginate_queryset(stores, self.request.GET.get('page'))
        return super(StoreLookupView, self).doSearchFilters(stores)

    def get_context_data(self, **kwargs):
        context = super(StoreLookupView, self).get_context_data(**kwargs)
        context['storeSearch'] = True
        return context


class StoreDetailView(LoginRequiredMixin, DetailView):
    model = Store
    template_name = 'tele/view.html'

    def get_context_data(self, **kwargs):
        context = super(StoreDetailView, self).get_context_data(**kwargs)
        return context


class LocalContactCreateView(LoginRequiredMixin, StoreLevelObjectMixin, CreateView):
    model = AddressbookContact
    form_class = ContactForm
    template_name = 'tele/create.html'

    def form_valid(self, form):
        contact = super(LocalContactCreateView, self).storeLevelFormSanitize(form)
        contact.staff = get_object_or_404(Staff, pk=self.request.session['staff_id'])
        form.save()
        return HttpResponseRedirect(reverse('tele:viewLocalContact', args=(contact.id,)))


class LocalContactLookupView(LoginRequiredMixin, BRListView, StoreSearchMixin):
    model = AddressbookContact
    template_name = 'tele/search.html'
    paginate_by = 30
    context_object_name = 'searchResults'
    queryset = AddressbookContact.objects.all()

    def get_queryset(self):
        #dynamic filter based on request.POST or request.GET
        contacts = AddressbookContact.objects.all().filterReadAll(self.request.store).filter(isShared=False)
        return super(LocalContactLookupView, self).doLocalContactsSearchFilters(contacts)

    def get_context_data(self, **kwargs):
        context = super(LocalContactLookupView, self).get_context_data(**kwargs)
        context['contactSearch'] = True
        return context


class LocalContactUpdateView(LoginRequiredMixin, StoreLevelObjectMixin, UpdateView):
    model = AddressbookContact
    form_class = ContactForm
    template_name = 'tele/update.html'

    def form_valid(self, form):
        contact = form.save(commit=False)
        form.save()
        return HttpResponseRedirect(reverse('tele:viewLocalContact', args=(contact.id,)))


class HeadOfficeContactLookupView(LoginRequiredMixin, BRListView, StoreSearchMixin):
    model = AddressbookContact
    template_name = 'tele/search.html'
    paginate_by = 30
    context_object_name = 'searchResults'
    queryset = AddressbookContact.objects.all()

    def get_queryset(self):
        #dynamic filter based on request.POST or request.GET
        contacts = AddressbookContact.objects.filter(isShared=True)
        return super(HeadOfficeContactLookupView, self).doLocalContactsSearchFilters(contacts)

    def get_context_data(self, **kwargs):
        context = super(HeadOfficeContactLookupView, self).get_context_data(**kwargs)
        context['headOfficeContactSearch'] = True
        return context


class HeadOfficeContactCreateView(LoginRequiredMixin, StoreLevelObjectMixin, CreateView):
    model = AddressbookContact
    form_class = ContactForm
    template_name = 'tele/create.html'

    def form_valid(self, form):
        contact = super(HeadOfficeContactCreateView, self).storeLevelFormSanitize(form)
        contact.staff = get_object_or_404(Staff, pk=self.request.session['staff_id'])
        contact.isShared = True
        form.save()
        return HttpResponseRedirect(reverse('tele:viewHeadOfficeContact', args=(contact.id,)))

    def get_context_data(self, **kwargs):
        context = super(HeadOfficeContactCreateView, self).get_context_data(**kwargs)
        context['globalContactAdd'] = True
        return context


class HeadOfficeContactUpdateView(LoginRequiredMixin, StoreLevelObjectMixin, UpdateView):
    model = AddressbookContact
    form_class = ContactForm
    template_name = 'tele/update.html'

    def form_valid(self, form):
        contact = form.save(commit=False)
        contact.isShared = True
        form.save()
        return HttpResponseRedirect(reverse('tele:viewHeadOfficeContact', args=(contact.id,)))


class HeadOfficeContactDetailView(LoginRequiredMixin, DetailView):
    model = AddressbookContact
    template_name = 'tele/view.html'

    def get_context_data(self, **kwargs):
        context = super(HeadOfficeContactDetailView, self).get_context_data(**kwargs)
        return context


class LocalContactDetailView(LoginRequiredMixin, DetailView):
    model = AddressbookContact
    template_name = 'tele/view.html'

    def get_context_data(self, **kwargs):
        try:
            context = super(LocalContactDetailView, self).get_context_data(**kwargs)
            contact_id = self.kwargs.get('pk') or self.request.GET.get('pk') or self.request.POST.get('pk') or ''
            brandAddressbookContact = BrandAddressbookContact.objects.filter(pk=contact_id)
            context['brandAddressbookContact'] = brandAddressbookContact
            brand = Brand.objects.filter(pk=brandAddressbookContact[0].brand_id)
            context['brand'] = brand[0]
        except (BrandAddressbookContact.DoesNotExist, IndexError):
            print ""
        return context


class LocalBrandRepUpdateView(LoginRequiredMixin, StoreLevelObjectMixin, UpdateView):
    model = BrandAddressbookContact
    form_class = ContactForm
    template_name = 'tele/update.html'

    def form_valid(self, form):
        brandAddressbookContact = form.save(commit=False)
        form.save()
        return HttpResponseRedirect(reverse('tele:viewBrand', args=(brandAddressbookContact.brand_id,)))


class LocalBrandRepCreateView(LoginRequiredMixin, StoreLevelObjectMixin, CreateView):
    model = BrandAddressbookContact
    form_class = BrandContactForm
    template_name = 'tele/create.html'

    def form_valid(self, form):
        m = super(LocalBrandRepCreateView, self).storeLevelFormSanitize(form)
        object_id = self.kwargs.get('object_id') or self.request.GET.get('object_id') or self.request.POST.get('object_id') or ''
        brand = get_object_or_404(Brand, pk=object_id)
        m.brand = brand
        m.staff = get_object_or_404(Staff, pk=self.request.session['staff_id'])
        m.save()
        self.object = m
        return HttpResponseRedirect(reverse('tele:viewBrand', args=(brand.id,)))

    def get_context_data(self, **kwargs):
        context = super(LocalBrandRepCreateView, self).get_context_data(**kwargs)
        object_id = self.kwargs.get('object_id') or self.request.GET.get('object_id') or self.request.POST.get('object_id') or ''
        brand = get_object_or_404(Brand, pk=object_id)
        context['brand'] = brand
        context['isBrandRep'] = True
        return context


def deleteLocalContact(request, pk):
    AddressbookContact.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse('tele:localContactLookup'))


def deleteHeadOfficeContact(request, pk):
    AddressbookContact.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse('tele:headOfficeContactLookup'))


def deleteLocalBrandRep(request, pk):
    brandAddressbookContact = get_object_or_404(BrandAddressbookContact, pk=pk)
    AddressbookContact.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse('tele:viewBrand', args=(brandAddressbookContact.brand_id,)))


