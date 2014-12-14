from decimal import Decimal
from datetime import timedelta
import json

from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, HttpResponse, redirect
from django.core.urlresolvers import reverse
from django.utils import timezone

from core.models import *
from b2b.models import *
from b2b.forms import *

from lib.narta.codecs import GenericReader, POResponder
from lib.jsonStringify.utility import decodeDate
from lib.jsonStringify.invoices import invoiceFromJson, jsonFromInvoice, jsonRevertFromInvoice
from lib.jsonStringify.orders import orderFromJson, jsonFromOrder
from lib.jsonStringify.b2bOrders import jsonFromB2BInvoice
from lib.jsonStringify.recons import reconFromJson

from lib.queries import get_query
from lib.search import filterGenericSearchQuery

from brutils.decorators import access_required
from brutils.generic.views import *

from vw.invoice_to_stock_movement import shortcuts

D = Decimal

@access_required('stock')
@login_required()
def stockOrderHome(request):
    storeOrders = StockOrder.objects.filter(Q(orderedBy__store=request.store) | Q(store=request.store))
    pending = storeOrders.filter(status="PENDING").order_by('-modified')[:25]
    saved = storeOrders.filter(status="SAVED").order_by('-modified')[:25]
    completed = storeOrders.filter(Q(status__exact="ACCEPTED")|Q(status__exact="REJECTED")|Q(status__exact="PARTIAL-ACCEPTED")).order_by('-modified')[:25]
    context = {
        'pending': pending,
        'saved': saved,
        'completed': completed,
    }
    return render(request, 'b2b/ordering/dashboard.html', context)

@access_required('stock')
@login_required()
def searchStockOrder(request, type):
    orders = StockOrder.objects.filter(Q(orderedBy__store=request.store) | Q(store=request.store))

    if type =="SAVED":
        orders = orders.filter(status="SAVED")
    elif type=="COMPLETED":
        orders = orders.filter(Q(status__exact="ACCEPTED")|Q(status__exact="REJECTED")|Q(status__exact="PARTIAL-ACCEPTED"))
    else:
        orders = orders.filter(status=type)

    orders = orders.order_by('-modified')
    context = filterGenericSearchQuery(orders, [], request.GET)

    context.update({
        'filter' : type,
        'entityName' : "StockOrder"
    })

    return render(request, 'b2b/ordering/search.html', context)

@access_required('stock')
@login_required()
def newStockOrder(request):
    purchasers = Brand.getUniquePurchasers()
    staffMember = request.staff
    stores = None
    jsonStores = None
    if request.store.isHead == True:
        stores = request.store.group.getImmediateAndBelowStores()
        jsonStores = json.dumps([item for item in stores.values('code', 'id')])

    #generate an order reference number
    staffCount = int(StockOrder.objects.filter(orderedBy=staffMember).count()) + 1
    orderRef = "%s-%s-%i" % (staffMember.store.code, staffMember.username, staffCount)
    tomorrow = datetime.datetime.now() + timedelta(days=1)
    after3months = datetime.datetime.now() + timedelta(days=3*30)

    context = {
        'stores': stores,
        'jsonStores': jsonStores,
        'orderRef': orderRef,
        'purchasers': purchasers,
        'staffCount': staffCount,
        'tomorrow': tomorrow,
        'after3months': after3months,
    }

    return render(request, 'b2b/ordering/new.html', context)

@access_required('stock')
@login_required()
def bookingStockOrder(request, order_id):
    #books in all stock in post data.
    bookings = json.loads(request.POST.get('bookings'))
    order = get_object_or_404(StockOrder, pk=order_id)
    for booking in bookings:
        line = StockOrderLine.objects.get(pk=booking.get('id'))
        line.item.deltaStockCounts(request.store, int(booking.get('quantity'))*-1, order, "Stock Order", line.unitNet)
    jsonResponse = json.dumps({
        "openOrder" : reverse('b2b:openOrder', args=[order_id]),
    })
    return HttpResponse(jsonResponse)

