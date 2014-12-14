       #local imports
from stock.forms import *
#local utility imports
from lib.search import filterGenericSearchQuery
from lib.jsonStringify.stocktakes import *
from lib.jsonStringify.claims import *
from lib.queries import *
from brutils.generic.views import *
#django imports
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
#python imports
import json

@login_required()
def dashboard(request):
    return render(request, 'stock/dashboard.html')

@access_required('stock')
@login_required()
def searchStockTake(request, type):
    stocktake = StockTake.objects.all().filter(store=request.store) #filter store stocktake

    if type =="SAVED":
        stocktake = stocktake.filter(status="SAVED")
    else:
        stocktake = stocktake.filter(status=type)

    context = filterGenericSearchQuery(stocktake, [], request.GET)

    context.update({
        'filter': type,
        'entityName': "Stock Take"
    })

    return render(request, 'stock/stocktake/search.html', context)

@access_required('stock')
@login_required()
def stockTakeHome(request):
    context = {
        'pending': StockTake.objects.all().filter(store=request.store, status="SAVED").order_by('-created')[:100],
        'completed': StockTake.objects.all().filter(store=request.store, status="COMPLETED").order_by('-created')[:25],
    }
    return render(request, 'stock/stocktake/dashboard.html', context)

@access_required('stock')
@login_required()
def newStockTake(request):
    context = {
        'products': Product.objects.all().filterReadAll(request.store)[:25]
    }
    return render(request, 'stock/stocktake/new.html', context)

@access_required('stock')
@login_required()
def newBarcodeStockTake(request):
    context = {
        'products': Product.objects.all().filterReadAll(request.store)[:25]
    }
    return render(request, 'stock/stocktake/new-barcode.html', context)

@access_required('stock')
@login_required()
def stocktakeFromBarcodeDump(request):
    import StringIO
    import csv
    #processing logic for CS3070 csv dump
    csvdump = request.GET.get('csv') or request.POST.get('csv') or None
    if csvdump is None:
        raise Http404(Exception("No CSV Data"))
    #verify data integrity
    EANSNotFound = []
    counter = 1
    for line in csv.reader(StringIO.StringIO(csvdump)):
        try:
            check = line[3]
            if len(check) > 4:
                Product.objects.get(EAN=check)
            elif len(check) <= 0:
                return HttpResponse(json.dumps({'error': 'Malformed Error on line #%i, you cannot have a blank scan' % counter}))
        except (Product.DoesNotExist, Product.MultipleObjectsReturned):
            EANSNotFound.append(line[3])
        except IndexError:
            #scan was not completed appropriately
            return HttpResponse(json.dumps({'error': 'Malformed Error on line #%i, you cannot have a blank scan' % counter}))
        counter += 1
    if len(EANSNotFound):
        return HttpResponse(json.dumps({'error': 'EANS Not Found: %s' % ', '.join(EANSNotFound)}))
    #Integrity check passed, create a stocktake object mocking the save stocktake page.
    stockTakeLines = []
    for line in csv.reader(StringIO.StringIO(csvdump)):
        #format should always be either barcode quantity or barcode only (quantity is one)
        if len(line[3]) > 4:
            product = Product.objects.get(EAN=line[3])
            currentItem = {
                'productID': product.id,
                'quantity': 1,
                'systemQuantity': product.getStockCounts(request.store).level,
                'nsbiQuantity': product.getNSBICount(request.store)
            }
            stockTakeLines.append(currentItem)
        else:
            currentItem['quantity'] = int(line[3])
    stocktakeObj = {
        'status': 'SAVED',
        'stockTakeLines': stockTakeLines
    }
    stockTake = stockTakeFromJson(stocktakeObj, request.staff)
    returnUrls = {
        "open" : reverse('stock:openStockTake', args=[stockTake.id]),
    }
    jsonResponse = json.dumps(returnUrls)
    return HttpResponse(jsonResponse)

@access_required('stock')
@login_required()
def saveStockTake(request):
    if ('stockTakeData' in request.POST) and request.POST['stockTakeData'].strip():
        stockTakeData = json.loads(request.POST['stockTakeData'], encoding="utf-8")
        stockTake = stockTakeFromJson(stockTakeData, request.staff)
        returnUrls = {
            "open" : reverse('stock:openStockTake', args=[stockTake.id]),
        }
        jsonResponse = json.dumps(returnUrls)
        return HttpResponse(jsonResponse)

