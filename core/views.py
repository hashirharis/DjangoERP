#local imports
from core.models import *
from core.forms import *
from users.models import Staff
from pos.models import SalesLine
#local utility imports
from brutils.generic.views import *
from lib.search import *
from lib.queries import *
#django imports
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Field
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView
from datetime import datetime, timedelta
import json





@login_required()
def home(request):
    if request.store.code == "VW":  # VW users cant access anything else but this
        return HttpResponseRedirect(reverse('vw:home'))
    elif request.staff:
        return HttpResponseRedirect(reverse('bulletins:home'))
    else:
        return render(request, 'core/dashboard.html', {})

#Product CRUD and Search
class ProductSearchMixin(object):
    def doSearchFilters(self, products):
        params = {}
        #search by simple query
        q = self.request.GET.get('q') or self.request.POST.get('q') or ''
        if len(q.strip()):
            products = products.filter(get_query(q, ['model']))
        params['q'] = q
        #search by status
        status = self.request.GET.getlist('status') or self.request.POST.getlist('status') or []
        status.append("current")
        products = products.filter(status__in=status)
        params['status'] = ','.join([x for x in status]) if len(status) else ''
        #search by category
        category = self.request.GET.getlist('category') or self.request.POST.getlist('category') or []
        category = filter(len, category)
        if len(category):
            categoryList = [int(x) for x in category]
            products = products.filter(Q(category__id__in=categoryList) | Q(category__parentCategory__id__in=categoryList) | Q(category__parentCategory__parentCategory__id__in=categoryList))
        params['category'] = ','.join([x for x in category]) if len(category) else ''
        #search by tags
        tags = self.request.GET.getlist('tags') or self.request.POST.getlist('tags') or []
        tags = filter(len, tags)
        if len(tags):
            tagList = [int(x) for x in tags]
            products = products.filter(tags__id__in=tagList)
        params['tags'] = ','.join([x for x in tags]) if len(tags) else ''
        #search by brand
        brand = self.request.GET.getlist('brand') or self.request.POST.getlist('brand') or []
        brand = filter(len, brand)
        if len(brand):
            brandList = [int(x) for x in brand]
            products = products.filter(brand__id__in=brandList)
        params['brand'] = ','.join([x for x in brand]) if len(brand) else ''
        self.context_append['params'] = params
        return products.order_by('-id')[:300]

class ProductPriceLookupView(LoginAndSalePrivelege, BRListView, ProductSearchMixin):
    model = Product
    template_name = 'core/product/search.html'
    paginate_by = 30
    context_object_name = 'products'
    queryset = Product.objects.all()

    def get_queryset(self):
        #dynamic filter based on request.POST or request.GET
        products = Product.objects.all().filterReadAll(self.request.store)
        return super(ProductPriceLookupView, self).doSearchFilters(products)

    def get_context_data(self, **kwargs):
        context = super(ProductPriceLookupView, self).get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.all().filterReadAll(self.request.store)
        context['brands'] = Brand.objects.all().filterReadAll(self.request.store)
        context['tags'] = ProductTag.objects.all().filterReadAll(self.request.store)
        return context

class ProductPriceBookLookup(LoginAndStockPrivelege, ProductPriceLookupView):
    model = Product
    template_name = 'core/product/pricebooksearch.html'

    def get_queryset(self):
        #dynamic filter based on request.POST or request.GET
        products = Product.objects.all().filterUpdateAll(self.request.store)
        return super(ProductPriceBookLookup, self).doSearchFilters(products)