@access_required('stock')
@login_required()
def calcNetGivenInvoice(request):
    id = None
    invoicePrice = D('0.00')
    returnVal = D('0.00')
    returnValEx = D('0.00')

    if ('id' in request.POST) and request.POST['id'].strip():
        id = request.POST['id']
        product = get_object_or_404(Product, pk=id)
        if ('invoicePrice' in request.POST) and request.POST['invoicePrice'].strip():
            invoicePrice = D(request.POST['invoicePrice'])
            returnVal = product.calculateSPANNet(invoicePrice)
            returnValEx = returnVal/D(settings.GST)

    returnDict = {
        "result": "%.2f" % returnVal,
        "resultExGST": "%.2f" % returnValEx
    }

    return HttpResponse(json.dumps(returnDict))

@access_required('stock')
@login_required()
def saveOrder(request):
    if request.method == 'POST':
        if ('orderData' in request.POST) and request.POST['orderData'].strip():
            orderData = json.loads(request.POST['orderData'],encoding="utf-8")
            stockOrder = orderFromJson(orderData, request.staff)
            request.store.updateOpenToBuy()
        returnUrls = {
            "openOrder" : reverse('b2b:openOrder', args=[stockOrder.id]),
        }
        jsonResponse = json.dumps(returnUrls)
        return HttpResponse(jsonResponse)

@access_required('stock')
@login_required()
def openOrder(request, order_id):
    #new order code
    purchasers = Brand.getUniquePurchasers()
    staffMember = request.staff
    stores = None
    jsonStores = None
    if request.store.isHead == True:
        stores = request.store.group.getImmediateAndBelowStores()
        jsonStores = json.dumps([item for item in stores.values('code', 'id')])

    #generate an order reference number
    staffCount = int(StockOrder.objects.filter(orderedBy=staffMember).count()) + 1
    orderRef = "%s-%s-%i" % (staffMember.store.code, staffMember.username, staffCount)
    tomorrow = datetime.datetime.now() + timedelta(days=1)
    after3months = datetime.datetime.now() + timedelta(days=3*30)

    context = {
        'stores': stores,
        'jsonStores': jsonStores,
        'orderRef': orderRef,
        'purchasers': purchasers,
        'staffCount': staffCount,
        'tomorrow': tomorrow,
        'after3months': after3months,
    }
    #end of new order code.

    #loadingOrderCode
    order = get_object_or_404(StockOrder, pk=order_id)
    etOrder = ElectronicStockOrder.objects.get(stockOrder=order) if order.is_et else None
    orderData = jsonFromOrder(order)

    loadContext = {
        'order': order,
        'etOrder': etOrder,
        'orderData': json.dumps(orderData),
    }
    context.update(loadContext)
    #end of loadingOrderCode

    if order.status =="SAVED":
        return render(request, 'b2b/ordering/new.html', context)
    if order.status =="PENDING":
        return render(request, 'b2b/ordering/pending.html', context)
    if order.status =="ACCEPTED" or order.status == "REJECTED" or order.status == "PARTIAL-ACCEPTED":
        return render(request, 'b2b/ordering/pending.html', context)

@access_required('stock')
@login_required()
def searchLocalities(request):
    if ('locality' in request.POST) and request.POST['locality'].strip():
        locality = request.POST['locality']
        localities = Postcode.objects.filter(locality__istartswith=locality).values('locality', 'code', 'state')
    return HttpResponse(json.dumps([item for item in localities]))

@access_required('stock')
@login_required()
def viewPurchaseOrder(request, etOrder_id):
    etOrder = get_object_or_404(ElectronicStockOrder,pk=etOrder_id)
    OrderLines = StockOrderLine.objects.filter(order=etOrder.stockOrder)
    po = GenericReader(etOrder.sentRAW).mapped
    context = {
        "etOrder": etOrder,
        "po": po,
        "orderLines": OrderLines,
    }
    return render(request, 'b2b/ordering/print/po.html', context)

