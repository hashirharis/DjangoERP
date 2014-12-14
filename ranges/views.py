# Create your views here.

from django.shortcuts import render
import models
import forms
from django.views.generic import View, ListView, DetailView, DeleteView
from users import models as usermodels
from django.shortcuts import HttpResponseRedirect
from core.models import Product
from django.views.generic import UpdateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import RequestContext
from datetime import datetime
import calendar
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
from stockranges import is_current_month
from django.conf import settings
from b2b.models import  HeadOfficeInvoice, HeadOfficeInvoiceLine
from django.db.models import Q
from django.db import IntegrityError


def core_stock_main(request):
    # just a small redirect to the current month if user didn't specify any
    date = datetime.now()
    month = int(date.month)
    year = int(date.year)
    qdict = request.GET.copy()
    qdict.update({'month': month, 'year': year})
    return HttpResponseRedirect(reverse('core_stock:stock_range', kwargs={'month': month, 'year': year}))


def editRangesMain(request):
    date = datetime.now()
    month = int(date.month)
    year = int(date.year)
    qdict = request.GET.copy()
    qdict.update({'month': month, 'year': year})
    return HttpResponseRedirect(reverse('core_stock:editRange', kwargs={'month': month, 'year': year}))


def convertUTCtoLocal(date):
    date = datetime.strptime(date, "%m/%Y")
    offset = datetime.now() - datetime.utcnow()
    ofsetDate = date - offset
    month = '%02d' % ofsetDate.month
    return str(month) + '/' + str(ofsetDate.year)


class StoreRangesView(View):
    template_name = "stock_ranges_main.html"
    stores = models.StoreRange.objects.all().order_by('store__name')
    model = models.StoreRange

    def get(self, request, *args, **kwargs):
        form = forms.AddStoreForm()
        month = self.kwargs.get('month')
        if len(month) == 1:
            month = '0' + month
        year = self.kwargs.get('year')
        date = month + '/' + year
        store_success = False

        if request.GET.get('s') != None:
            store_success = request.GET.get('s')
        print '______________'


        if request.store.displayHOMenu():
            stores_gold = models.StoreRange.objects.filter(month__contains=date, rangeType = "G").order_by('store__name')
            stores_silver = models.StoreRange.objects.filter(month__contains=date, rangeType = "S").order_by('store__name')
            stores_bronze = models.StoreRange.objects.filter(month__contains=date, rangeType = "B").order_by('store__name')
        else:
            stores_gold = models.StoreRange.objects.filter(store=request.store, month__contains=date, rangeType = "G").order_by('store__name')
            stores_silver = models.StoreRange.objects.filter(store=request.store, month__contains=date, rangeType = "S").order_by('store__name')
            stores_bronze = models.StoreRange.objects.filter(store=request.store, month__contains=date, rangeType = "B").order_by('store__name')

        monthname = calendar.month_name[int(month)]
        no_ranges = False
        if len(stores_gold)+len(stores_silver)+len(stores_bronze) == 0 and not request.store.displayHOMenu():
            no_ranges = True



        variables = {'form': form, 'stores_gold': stores_gold, 'stores_silver': stores_silver,
                     'stores_bronze': stores_bronze, 'month': monthname, 'year': year, 'can_edit':request.store.displayHOMenu(),
        'root':settings.STATIC_ROOT, 'no_ranges': no_ranges}
        if store_success:
            variables['store_name_success'] = store_success
        if request.GET.get('success'):
            variables['success'] = True
        elif request.GET.get('fail'):
            variables['fail'] = True
        variables = RequestContext(request, variables)
        return render(request, self.template_name, variables)

    def get_context_data(self, **kwargs):
        self.context = super(StoreRangesView, self).get_context_data(**kwargs)
        self.context['form'] = self.form
        self.context['object_list'] = self.stores
        return self.context

    def move_to_next_month(self, storeRange):
        date_after_month = (datetime.today() + relativedelta(months=1)).strftime('%m/%Y')
        if not models.StoreRange.objects.filter(store=storeRange.store, rangeType=storeRange.rangeType,
                                                month=date_after_month).exists():
            newproductrange = models.StoreRange(store=storeRange.store, rangeType=storeRange.rangeType,
                                                month=date_after_month)
            try:
                newproductrange.save()
            except IntegrityError:
                pass

    def post(self, request, *args, **kwargs):
        form = forms.AddStoreForm(request.POST)
        success = False
        url = reverse('core_stock:stock_range')
        if form.is_valid():
            store = usermodels.Store.objects.get(id=form.cleaned_data.get('storeName'))
            range_type = form.cleaned_data.get('rangeType')
            month = form.cleaned_data.get('month')
            month_for_url = form.cleaned_data.get('month').split('/')[0]
            year = form.cleaned_data.get('month').split('/')[1]
            url = reverse('core_stock:stock_range', kwargs={'month': month_for_url, 'year': year})
            try:
                storeRange = models.StoreRange.objects.get(store=store, month=month, rangeType=range_type)
                qs = 'fail=True'
            except models.StoreRange.DoesNotExist:
                storeRange = models.StoreRange(store=store, rangeType=range_type, month=month)
                try:
                    storeRange.save()
                    qs = 'success=True&s='+str(storeRange)
                    if is_current_month(month):
                        self.move_to_next_month(storeRange)
                except IntegrityError:
                    qs = 'fail=True'



        else:
            qs = 'fail=True'
        return HttpResponseRedirect('?'.join((url, qs)))