class ProductAjaxLookupView(LoginRequiredMixin, BRListView):
    model = Product
    template_name = 'core/product/search-ajax-other.html'
    paginate_by = 30
    context_object_name = 'products'

    def get_queryset(self):
        #dynamic filter based on request.POST or request.GET
        products = Product.objects.all().filterReadAll(self.request.store)
        productID = self.request.GET.get('productID') or self.request.POST.get('productID') or ''
        price = self.request.GET.get('price') or self.request.POST.get('price') or ''
        if len(productID.strip()) and len(price.strip()):
            #search for product warranties
            product = Product.objects.get(pk=productID)
            products = products.filter(category__in=product.category.getExtWarrantyTypes(), warranty__startValue__lte=price, warranty__endValue__gte=price).order_by('-id')
        elif len(productID.strip()):
            #search only specific product
            products = Product.objects.filter(pk=productID)
        else:
            #regular search
            q = self.request.GET.get('q') or self.request.POST.get('q') or ''
            if len(q.strip()):
                products = products.filter(get_query(q, ['model']))
            #search by purchaser
            purchaser = self.request.GET.get('purchaser') or self.request.POST.get('purchaser') or ''
            if len(purchaser.strip()):
                brandSuppliers = Brand.objects.filter(purchaser=purchaser).values('id')
                products = products.filter(brand__id__in=brandSuppliers)
            distributor = self.request.GET.get('distributor') or self.request.POST.get('distributor') or ''
            if len(distributor.strip()):
                brandSuppliers = Brand.objects.filter(distributor=distributor).values('id')
                products = products.filter(brand__id__in=brandSuppliers)
        return products.order_by('-id')[:30]

    def get_context_data(self, **kwargs):
        context = super(ProductAjaxLookupView, self).get_context_data(**kwargs)
        context['format'] = self.request.GET.get('format') or self.request.POST.get('format') or ''
        productID = self.request.GET.get('productID') or self.request.POST.get('productID') or ''
        if len(productID.strip()):
            context['warrantyRefId'] = Product.objects.get(pk=productID)
        return context

    def render_to_response(self, context, **response_kwargs):
        format = self.request.GET.get('format') or self.request.POST.get('format') or ''
        if format == "stocktake":
            return HttpResponse(json.dumps([{'id': x.id, 'text': x.model, 'systemQuantity': x.getStockCounts(self.request.store).level, 'nsbiQuantity': x.getNSBICount(self.request.store)} for x in self.get_queryset()]))
        else:
            response_kwargs.setdefault('content_type', self.content_type)
            return self.response_class(
                request=self.request,
                template=self.get_template_names(),
                context=context,
                **response_kwargs
            )

class ProductDetailView(LoginAndSalePrivelege, DetailView):
    model = Product
    template_name = 'core/product/view.html'

    def get_context_data(self, **kwargs):
        from stock.models import StoreInventory
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        #global stock levels
        product_stock_levels = StoreInventory.objects.filter(product=self.object)
        product_stock_levels_count = product_stock_levels.aggregate(total=Sum('level'))
        context['stock_levels'] = product_stock_levels
        context['stock_level_total'] = 0 if product_stock_levels_count['total'] is None else product_stock_levels_count['total']
        #local stock levels
        local_levels = StoreInventory.objects.get_or_create(product=self.object, store=self.request.store)[0]
        context['local_levels'] = local_levels
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        deals = Deal.objects.filter(product=self.object, endDate__gt=today)
        currentCount = deals.filter(startDate__lte=today).count() #current
        pendingCount = deals.filter(startDate__gt=today).count() #current
        context['currentCount'] = currentCount
        context['pendingCount'] = pendingCount
        context['deals'] = deals
        context['canEdit'] = self.object.can_write(self.request.store)
        return context

class ProductCalculationSummaryView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'core/product/product-calc-summary.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        id = self.request.GET.get('id') or self.request.POST.get('id') or ''
        return Product.objects.get(pk=id)

    def post(self, request, *args, **kwargs):
        return super(ProductCalculationSummaryView, self).get(request, *args, **kwargs)