@access_required('stock')
@login_required()
def viewPurchaseOrderResponse(request, etOrder_id):
    etOrder = get_object_or_404(ElectronicStockOrder, pk=etOrder_id)
    OrderLines = StockOrderLine.objects.filter(order=etOrder.stockOrder)
    por = GenericReader(etOrder.responseRAW).mapped
    context = {
        "etOrder" : etOrder,
        "por" : por,
        "orderLines" : OrderLines,
    }
    return render(request, 'b2b/ordering/print/por.html', context)

@login_required()
def HOInvoicingHome(request):
    twoYearsEarlier = datetime.date(datetime.date.today().year-2, 7, 1)
    context = {
        'pending': HeadOfficeInvoice.objects.all().filter(Q(reconciledDate__isnull=True) | Q(chargedDate__isnull=False)).order_by('-createdDate')[:100],
    }
    return render(request, 'b2b/invoicing/dashboard.html', context)





@login_required()
def newHOInvoice(request):
    shortcuts.initialiseMerchandiserSession(request)
    distributors = Brand.getUniqueDistributors()
    stores = Store.objects.all()
    stores = stores.exclude(code="VW")  #  can only create new virtual warehouse invoices from inside the VW module
    context = {
        'distributors': distributors,
        'stores': stores,
    }
    return render(request, 'b2b/invoicing/new.html', context)


@login_required()
def deleteHOInvoice(request, invoice_id):
    HoInvoice = get_object_or_404(HeadOfficeInvoice, pk=invoice_id)
    if HoInvoice.chargedBy is None and HoInvoice.reconciledBy is None and request.store.displayHOMenu():
        HoInvoice.delete()
    #update the open to buys
    request.store.updateOpenToBuy()
    return redirect("b2b:HOInvoicingHome")

@login_required()
def reverseHOInvoice(request, invoice_id):
    distributors = Brand.getUniqueDistributors()
    stores = Store.objects.all()
    context = {
        'distributors': distributors,
        'stores': stores,
    }
    #load older invoice
    HoInvoice = get_object_or_404(HeadOfficeInvoice, pk=invoice_id)
    HOInvoiceJson = jsonRevertFromInvoice(HoInvoice)
    updatedContext = {
        'invoiceData': json.dumps(HOInvoiceJson),
    }
    context.update(updatedContext)
    return render(request, 'b2b/invoicing/new.html', context)

@login_required()
def saveHOInvoice(request):
    if ('invoiceData' in request.POST) and request.POST['invoiceData'].strip():
        HOInvoiceData = json.loads(request.POST['invoiceData'], encoding="utf-8")
        HOInvoice = invoiceFromJson(HOInvoiceData, request.staff, request.session)
        returnUrls = {
            "openInvoice" : reverse('b2b:openHOInvoice', args=[HOInvoice.id]),
        }
        jsonResponse = json.dumps(returnUrls)
        request.store.updateOpenToBuy()
        return HttpResponse(jsonResponse)

@login_required()
def openHOInvoice(request, invoice_id):
    shortcuts.initialiseMerchandiserEditSession(request)
    # new HO Loading Context
    # dummy commit
    distributors = Brand.getUniqueDistributors()
    stores = Store.objects.all()
    context = {
        'distributors': distributors,
        'stores': stores,
    }
    #existing HO Invoice Loading
    HoInvoice = get_object_or_404(HeadOfficeInvoice, pk=invoice_id)
    HOInvoiceJson = jsonFromInvoice(HoInvoice)
    updatedContext = {
        'invoiceData': json.dumps(HOInvoiceJson),
        'invoice': HoInvoice,
    }     
    context.update(updatedContext)
    if request.store.displayHOMenu() and request.GET.get('viewable', '') is '':
        #HO store editing an invoice
        if HoInvoice.chargedBy is None and HoInvoice.reconciledBy is None:
            return render(request, 'b2b/invoicing/new.html', context)
        else:
            return render(request, 'b2b/invoicing/view.html', context)
    elif request.store == HoInvoice.store:
        return render(request, 'b2b/invoicing/store-view.html', context)
    else:
        #store trying to access an invoice that isn't theirs
        return redirect('b2b:invoicesAll')