@access_required('stock')
@login_required()
def openStockTake(request, stocktake_id):
    context = {
        'products': Product.objects.all().filterReadAll(request.store)[:25]
    }
    stocktake = get_object_or_404(StockTake, pk=stocktake_id)
    updatedContext = {
        'stockTakeData' : json.dumps(jsonFromStockTake(stocktake)),
        'stocktake' : stocktake,
    }
    context.update(updatedContext)
    if stocktake.status == "SAVED":
        return render(request, 'stock/stocktake/new.html', context)
    else:
        return render(request, 'stock/stocktake/completed.html', context)

@access_required('stock')
@login_required()
def searchClaim(request, type):
    claim = Claim.objects.all().filter(store=request.store) #filter store stocktake

    if type =="SAVED":
        claim = claim.filter(status="SAVED")
    else:
        claim = claim.filter(status=type)

    context = filterGenericSearchQuery(claim, [], request.GET)

    context.update({
        'filter' : type,
        'entityName' : "Claim"
    })

    return render(request, 'stock/claim/search.html', context)

@access_required('stock')
@login_required()
def claimHome(request):
    context = {
        'pending': Claim.objects.all().filter(store=request.store).filter(Q(status="SAVED") | Q(status="PENDING")).order_by('-created'),
        'completed': Claim.objects.all().filter(store=request.store, status="COMPLETED").order_by('-created')[:25],
    }
    return render(request, 'stock/claim/dashboard.html', context)

@access_required('stock')
@login_required()
def newClaim(request):
    context = {}
    return render(request, 'stock/claim/new.html', context)

@access_required('stock')
@login_required()
def saveClaim(request):
    if ('claimData' in request.POST) and request.POST['claimData'].strip():
        data = json.loads(request.POST['claimData'], encoding="utf-8")
        claim = claimFromJson(data, request.staff)
        returnUrls = {
            "open" : reverse('stock:openClaim',args=[claim.id]),
        }
        jsonResponse = json.dumps(returnUrls)
        return HttpResponse(jsonResponse)

@access_required('stock')
@login_required()
def openClaim(request, claim_id):
    claim = get_object_or_404(Claim, pk=claim_id)
    claimData = json.dumps(jsonFromClaim(claim))
    context = {
        'claimData' : claimData,
        'claim' : claim,
    }
    if claim.status == "SAVED":
        return render(request, 'stock/claim/new.html', context)
    elif claim.status == "PENDING":
        return render(request, 'stock/claim/completed.html', context)
    else: #COMPLETED
        return render(request, 'stock/claim/completed.html', context)

class ManualStockMovementCreateView(LoginAndStockPrivelege, CreateView):
    model = ManualStockMovement
    form_class = ManualStockMovementForm
    template_name = 'stock/movement/create.html'

    def form_valid(self, form):
        movement = form.save(commit=False)
        movement.createdBy = self.request.staff
        movement.save()
        quantity = form.cleaned_data.get('quantity')
        product = get_object_or_404(Product, pk=form.cleaned_data.get('product'))
        staff = self.request.staff
        if form.cleaned_data.get('type') == 'IN':
            quantity = quantity * -1
        product.deltaStockCounts(staff.store, quantity, reference=movement, referenceType='Manual', purchaseNet=form.cleaned_data.get('purchaseNet'))
        return HttpResponseRedirect(reverse('core:viewProduct', args=(product.id,)))

class InventoryAjaxLookupView(LoginRequiredMixin, BRListView):
    model = StoreInventoryItem
    template_name = 'stock/inventory/search-ajax-main.html'
    paginate_by = 30

    def get_queryset(self):
        movements = StoreInventoryItem.objects.all().filter(inventory__store=self.request.store)
        #dynamic filter based on request.POST or request.GET
        q = self.request.GET.get('q') or self.request.POST.get('q') or ''
        if len(q.strip()):
            movements = movements.filter(get_query(q, ['inventory__product__model']))
        exclude_ids = json.loads(self.request.GET.get('exclude') or self.request.POST.get('exclude') or '[]')
        movements = movements.exclude(id__in=exclude_ids)
        return movements.order_by('-id')[:30]

#merchandiser
from brutils.generic.views import LoginRequiredMixin, BRListView
from django.views.generic import DetailView
from core.models import Product, ProductCategory, Brand
from stock.models import StoreInventory, Store
from django.db.models import Sum, Q
from datetime import datetime
from core.models import Deal