class ProductRangeUpdateView(UpdateView):
    model = models.ProductRange
    success_url = reverse_lazy("core_stock:editRange")
    form_class = forms.UpdateProductRangeForm
    template_name = "add_stock_range_form.html"



    def form_valid(self, request, *args, **kwargs):
        self.valid = super(ProductRangeUpdateView, self).form_valid(request, **kwargs)
        product_id = self.kwargs.get('pk')
        print self.valid
        product_range = models.ProductRange.objects.get(id=product_id)
        if is_current_month(product_range.month):
            self.update_next_month(product_range)
        return HttpResponseRedirect(reverse('core_stock:editRange'))

    def update_next_month(self, updated_range):
        date_after_month = (datetime.today() + relativedelta(months=1)).strftime('%m/%Y')
        if models.ProductRange.objects.filter(product=updated_range.product, productRange=updated_range.productRange,
                                              month=date_after_month).exists():
            newproductrange = models.ProductRange.objects.get(product=updated_range.product,
                                                              productRange=updated_range.productRange,
                                                              month=date_after_month)
            newproductrange.guaranteed = updated_range.guaranteed
            newproductrange.productRange = updated_range.productRange
            newproductrange.bonus = updated_range.bonus
            newproductrange.save()

    def get(self, request, *args, **kwargs):
        if not request.store.displayHOMenu():
            return HttpResponseRedirect(reverse('core_stock:stock_range'))
        else:
            return super(ProductRangeUpdateView,self).get(self,*args, **kwargs)


class StockRangeUpdateView(UpdateView):
    model = models.StoreRange
    success_url = reverse_lazy("core_stock:stock_range")
    form_class = forms.UpdateRangeForm
    template_name = "add_stock_range_form.html"

    def form_valid(self, request, *args, **kwargs):
        self.valid = super(StockRangeUpdateView, self).form_valid(request, **kwargs)
        store_id = self.kwargs.get('pk')
        print self.valid
        store_range = models.StoreRange.objects.get(id=store_id)
        if is_current_month(store_range.month):
            print 'is current month'
            self.update_next_month(store_range)
        return HttpResponseRedirect(reverse('core_stock:stock_range'))

    def update_next_month(self, updated_range):
        date_after_month = (datetime.today() + relativedelta(months=1)).strftime('%m/%Y')
        if models.StoreRange.objects.filter(store=updated_range.store, month=date_after_month,
                                            rangeType=updated_range.rangeType).exists():
            newStoreRange = models.StoreRange.objects.get(store=updated_range.store, month=date_after_month,
                                                          rangeType=updated_range.rangeType)
            newStoreRange.rangeType = updated_range.rangeType
            newStoreRange.save()

    def get(self, request, *args, **kwargs):
        if not request.store.displayHOMenu():
            return HttpResponseRedirect(reverse('core_stock:stock_range'))
        else:
            return super(StockRangeUpdateView,self).get(self,*args, **kwargs)


class ProductRangeDeleteView(DeleteView):
    model = models.ProductRange
    success_url = reverse_lazy('core_stock:editRange')
    template_name = "productrange_confirm_delete.html"

    def get(self, request, *args, **kwargs):
        if not request.store.displayHOMenu():
            return HttpResponseRedirect(reverse('core_stock:stock_range'))
        else:
            return super(ProductRangeDeleteView,self).get(self,*args, **kwargs)

    def get_object(self, queryset=None):
        product_range = super(ProductRangeDeleteView, self).get_object()
        if is_current_month(product_range.month):
            self.update_next_month(product_range)
        return product_range

    def update_next_month(self, product_range):
        date_after_month = (datetime.today() + relativedelta(months=1)).strftime('%m/%Y')
        if models.ProductRange.objects.filter(product=product_range.product, productRange=product_range.productRange,
                                              month=date_after_month).exists():
            newproductrange = models.ProductRange.objects.get(product=product_range.product,
                                                              productRange=product_range.productRange,
                                                              month=date_after_month)
            newproductrange.delete()