@login_required()
def searchHOInvoices(request, type):
    invoices = HeadOfficeInvoice.objects.all()

    if request.store.displayHOMenu() and request.GET.get('viewable', '') is '':
        #HO searching all invoices
        pass
    else:
        #Store Searching for HO Invoices
        invoices = invoices.filter(store=request.store) #filter stores invoices.

    if type == "PENDING":
        invoices = invoices.filter(Q(chargedDate__isnull=True) | Q(reconciledDate__isnull=True))
    elif type == "COMPLETED": #within last 2 financial years
        twoYearsEarlier = datetime.date(datetime.date.today().year-2, 7, 1)
        invoices = invoices.filter(chargedDate__gte=twoYearsEarlier, reconciledDate__isnull=False)
    elif type == "ARCHIVED":
        twoYearsEarlier = datetime.date(datetime.date.today().year-2, 7, 1)
        invoices = invoices.filter(chargedDate__lte=twoYearsEarlier, reconciledDate__isnull=False)

    #get only invoices that have been charged
    context = filterGenericSearchQuery(invoices, ['invoiceNumber', 'orderReference', 'storeInformation', 'headofficeinvoiceline__item__model'], request.GET)

    context.update({
        'entityName': "Invoice",
        'filter': type,
    })

    if request.store.displayHOMenu() and request.GET.get('viewable', '') is '':
        #HO searching all invoices
        return render(request, 'b2b/invoicing/search.html', context)
    else:
        #Store Searching for HO Invoices
        return render(request, 'b2b/store-invoicing/search.html', context)

@login_required()
def searchHOInvoicesAjax(request):
    #this view is for recons
    invoices = HeadOfficeInvoice.objects.all()
    endDate = decodeDate(request.GET.get('endDate') or request.POST.get('endDate'))
    distributor = request.GET.get('distributor') or request.POST.get('distributor')
    format = request.GET.get('format') or request.POST.get('format')

    debitTypes = settings.DEBIT_TYPES
    jsonList = []

    if format == "recon":
        invoices = invoices.filter(distributor__distributor=distributor)
        invoices = invoices.filter(reconciledDate__isnull=True).filter(invoiceDate__lte=endDate)
        jsonList = [
            {
                'id': invoice.id,
                'invoiceNum': invoice.invoiceNumber,
                'invoiceDate': invoice.invoiceDate.strftime('%d/%m/%Y'),
                'store': invoice.store.name,
                'orderNum': invoice.orderReference,
                'debit': '%.2f' % (invoice.invTotal if invoice.type in debitTypes else 0.00),
                'credit': '%.2f' % (0.00 if invoice.type in debitTypes else invoice.invTotal),
                'balance': '', #TODO: total of extended credit owing
                'extCredit': invoice.extendedCredit,
                'dueDate': invoice.dueDate.strftime('%d/%m/%Y') if invoice.dueDate is not None else '',
                'comment': ''
            }
            for invoice in invoices
        ]

    #dump json in appropriate format.
    return HttpResponse(json.dumps(jsonList))

class B2BSearchView(BRListView):
    model = B2BInvoice
    template_name = 'b2b/invoicing/search-b2b.html'
    paginate_by = 30

    def get_queryset(self):
        #dynamic filter based on request.POST or request.GET
        invoices = B2BInvoice.objects.all()

        #if(len(invoices) <=0): #testing b2b invoice to invoice TODO:comment this out when going live.
        #    B2BInvoice.testB2BInvoice()
        #    invoices = B2BInvoice.objects.all()
        #search by simple query
        q = self.request.GET.get('q') or self.request.POST.get('q') or ''
        self.context_append['q'] = q
        if len(q.strip()):
            invoices = invoices.filter(get_query(q, ['store__name', 'invoiceNumber', 'orderNumber']))
        return invoices.order_by('-id')[:300]

@login_required()
def b2bInvoiceToInvoice(request, invoice_id):
    b2binvoice = get_object_or_404(B2BInvoice, id=invoice_id)
    data = jsonFromB2BInvoice(b2binvoice)
    return HttpResponse(json.dumps(data))