#Merchandiser.
class MerchandiserSearchMixin(object):
    def doSearchFilters(self, products):
        params = {}
        current = self.request.GET.getlist('current') or self.request.POST.getlist('current') or []
        superceded = self.request.GET.getlist('chkSuperceeded') or self.request.POST.getlist('chkSuperceeded') or []
        obsolete = self.request.GET.getlist('chkObsolete') or self.request.POST.getlist('chkObsolete') or []
        sortTypes = self.request.GET.getlist('sortTypes') or self.request.POST.getlist('sortTypes') or []
        category = self.request.GET.getlist('category') or self.request.POST.getlist('category') or []
        stores = self.request.GET.getlist('stores') or self.request.POST.getlist('stores') or []
        brand = self.request.GET.getlist('brand') or self.request.POST.getlist('brand') or []
        SOHFilter = self.request.GET.getlist('chkSOH') or self.request.POST.getlist('chkSOH') or []
        removePricing = self.request.GET.getlist('chkRemovePricing') or self.request.POST.getlist('chkRemovePricing') or []
        removeHistory = self.request.GET.getlist('chkRemoveHistory') or self.request.POST.getlist('chkRemoveHistory') or []
        reverseSort = self.request.GET.getlist('chkReverseSort') or self.request.POST.getlist('chkReverseSort') or []

        removePricing = filter(len, removePricing)
        if len(removePricing):
            params['removePricingTable'] = True
        params['chkRemovePricing'] = ','.join([x for x in removePricing]) if len(removePricing) else ''

        removeHistory = filter(len, removeHistory)
        if len(removeHistory):
            params['removeHistoryTable'] = True
        params['chkRemoveHistory'] = ','.join([x for x in removeHistory]) if len(removeHistory) else ''

        #filter by SOH
        SOHFilter = filter(len, SOHFilter)
        if len(SOHFilter):
            inventoryItems = StoreInventory.objects.filter(store=self.request.store, level__gte=1)
            productIdList = []
            for inventory in inventoryItems:
                productIdList.append(inventory.product.id)
            products = products.filter(id__in=productIdList)
        params['chkSOH'] = ','.join([x for x in SOHFilter]) if len(SOHFilter) else ''

        #filter by status
        both = False
        supercededFlag = False
        obsoleteFlag = False
        try:
            if superceded[0] == "superceded" and obsolete[0] == "obsolete":
                both = True
        except IndexError:
            pass
        try:
            if superceded[0] == "superceded":
                supercededFlag = True
        except IndexError:
            pass
        try:
            if obsolete[0] == "obsolete":
                obsoleteFlag = True
        except IndexError:
            pass
        if both:
            params['chkSuperceeded'] = ','.join([x for x in superceded]) if len(superceded) else ''
            params['chkObsolete'] = ','.join([x for x in obsolete]) if len(obsolete) else ''
        elif supercededFlag:
            products = products.filter().exclude(status='obsolete')
            params['chkSuperceeded'] = ','.join([x for x in superceded]) if len(superceded) else ''
        elif obsoleteFlag:
            products = products.filter().exclude(status='superceded')
            params['chkObsolete'] = ','.join([x for x in obsolete]) if len(obsolete) else ''
        else:
            current.append("current")
            products = products.filter(status='current')
            params['current'] = ','.join([x for x in current]) if len(current) else ''

        #filter by category
        category = filter(len, category)
        if len(category):
            categoryList = [int(x) for x in category]
            products = products.filter(Q(category__id__in=categoryList) | Q(category__parentCategory__id__in=categoryList) | Q(category__parentCategory__parentCategory__id__in=categoryList))
        params['category'] = ','.join([x for x in category]) if len(category) else ''

        #filter by brand
        brand = filter(len, brand)
        if len(brand):
            brandList = [int(x) for x in brand]
            products = products.filter(brand__id__in=brandList)
        params['brand'] = ','.join([x for x in brand]) if len(brand) else ''

        #filter by stores
        stores = filter(len, stores)
        if len(stores):
            try:
                inventoryItems = StoreInventory.objects.filter(store=stores[0])
                productIdList = []
                for inventory in inventoryItems:
                    productIdList.append(inventory.product.id)
                products = products.filter(id__in=productIdList)
                store = Store.objects.filter(id=stores[0])
                params['storeToFilter'] = store
            except IndexError:
                pass
        params['stores'] = ','.join([x for x in stores]) if len(stores) else ''

        # set sort type
        if not sortTypes:
            products = products.order_by('-goPrice')
        try:
            if sortTypes[0] == "0":
                products = products.order_by('-tradePrice')
            elif sortTypes[0] == "1":
                products = products.order_by('-goPrice')
            elif sortTypes[0] == "2":
                products = products.order_by('brand__brand')
            elif sortTypes[0] == "3":
                products = products.order_by('model')
            elif sortTypes[0] == "4":
                products = products.order_by('description')
            elif sortTypes[0] == "5":
                products = products.order_by('category__name')
            elif sortTypes[0] == "6":
                products = products.order_by('-tradePrice')
            else:
                products = products.order_by('-goPrice')
        except IndexError:
            pass
        params['sortTypes'] = ','.join([x for x in sortTypes]) if len(sortTypes) else ''

        reverseSort = filter(len, reverseSort)  # set reverse sort type
        if len(reverseSort):
            if not sortTypes:
                products = products.order_by('goPrice')
            try:
                if sortTypes[0] == "0":
                    products = products.order_by('tradePrice')
                elif sortTypes[0] == "1":
                    products = products.order_by('goPrice')
                elif sortTypes[0] == "2":
                    products = products.order_by('-brand__brand')
                elif sortTypes[0] == "3":
                    products = products.order_by('-model')
                elif sortTypes[0] == "4":
                    products = products.order_by('-description')
                elif sortTypes[0] == "5":
                    products = products.order_by('-category__name')
                elif sortTypes[0] == "6":
                    products = products.order_by('tradePrice')
                else:
                    products = products.order_by('goPrice')
            except IndexError:
                pass
            params['sortTypes'] = ','.join([x for x in sortTypes]) if len(sortTypes) else ''
        params['chkReverseSort'] = ','.join([x for x in reverseSort]) if len(reverseSort) else ''
        params['count'] = products.count()
        self.context_append['params'] = params
        return products