class StoreRangeDeleteView(DeleteView):
    model = models.StoreRange
    success_url = reverse_lazy('core_stock:stock_range')
    template_name = "productrange_confirm_delete.html"

    def get(self, request, *args, **kwargs):
        if not request.store.displayHOMenu():
            return HttpResponseRedirect(reverse('core_stock:stock_range'))
        else:
            return super(StoreRangeDeleteView, self).get(self, *args, **kwargs)

    def post(self, *args, **kwargs):
        current_month = str(self.get_object().month).split('/')[0]
        current_year = str(self.get_object().month).split('/')[1]
        self.success_url = reverse_lazy('core_stock:stock_range', kwargs={'month':current_month, 'year':current_year})
        return super(StoreRangeDeleteView, self).post(*args, **kwargs)

    def get_object(self, queryset=None):
        product_range = super(StoreRangeDeleteView, self).get_object()
        if is_current_month(product_range.month):
            self.update_next_month(product_range)
        return product_range

    def update_next_month(self, updated_range):
        date_after_month = (datetime.today() + relativedelta(months=1)).strftime('%m/%Y')
        if models.StoreRange.objects.filter(rangeType=updated_range.rangeType, store=updated_range.store,
                                            month=date_after_month).exists():
            newStoreRange = models.StoreRange.objects.get(store=updated_range.store, month=date_after_month,
                                                          rangeType=updated_range.rangeType)
            newStoreRange.delete()


class StoreDetailView(View):
    context_object_name = 'object_list'
    model = models.StoreDetail
    template_name = "store_details.html"

    def get_queryset(self):
        return models.StoreDetail.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(StoreDetailView, self).get_context_data()
        return context

    def get(self, request, *args, **kwargs):
        storeid = self.kwargs['pk']
        store = models.StoreRange.objects.get(id=storeid)
        date_object = datetime.strptime(store.month, '%m/%Y')
        details, total = self.getStocksForMonth(store)
        vars = RequestContext(request,{'details': details, 'storerange': store,
                                                    'month': calendar.month_name[int(date_object.month)],
                                                    'year': date_object.year,
                                                    'total': total})
        return render(request, self.template_name,vars )

    def getStocksForMonth(self, store):
        date_object = datetime.strptime(store.month, '%m/%Y')
        storeType = store.rangeType

        invoices = HeadOfficeInvoice.objects.filter(store=store.store, invoiceDate__month=date_object.month,
                                                    invoiceDate__year=date_object.year)
        rangedItems = [i.product for i in models.ProductRange.objects.filter(productRange = storeType,
                                                                             month__contains=str(date_object.month)+'/'+str(date_object.year)).order_by('product__model')]
        invoiceLines = [i.item for i in HeadOfficeInvoiceLine.objects.filter(invoice__in=invoices, item__in=rangedItems).distinct()]
        productRanges = models.ProductRange.objects.filter(Q(product__in =invoiceLines,productRange=storeType,
                                                           month__contains=str(date_object.month)+'/'+str(date_object.year)) | Q(productRange=storeType,
                                                           month__contains=str(date_object.month)+'/'+str(date_object.year), guaranteed=True)).distinct().order_by('product')

        finalSum = productRanges.aggregate(Sum('bonus'))
        return productRanges,finalSum.get('bonus__sum')