#Recons
@login_required()
def searchRecons(request, type):
    entities = Recon.objects.all()

    if type =="SAVED":
        entities = entities.filter(status="SAVED")
    else:
        entities = entities.filter(status=type)

    context = filterGenericSearchQuery(entities, [], request.GET)

    context.update({
        'filter': type,
        'entityName': "Reconciliation"
    })

    return render(request, 'b2b/recon/search.html', context)

@login_required()
def reconHome(request):
    context = {
        'completed': Recon.objects.all().filter(status="COMPLETED").order_by('-created')[:100],
    }
    return render(request, 'b2b/recon/dashboard.html', context)

@login_required()
def newRecon(request):
    context = {
        'invoices': HeadOfficeInvoice.objects.all().filter(reconciledDate__isnull=True)[:25],
        'distributors': Brand.getUniqueDistributors()
    }
    return render(request, 'b2b/recon/new.html', context)

@login_required()
def saveRecon(request):
    if ('reconData' in request.POST) and request.POST['reconData'].strip():
        reconData = json.loads(request.POST['reconData'], encoding="utf-8")
        recon = reconFromJson(reconData, request.staff)
        returnUrls = {
            "open": reverse('b2b:reconHome'),
        }
        jsonResponse = json.dumps(returnUrls)
        return HttpResponse(jsonResponse)

@login_required()
def reverseRecon(request, recon_id):
    recon = get_object_or_404(Recon, pk=recon_id)
    for line in recon.reconlines_set.all():
        invoiceToReverse = line.invoice
        invoiceToReverse.reconciledBy = None
        invoiceToReverse.reconciledDate = None
        invoiceToReverse.save()
        line.delete()
    recon.delete()
    return redirect('b2b:reconHome')
#recons

#claims
@login_required()
def searchCharges(request):
    entities = Charge.objects.all()
    context = filterGenericSearchQuery(entities, ['store__name'], request.GET)
    context.update({
        'filter': type,
        'entityName': "Charge"
    })
    return render(request, 'b2b/charge/search.html', context)

@login_required()
def chargesHome(request):
    context = {
        'completed': Charge.objects.all().order_by('-chargeGroup')[:100],
    }
    return render(request, 'b2b/charge/dashboard.html', context)

@login_required()
def produceInvoiceList(request):
    #newCharge
    template = 'b2b/charge/new.html'
    context = {
        'stores': [],
    }
    if len(request.POST.get('endDate', '')):
        template = 'b2b/charge/invoiceList.html'
        endDate = decodeDate(request.GET.get('endDate') or request.POST.get('endDate'))
        context.update(getChargeInvoices(endDate))
    return render(request, template, context)

def produceInvoiceLinesList(request):
    template = 'b2b/charge/invoiceLineList.html'
    context = {
        'stores': [],
    }
    endDate = decodeDate(request.GET.get('endDate') or request.POST.get('endDate'))
    context.update(getChargeInvoices(endDate))
    return render(request, template, context)

@login_required()
def produceChargeSheet(request):
    endDate = decodeDate(request.GET.get('endDate') or request.POST.get('endDate'))
    obj = getChargeInvoices(endDate)
    group = Charge.getMostRecentChargeGroup()+1
    debitTypes = settings.DEBIT_TYPES

    for store in obj.get('stores'):
        dbStore = get_object_or_404(Store, pk=store.get('id'))
        charge = Charge(store=dbStore, chargeDate=endDate, createdBy=request.staff, chargeGroup=group)
        charge.save()
        #gonna assume extended credit doesn't drag on for longer than a month
        dbStore.extendedCreditTotals = D('0.00')
        for invoice in store.get('storeInvoices'):
            dbInvoice = get_object_or_404(HeadOfficeInvoice, pk=invoice.get('id'))
            dbInvoice.chargedBy = request.staff
            dbInvoice.chargedDate = charge.created
            dbInvoice.save()
            #each invoice affects the stores currentDebt or extendedCreditAmount
            """
                take the spannetexgst amount and that's what affects the open to buy Hamza 12/11/2014.
                20% difference between the 2 etc etc.
            """
            if dbInvoice.extendedCredit:
                dbStore.extendedCreditTotals += (dbInvoice.netTotal if dbInvoice.type not in debitTypes else dbInvoice.netTotal*-1)
            dbStore.currentDebt += (dbInvoice.netTotal if dbInvoice.type not in debitTypes else dbInvoice.netTotal*-1)
            line = ChargeLine(charge=charge, invoice=dbInvoice)
            line.save()
        dbStore.save()
        dbStore.updateOpenToBuy()

    return redirect('b2b:chargesHome')