#Product CRUD and Search
class ProductCreateView(LoginAndStockPrivelege, StoreLevelObjectMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'core/product/create.html'

    def get_context_data(self, **kwargs):
        context = super(ProductCreateView, self).get_context_data(**kwargs)
        context['parentCategories'] = ProductCategory.objects.filter(depth=1).exclude(name__istartswith='Extended')
        return context

    def form_valid(self, form):
        product = super(ProductCreateView, self).storeLevelFormSanitize(form)
        product.staff = get_object_or_404(Staff, pk=self.request.session['staff_id'])
        product.costPrice = product.tradePrice
        product.updateCurrentSPANNet() #also saves
        form.save_m2m()
        return HttpResponseRedirect(reverse('core:viewProduct', args=(product.id,)))

class WarrantyCreateView(ProductCreateView):
    model = Warranty
    form_class = WarrantyForm

    def get_context_data(self, **kwargs):
        context = super(WarrantyCreateView, self).get_context_data(**kwargs)
        context['parentCategories'] = ProductCategory.objects.filter(depth=1, name__istartswith="Extended")
        context['isWarrantyCreateView'] = True
        return context

class ProductUpdateView(LoginAndStockPrivelege, StoreLevelObjectMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'core/product/update.html'

    def get_context_data(self, **kwargs):
        context = super(ProductUpdateView, self).get_context_data(**kwargs)
        context['parentCategories'] = ProductCategory.objects.filter(depth=1).exclude(name__istartswith='Extended')
        return context

    def form_valid(self, form):
        product = form.save(commit=False)
        product.updateCurrentSPANNet()
        form.save_m2m()
        return HttpResponseRedirect(reverse('core:viewProduct', args=(product.id,)))

class WarrantyUpdateView(ProductUpdateView):
    model = Warranty
    form_class = WarrantyForm
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super(WarrantyUpdateView, self).get_context_data(**kwargs)
        context['parentCategories'] = ProductCategory.objects.filter(depth=1, name__istartswith="Extended")
        return context

class ProductDeleteView(LoginAndStockPrivelege, JSONDeleteView):
    model = Product

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        product = self.object
        if SalesLine.objects.filter(item=product).count():
            return HttpResponse(json.dumps({'error':'You cannot delete a product that is in a sale.', }))
        product.delete()
        return HttpResponse(json.dumps({'success': True, }))

#product tag CRUD
class ProductTagSearchView(LoginAndStockPrivelege, BRListView):
    model = ProductTag
    template_name = 'core/tags/search.html'
    paginate_by = 30

    def get_queryset(self):
        #dynamic filter based on request.POST or request.GET
        tags = ProductTag.objects.all().filterUpdateAll(self.request.store).filter(Q(type__exact='Feature') | Q(type__exact='Other'))
        #search by simple query
        q = self.request.GET.get('q') or self.request.POST.get('q') or ''
        if len(q.strip()):
            tags = tags.filter(get_query(q, ['tag']))
        self.context_append['q'] = q
        self.context_append.update(getGenericCrudURLS("ProductTag", c=True, u=True, d=True))
        return tags.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(ProductTagSearchView, self).get_context_data(**kwargs)
        context['form'] = TagForm(store=self.request.store)
        return context

class ProductTagCreateView(LoginRequiredMixin, StoreLevelObjectMixin, JSONCreateView):
    model = ProductTag
    form_class = TagForm

    def form_valid(self, form):
        tag = super(ProductTagCreateView, self).storeLevelFormSanitize(form)
        tag.save()
        return HttpResponse(json.dumps({'success': True, }))

class ProductTagUpdateView(LoginRequiredMixin, StoreLevelObjectMixin, JSONUpdateView):
    model = ProductTag
    form_class = TagForm
    template_name = 'core/tags/update.html'

class ProductTagDeleteView(LoginRequiredMixin, JSONDeleteView):
    model = ProductTag
#end of product tag crud

#brand crud
class BrandSearchView(LoginAndStockPrivelege, BRListView):
    model = Brand
    template_name = 'core/brand/search.html'
    paginate_by = 30

    def get_queryset(self):
        #dynamic filter based on request.POST or request.GET
        brands = Brand.objects.all().filterReadAll(self.request.store)
        #search by simple query
        q = self.request.GET.get('q') or self.request.POST.get('q') or ''
        self.context_append['q'] = q
        if len(q.strip()):
            brands = brands.filter(get_query(q, ['brand', 'distributor']))
        #brands.annotate(Count('product')).order_by('product__count')[:300]
        return brands.order_by('brand')[:300]

class BrandCreateView(LoginAndStockPrivelege, StoreLevelObjectMixin, CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'core/brand/create.html'

    def form_valid(self, form):
        brand = super(BrandCreateView, self).storeLevelFormSanitize(form)
        brand.actualRebate = brand.rebate
        brand.save()
        return HttpResponseRedirect(reverse('core:viewBrand', args=(brand.id,)))

    def get_context_data(self, **kwargs):
        context = super(BrandCreateView, self).get_context_data(**kwargs)
        context['distributors'] = json.dumps([str(x) for x in Brand.getUniqueDistributors()])
        context['purchasers'] = json.dumps([str(x) for x in Brand.getUniquePurchasers()])
        return context

class BrandUpdateView(LoginAndStockPrivelege, StoreLevelObjectMixin, UpdateView):
    model = Brand
    form_class = BrandForm
    template_name = 'core/brand/update.html'

    def form_valid(self, form):
        brand = super(BrandUpdateView, self).storeLevelFormSanitize(form)
        brand.save()
        return HttpResponseRedirect(reverse('core:viewBrand', args=(brand.id,)))

    def get_context_data(self, **kwargs):
        context = super(BrandUpdateView, self).get_context_data(**kwargs)
        context['distributors'] = json.dumps([str(x) for x in Brand.getUniqueDistributors()])
        context['purchasers'] = json.dumps([str(x) for x in Brand.getUniquePurchasers()])
        return context

class BrandDetailView(LoginAndStockPrivelege, DetailView):
    model = Brand
    template_name = 'core/brand/view.html'

    def get_context_data(self, **kwargs):
        context = super(BrandDetailView, self).get_context_data(**kwargs)
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        deals = ClassVendorBonus.objects.filter(brand=self.object, endDate__gt=today)
        currentCount = deals.filter(startDate__lte=today).count() #current
        pendingCount = deals.filter(startDate__gt=today).count() #current
        context['currentCount'] = currentCount
        context['pendingCount'] = pendingCount
        context['deals'] = deals
        return context

class BrandDeleteView(LoginAndStockPrivelege, JSONDeleteView):
    model = Brand

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        brand = self.object
        if Product.objects.filter(brand=brand).count():
            return HttpResponse(json.dumps({'error': 'You cannot delete a brand which has products that use it.', }))
        brand.delete()
        return HttpResponse(json.dumps({'success': True, }))

#end of brand crud
class VendorBonusSearchView(LoginAndStockPrivelege, BRListView):
    model = ClassVendorBonus
    template_name = 'core/brand/vendorBonus/search.html'
    paginate_by = 30
    context_object_name = 'deals'

    def get_queryset(self):
        #dynamic filter based on request.POST or request.GET
        brand_id = self.kwargs.get('brand_id') or self.request.GET.get('brand_id') or self.request.POST.get('brand_id') or ''
        brand = get_object_or_404(Product, pk=brand_id)
        deals = ClassVendorBonus.objects.all().filter(brand=brand)
        #search by simple query
        startDate = self.request.GET.get('startDate') or self.request.POST.get('startDate') or ''
        if startDate == '':
            startDate = datetime.today() - timedelta(days=120)
        else:
            startDate = datetime.strptime(startDate, "%m/%d/%Y")
        endDate = self.request.GET.get('endDate') or self.request.POST.get('endDate') or ''
        if endDate == '':
            endDate = datetime.today() + timedelta(days=1)
        else:
            endDate = datetime.strptime(endDate, "%m/%d/%Y")
        if startDate > endDate:
            endDate = startDate
        self.context_append['startDate'] = startDate
        self.context_append['endDate'] = endDate
        return deals.filter(endDate__lte=endDate, startDate__gte=startDate).order_by('-endDate')[:300]

    def get_context_data(self, **kwargs):
        context = super(VendorBonusSearchView, self).get_context_data(**kwargs)
        brand_id = self.kwargs.get('brand_id') or self.request.GET.get('brand_id') or self.request.POST.get('brand_id') or ''
        brand = get_object_or_404(Brand, pk=brand_id)
        context['brand'] = brand
        return context

class VendorBonusCreateView(LoginAndStockPrivelege, CreateView):
    model = ClassVendorBonus
    form_class = VendorBonusForm
    template_name = 'core/brand/vendorBonus/create.html'

    def get_form_kwargs(self):
        kwargs = super(VendorBonusCreateView, self).get_form_kwargs()
        kwargs['store'] = self.request.store
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(VendorBonusCreateView, self).get_context_data(**kwargs)
        brand_id = self.kwargs.get('brand_id') or self.request.GET.get('brand_id') or self.request.POST.get('brand_id') or ''
        brand = get_object_or_404(Brand, pk=brand_id)
        context['brand'] = brand
        context['parentCategories'] = ProductCategory.objects.filter(depth=1).exclude(name__istartswith='Extended')
        return context

    def form_valid(self, form):
        #add product
        m = form.save(commit=False)
        brand_id = self.kwargs.get('brand_id') or self.request.GET.get('brand_id') or self.request.POST.get('brand_id') or ''
        brand = get_object_or_404(Brand, pk=brand_id)
        m.brand = brand
        staff = get_object_or_404(Staff, pk=self.request.session['staff_id'])
        m.createdBy = staff
        m.save()
        self.object = m
        return HttpResponseRedirect(reverse('core:viewBrand', args=(brand.id,)))

class VendorBonusUpdateView(LoginAndStockPrivelege, UpdateView):
    model = ClassVendorBonus
    form_class = VendorBonusForm
    template_name = 'core/brand/vendorBonus/update.html'

    def get_form_kwargs(self):
        kwargs = super(VendorBonusUpdateView, self).get_form_kwargs()
        kwargs['store'] = self.request.store
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(VendorBonusUpdateView, self).get_context_data(**kwargs)
        context['brand'] = self.object.brand
        context['parentCategories'] = ProductCategory.objects.filter(depth=1).exclude(name__istartswith='Extended')
        return context

    def form_valid(self, form):
        #add product
        m = form.save()
        m.save()
        self.object = m
        return HttpResponseRedirect(reverse('core:viewBrand', args=(self.object.brand.id,)))

class VendorBonusDeleteView(LoginAndStockPrivelege, JSONDeleteView):
    model = ClassVendorBonus

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        bonus = self.object
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        bonus.active = False
        bonus.endDate = today
        bonus.save()
        return HttpResponse(json.dumps({'success': True, }))

#Product Deal CRUD
class ProductDealSearchView(LoginAndSalePrivelege, BRListView):
    model = Deal
    template_name = 'core/product/deal/search.html'
    paginate_by = 30
    context_object_name = 'deals'

    def get_queryset(self):
        #dynamic filter based on request.POST or request.GET
        product_id = self.kwargs.get('product_id') or self.request.GET.get('product_id') or self.request.POST.get('product_id') or ''
        product = get_object_or_404(Product, pk=product_id)
        deals = Deal.objects.all().filter(product=product)
        #search by simple query
        startDate = self.request.GET.get('startDate') or self.request.POST.get('startDate') or ''
        if startDate == '':
            startDate = datetime.today() - timedelta(days=120)
        else:
            startDate = datetime.strptime(startDate, "%m/%d/%Y")
        endDate = self.request.GET.get('endDate') or self.request.POST.get('endDate') or ''
        if endDate == '':
            endDate = datetime.today() + timedelta(days=1)
        else:
            endDate = datetime.strptime(endDate, "%m/%d/%Y")
        if startDate > endDate:
            endDate = startDate
        self.context_append['startDate'] = startDate
        self.context_append['endDate'] = endDate
        return deals.filter(endDate__lte=endDate, startDate__gte=startDate).order_by('-endDate')[:300]

    def get_context_data(self, **kwargs):
        context = super(ProductDealSearchView, self).get_context_data(**kwargs)
        product_id = self.kwargs.get('product_id') or self.request.GET.get('product_id') or self.request.POST.get('product_id') or ''
        product = get_object_or_404(Product, pk=product_id)
        context['product'] = product
        return context

class ProductDealCreateView(LoginAndStockPrivelege, CreateView):
    model = Deal
    form_class = DealForm
    template_name = 'core/product/deal/create.html'

    def get_context_data(self, **kwargs):
        context = super(ProductDealCreateView, self).get_context_data(**kwargs)
        product_id = self.kwargs.get('product_id') or self.request.GET.get('product_id') or self.request.POST.get('product_id') or ''
        product = get_object_or_404(Product, pk=product_id)
        context['product'] = product
        return context

    def form_valid(self, form):
        #add product
        m = form.save(commit=False)
        product_id = self.kwargs.get('product_id') or self.request.GET.get('product_id') or self.request.POST.get('product_id') or ''
        product = get_object_or_404(Product, pk=product_id)
        m.product = product
        staff = get_object_or_404(Staff, pk=self.request.session['staff_id'])
        m.createdBy = staff
        m.save()
        self.object = m
        return HttpResponseRedirect(reverse('core:viewProduct', args=(product.id,)))

class ProductDealUpdateView(LoginAndStockPrivelege, UpdateView):
    model = Deal
    form_class = DealForm
    template_name = 'core/product/deal/update.html'

    def get_context_data(self, **kwargs):
        context = super(ProductDealUpdateView, self).get_context_data(**kwargs)
        context['product'] = self.object.product
        return context

    def form_valid(self, form):
        #add product
        m = form.save()
        m.save()
        self.object = m
        return HttpResponseRedirect(reverse('core:viewProduct', args=(self.object.product.id,)))

class ProductDealDeleteView(LoginAndStockPrivelege, JSONDeleteView):
    model = Deal

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        deal = self.object
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        deal.active = False
        deal.endDate = today
        deal.save()
        return HttpResponse(json.dumps({'success': True, }))

#end of Product Deal CRUD

#Product Category CRUD
class ProductCategoryListView(LoginAndStockPrivelege, BRListView):
    model = ProductCategory
    template_name = 'core/categories/list.html'
    queryset = ProductCategory.objects.all()

    def get_queryset(self):
        #dynamic filter based on request.POST or request.GET
        categories = self.queryset.filterReadAll(self.request.store).filter(depth=1)
        return categories.order_by('name')

    def get_context_data(self, **kwargs):
        context = super(ProductCategoryListView, self).get_context_data(**kwargs)
        context['form'] = ProductCategoryForm(store=self.request.store)
        context['allCategories'] = self.queryset.filterReadAll(self.request.store)
        context['deleteURL'] = reverse('core:deleteProductCategory', args=[1])
        context['updateURL'] = reverse('core:updateProductCategory', args=[1])
        context['createURL'] = reverse('core:createProductCategory')
        return context

class ProductCategoryCreateView(LoginAndStockPrivelege, StoreLevelObjectMixin, JSONCreateView):
    model = ProductCategory
    form_class = ProductCategoryForm

    def form_valid(self, form):
        category = super(ProductCategoryCreateView, self).storeLevelFormSanitize(form)
        category.depth = category.parentCategory.depth + 1 if category.parentCategory else 1
        category.save()
        return HttpResponse(json.dumps({'success': True, }))

class ProductCategoryUpdateView(LoginAndStockPrivelege, StoreLevelObjectMixin, JSONUpdateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    template_name = 'core/categories/update.html'
    context_object_name = 'object'

    def form_valid(self, form):
        category = form.save()
        category.depth = category.parentCategory.depth + 1 if category.parentCategory else 1
        category.save()
        return HttpResponse(json.dumps({'success': True, }))

class ProductCategoryMarkupUpdateView(LoginAndStockPrivelege, JSONUpdateView):
    model = ProductCategoryMarkup
    form_class = ProductCategoryMarkupForm
    template_name = 'core/categories/update-markup.html'
    context_object_name = 'object'

    def get_object(self, queryset=None):
        category = get_object_or_404(ProductCategory, pk=self.kwargs['pk'])
        return ProductCategoryMarkup.objects.get_or_create(store=self.request.store, category=category)[0]

class ProductCategoryDeleteView(LoginAndSalePrivelege, JSONDeleteView):
    model = ProductCategory

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        category = self.object
        if len(Product.objects.filter(Q(category=category)|Q(category__parentCategory=category)|Q(category__parentCategory__parentCategory=category)|Q(category__parentCategory__parentCategory__parentCategory=category))):
            return HttpResponse(json.dumps({'error': 'Category is attached to one or more Products - Action Not Completed', }))
        else:
            category.delete()
            return HttpResponse(json.dumps({'success': True, }))
#End of Product Category CRUD