class EditRangesListView(ListView):
    template_name = "product_range_table.html"
    form = forms.AddProductForm
    golden = models.ProductRange.objects.filter(productRange='G').order_by('product__model')
    silver = models.ProductRange.objects.filter(productRange='S').order_by('product__model')
    bronze = models.ProductRange.objects.filter(productRange='B').order_by('product__model')
    success_url = reverse_lazy("core_stock:edit_ranges")
    model = models.ProductRange()

    def get_context_data(self, **kwargs):
        self.context = super(EditRangesListView, self).get_context_data(**kwargs)
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        if len(month) == 1:
            month = '0' + month
        date = month + '/' + year
        self.golden = models.ProductRange.objects.filter(productRange='G', month__contains=date).order_by(
            'product__model')
        self.silver = models.ProductRange.objects.filter(productRange='S', month__contains=date).order_by(
            'product__model')
        self.bronze = models.ProductRange.objects.filter(productRange='B', month__contains=date).order_by(
            'product__model')
        self.context['form'] = self.form
        self.context['gold'] = self.golden
        self.context['silver'] = self.silver
        self.context['bronze'] = self.bronze
        self.context['month'] = calendar.month_name[int(month)]
        self.context['year'] = year
        return self.context

    def get(self, request, *args, **kwargs):
        if not request.store.displayHOMenu():
            return HttpResponseRedirect(reverse("core_stock:stock_range"))
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        if len(month) == 1:
            month = '0' + month
        date = month + '/' + year
        variables = {}
        golden = models.ProductRange.objects.filter(productRange='G', month__contains=date).order_by(
            'product__model')
        silver = models.ProductRange.objects.filter(productRange='S', month__contains=date).order_by(
            'product__model')
        bronze = models.ProductRange.objects.filter(productRange='B', month__contains=date).order_by(
            'product__model')
        monthname = calendar.month_name[int(month)]
        variables['form'] = self.form
        variables['gold'] = golden
        variables['silver'] = silver
        variables['bronze'] = bronze
        variables['month'] = monthname
        variables['year'] = year
        if request.GET.get('success'):
            variables['success'] = True
        elif request.GET.get('fail'):
            variables['fail'] = True
        else:
            pass
        variables = RequestContext(request, variables)
        return render(request, self.template_name, variables)

    def move_to_next_month(self, oldrange):
        date_after_month = (datetime.today() + relativedelta(months=1)).strftime('%m/%Y')
        if not models.ProductRange.objects.filter(product=oldrange.product, productRange=oldrange.productRange
                ,month=date_after_month).exists():
            newproductrange = models.ProductRange(product=oldrange.product, guaranteed=oldrange.guaranteed,
                                                  bonus=oldrange.bonus, productRange=oldrange.productRange,
                                                  month=date_after_month)
            newproductrange.save()

    def post(self, request, *args, **kwargs):
        year = self.kwargs['year']
        month_url = self.kwargs['month']
        form = self.form(request.POST)
        if form.is_valid():
            product = Product.objects.get(id=form.cleaned_data.get('product'))
            guaranteed = form.cleaned_data.get('guaranteed')
            month = form.cleaned_data.get('month')
            url = reverse('core_stock:editRange', kwargs={'year': year, 'month': month_url}) + "?success=True"
            bonusType = 0
            if form.cleaned_data.get('rangeType_gold'):
                bonusType = "G"
                bonus = form.cleaned_data.get('gold_bonus')
                exists1 = models.ProductRange.objects.filter(product=product, productRange="G", month=month).exists()
                if not exists1:
                    prange = models.ProductRange(product=product, guaranteed=guaranteed, bonus=bonus, productRange="G",
                                                 month=month)
                    prange.save()
                    if is_current_month(month):
                        self.move_to_next_month(prange)
                else:
                    url = reverse('core_stock:editRange', kwargs={'year': year, 'month': month_url}) + "?fail=True"
            if form.cleaned_data.get('rangeType_silver'):
                bonusType = "S"
                bonus = form.cleaned_data.get('silver_bonus')
                exists2 = models.ProductRange.objects.filter(product=product, productRange="S", month=month).exists()
                if not exists2:
                    prange = models.ProductRange(product=product, guaranteed=guaranteed, bonus=bonus, productRange="S",
                                                 month=month)
                    prange.save()
                    if is_current_month(month):
                        self.move_to_next_month(prange)
                else:
                    url = reverse('core_stock:editRange', kwargs={'year': year, 'month': month_url}) + "?fail=True"
            if form.cleaned_data.get('rangeType_bronz'):
                bonusType = "B"
                bonus = form.cleaned_data.get('bronze_bonus')
                exists3 = models.ProductRange.objects.filter(product=product, productRange="B", month=month).exists()
                if not exists3:
                    prange = models.ProductRange(product=product, guaranteed=guaranteed, bonus=bonus, productRange="B",
                                                 month=month)
                    prange.save()
                    if is_current_month(month):
                        self.move_to_next_month(prange)
                else:
                    url = reverse('core_stock:editRange', kwargs={'year': year, 'month': month_url}) + "?fail=True"

            if guaranteed:
                stores = []
                if bonusType == "G":
                    stores = models.StoreRange.objects.filter(rangeType="G", month=month)
                elif bonusType == "S":
                    stores = models.StoreRange.objects.filter(rangeType="S", month=month)
                elif bonusType == "B":
                    stores = models.StoreRange.objects.filter(rangeType="B", month=month)

                if bonusType in ["G", "S", "B"]:
                    for storeRange in stores:
                        detail = models.StoreDetail(product=product, storeRange = storeRange, passed="T", month=month,
                                                    bonus= bonus, guaranteed=guaranteed)
                        detail.save()

        else:
            url = reverse('core_stock:editRange', kwargs={'year': year, 'month': month_url}) + "?bad=True"
        return HttpResponseRedirect(url)




    
    
    