def printSummaryChargeSheet(request, charge_id):
    template = 'b2b/charge/print.html'
    charge = get_object_or_404(Charge, pk=charge_id)
    stores = Charge.objects.all().filter(chargeGroup=charge.chargeGroup).values_list('store__id', flat=True).distinct()
    return render(request, template, getChargeInvoices(charge.chargeDate, storeList=stores, getChargedOnly=True))

def printStoreChargeSheet(request, charge_id):
    template = 'b2b/charge/print.html'
    charge = get_object_or_404(Charge, pk=charge_id)
    return render(request, template, getChargeInvoices(charge.chargeDate, storeList=[charge.store.id], getChargedOnly=True))

def getChargeInvoices(endDate, storeList=None, getChargedOnly=False):
    #this will return an obj that will have all the information for the invoices entered in a month upto a certain day
    #start date will always be the start of the month
    endDate = endDate
    startDate = datetime.datetime(endDate.year, endDate.month, 1)
    invoices = HeadOfficeInvoice.objects.all().filter(Q(invoiceDate__lte=endDate) & Q(invoiceDate__gte=startDate)).order_by('store__name')
    if getChargedOnly:
        invoices = invoices.filter(chargeline__isnull=False)
    debitTypes = settings.DEBIT_TYPES

    completeTotal = 0
    returnObj = {}
    stores = []
    storeList = invoices.values_list('store__id', flat=True).distinct() if storeList is None else storeList

    for store in storeList:
        #append to overall result
        storeInvoices = []
        storeTotal = 0
        for invoice in invoices.filter(store__id=store).order_by('distributor'):
            storeTotal += invoice.invTotal if invoice.type not in debitTypes else invoice.invTotal*-1
            obj = {
                'id': invoice.id,
                'invoiceNum': invoice.invoiceNumber,
                'store': invoice.store,
                'distributor': invoice.distributor.distributor,
                'invoiceDate': invoice.invoiceDate.strftime('%d/%m/%Y'),
                'orderReference': invoice.orderReference,
                'type': invoice.type,
                'netInc': invoice.invTotal if invoice.type not in debitTypes else invoice.invTotal*-1,
                'extCredit': invoice.dueDate.strftime('%d/%m/%Y') if invoice.dueDate and invoice.extendedCredit is not None else '',
                'freight': invoice.freight if invoice.type not in debitTypes else invoice.freight*-1,
                'freightInc': invoice.freight*Decimal(settings.GST) if invoice.type not in debitTypes else invoice.freight*Decimal(settings.GST)*-1,
                'lines': [
                    {
                        'invoiceID': invoiceLine.invoice.id,
                        'store': invoiceLine.invoice.store,
                        'distributor': invoiceLine.invoice.distributor.distributor,
                        'invoiceNum': invoiceLine.invoice.invoiceNumber,
                        'invoiceDate': invoiceLine.invoice.invoiceDate.strftime('%d/%m/%Y'),
                        'invoiceOrderRef': invoiceLine.invoice.orderReference,
                        'model': invoiceLine.item.model,
                        'invoiceType': invoiceLine.invoice.type,
                        'unitPrice': invoiceLine.unitPrice,
                        'quantity': invoiceLine.quantity,
                        'netInc': invoiceLine.invoicePrice if invoiceLine.invoice.type not in debitTypes else invoiceLine.invoicePrice*-1,
                        'extCredit': invoiceLine.invoice.dueDate.strftime('%d/%m/%Y') if invoiceLine.invoice.dueDate and invoiceLine.invoice.extendedCredit is not None else '',
                    }
                    for invoiceLine in invoice.headofficeinvoiceline_set.all()
                ]
            }
            storeInvoices.append(obj)
        completeTotal += storeTotal
        stores.append({
            'storeTotal': storeTotal,
            'storeInvoices': storeInvoices,
            'id': store
        })
    returnObj.update({
        "endDate": endDate,
        "completeTotal": completeTotal,
    })
    returnObj.update({
        'stores': stores
    })
    return returnObj