class ProductPriceLookupView(LoginRequiredMixin, BRListView, MerchandiserSearchMixin):
    model = Product
    template_name = 'stock/merchandiser/search.html'
    paginate_by = 30
    context_object_name = 'products'
    queryset = Product.objects.all()

    def get_queryset(self):
        chkRemovePricing = self.request.GET.getlist('chkRemovePricing') or self.request.POST.getlist('chkRemovePricing') or []
        chkRemovePricing = filter(len, chkRemovePricing)
        if len(chkRemovePricing):
            self.paginate_by = 50

        chkRemoveHistory = self.request.GET.getlist('chkRemoveHistory') or self.request.POST.getlist('chkRemoveHistory') or []
        chkRemoveHistory = filter(len, chkRemoveHistory)
        if len(chkRemoveHistory):
            self.paginate_by = 100

        #dynamic filter based on request.POST or request.GET
        products = Product.objects.all().filterReadAll(self.request.store)
        return super(ProductPriceLookupView, self).doSearchFilters(products)

    def get_context_data(self, **kwargs):
        sortTypesList = [
            {'id': '0', 'name': 'Net'},
            {'id': '1', 'name': 'GO'},
            {'id': '3', 'name': 'Model'},
            {'id': '4', 'name': 'Description'},
            {'id': '5', 'name': 'Category'},
            {'id': '6', 'name': 'Invoice'},
            {'id': '2', 'name': 'Brand'}
        ]
        context = super(ProductPriceLookupView, self).get_context_data(**kwargs)
        context['sortTypes'] = sortTypesList
        context['categories'] = ProductCategory.objects.all().filterReadAll(self.request.store)
        context['brands'] = Brand.objects.all().filterReadAll(self.request.store)
        context['stores'] = Store.objects.all()
        return context

class SalesAnalysisHomeView(LoginRequiredMixin, BRListView, MerchandiserSearchMixin):
    model = Product
    template_name = "stock/merchandiser/dashboard.html"

class ProductDetailView(DetailView):
    model = Product
    template_name = 'stock/merchandiser/view-product.html'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        product_stock_levels = StoreInventory.objects.filter(product=self.object, level__gt=0)
        product_stock_levels_count = product_stock_levels.aggregate(total=Sum('level'))
        context['stock_levels'] = product_stock_levels
        context['stock_level_total'] = 0 if product_stock_levels_count['total'] is None else product_stock_levels_count['total']
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