#claims

#payments
class StorePaymentsListView(LoginAndAdminPrivelege, BRListView):
    model = StorePayment
    template_name = 'b2b/store-payments/list.html'

    def get_queryset(self):
        return StorePayment.objects.all().filter(store__pk=self.kwargs['pk']).order_by('-pk')

class StorePaymentsDeleteView(LoginAndAdminPrivelege, JSONDeleteView):
    model = StorePayment

    def get_object(self, *args, **kwargs):
        return StorePayment.objects.all().filter(store__pk=self.kwargs['pk']).latest('pk')

    def delete(self, request, *args, **kwargs):
        self.get_object().revertPayment()
        self.get_object().store.updateOpenToBuy()
        return super(StorePaymentsDeleteView, self).delete(self, request, *args, **kwargs)

class StorePaymentsCreateView(LoginAndAdminPrivelege, JSONUpdateView):
    model = StorePayment
    form_class = StorePaymentForm
    template_name = 'b2b/store-payments/create.html'

    def get_object(self, *args, **kwargs):
        store = get_object_or_404(Store, pk=self.kwargs['pk'])
        return StorePayment(store=store)

    def form_valid(self, form):
        m = form.save()
        m.processPayment()
        m.store.updateOpenToBuy()
        return HttpResponse(json.dumps({'success': True, }))
#/payments

@login_required()
def nteSim(request):
    entities = StockOrder.objects.filter(is_et=True)
    entities = entities.filter(Q(status__exact="PENDING"))
    context = filterGenericSearchQuery(entities, ['reference'], request.POST)
    context.update({
        'entityName': "Order"
    })
    return render(request, 'b2b/test-order/search.html', context)

@login_required()
def nteOrderAccept(request, order_id):
    stockOrder = StockOrder.objects.get(pk=order_id)
    etOrder = ElectronicStockOrder.objects.get(stockOrder=stockOrder)
    #create a generic response RAW
    etOrder.responseRAW = POResponder(etOrder.sentRAW, 29).PORRAW
    #add values : response RAW, responseValue, responseOrder, and responseDate to model
    etOrder.responseValue = 29
    etOrder.responseReceivedDate = datetime.datetime.now()
    etOrder.save()
    stockOrder.status = "ACCEPTED"
    stockOrder.save()
    #return
    return redirect('b2b:nteSim')

@login_required()
def nteOrderPartialAccept(request, order_id):
    stockOrder = StockOrder.objects.get(pk=order_id)
    etOrder = ElectronicStockOrder.objects.get(stockOrder=stockOrder)
    #create a generic response RAW
    etOrder.responseRAW = POResponder(etOrder.sentRAW, 4).PORRAW
    #add values : response RAW, responseValue, responseOrder, and responseDate to model
    etOrder.responseValue = 4
    etOrder.responseReceivedDate = datetime.datetime.now()
    etOrder.save()
    stockOrder.status = "PARTIAL-ACCEPTED"
    stockOrder.save()
    #return
    return redirect('b2b:nteSim')

@login_required()
def nteOrderReject(request, order_id):
    stockOrder = StockOrder.objects.get(pk=order_id)
    etOrder = ElectronicStockOrder.objects.get(stockOrder=stockOrder)
    #create a generic response RAW
    etOrder.responseRAW = POResponder(etOrder.sentRAW, 27).PORRAW
    #add values : response RAW, responseValue, responseOrder, and responseDate to model
    etOrder.responseValue = 27
    etOrder.responseReceivedDate = datetime.now()
    etOrder.save()
    stockOrder.status = "REJECTED"
    stockOrder.save()
    #return
    return redirect('b2b:nteSim')