from decimal import Decimal
from math import floor
from itertools import chain
import json
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

from brutils.decorators import access_required
from brutils.generic.views import JSONUpdateView, JSONDeleteView, JSONCreateView, LoginAndSalePrivelege, LoginAndAdminPrivelege, BRListView, StoreLevelObjectMixin
from pos.models import *
from pos.forms import *
from lib.jsonStringify.sales import saleFromJson, jsonFromSale
from lib.jsonStringify.utility import decodeReceivedText
from lib.search import filterGenericSearchQuery, getGenericCrudURLS
from lib.queries import get_query

# Create your views here.
@access_required('sale')
@login_required()
def home(request):
    terminal = Terminal.objects.get_or_create(store=request.store, name=1)
    terminals = Terminal.objects.filter(store=request.store)
    spanSize = int(floor(12/len(terminals))) #for span div
    context = {'terminals': terminals,
               'spanSize': spanSize}
    return render(request, 'pos/dashboard.html', context)

@access_required('sale')
@login_required()
def newSale(request, terminal_id=0):
    Terminal.objects.get_or_create(store=request.store, name=1)
    if terminal_id == 0: #if no terminal_id was passed get the first one
        terminal = Terminal.objects.filter(store=request.store)[0]
    else:
        terminal = get_object_or_404(Terminal, id=terminal_id)
    paymentMethods = PaymentMethod.objects.all().filterReadAll(request.store)
    customerForm = CustomerForm(store=request.store)

    context = {
        'terminal' : terminal,
        'customerForm' : customerForm,
        'paymentMethods': paymentMethods,
    }

    return render(request, 'pos/sales/new.html', context)

@access_required('sale')
@login_required()
def newSaleFromCustomer(request, customer_id, terminal_id=0):
    Terminal.objects.get_or_create(store=request.store, name=1)
    if terminal_id ==0: #if no terminal_id was passed get the first one
        terminal = Terminal.objects.filter(store=request.store)[0]
    else:
        terminal = get_object_or_404(Terminal, id=terminal_id)
    paymentMethods = PaymentMethod.objects.all().filterReadAll(request.store)
    customerForm = CustomerForm(store=request.store)
    customer = get_object_or_404(Customer, id=customer_id)
    sale = Sale(customer=customer)
    salesData = jsonFromSale(sale)

    context = {
        'terminal' : terminal,
        'customerForm' : customerForm,
        'paymentMethods': paymentMethods,
        'salesData': json.dumps(salesData),
    }

    return render(request, 'pos/sales/new.html', context)

@access_required('sale')
@login_required()
def openSale(request, terminal_id, sale_id):
    #base sale items.
    terminal = get_object_or_404(Terminal, id=terminal_id)
    paymentMethods = PaymentMethod.objects.all().filterReadAll(request.store)
    customerForm = CustomerForm(store=request.store)
    #saved sale specific
    sale = get_object_or_404(Sale, id=sale_id)
    printing = range(1, sale.getMostRecentGroupedBy()+1)#iterable for previous invoices
    salesData = jsonFromSale(sale)

    context = {
        'terminal': terminal,
        'customerForm': customerForm,
        'paymentMethods': paymentMethods,
        'walkInCustomerID': 4,
        #loadsale specific
        'sale': sale,
        'salesData': json.dumps(salesData),
        'printing': printing,
        #end
    }

    if sale.status == "COMPLETED":
        return render(request, 'pos/sales/completed.html', context)
    elif sale.status == "QUOTE":
        return render(request, 'pos/sales/new.html', context)
    else: #PENDING
        return render(request, 'pos/sales/pending.html', context)

@access_required('sale')
@login_required()
def saveSale(request, terminal_id):
    staffMember = get_object_or_404(Staff, pk=request.session['staff_id'])
    terminal = get_object_or_404(Terminal, id=terminal_id)
    groupedBy = 0
    if request.method == 'POST':
        if ('salesData' in request.POST) and request.POST['salesData'].strip():
            salesData = json.loads(request.POST['salesData'],encoding="utf-8")
            try:
                prevSale = Sale.objects.get(pk=salesData['id'])
            except Sale.DoesNotExist:
                prevSale = None
            #savesale
            sale = saleFromJson(salesData, terminal, staffMember)
            #create terminal Activity
            term = TerminalActivity.objects.get_or_create(sale=sale, terminal=terminal)[0]
            term.save()
            returnUrls = {
                "storePrint" : reverse('pos:printPaymentReceipt', args=[sale.id, groupedBy]),
                "openSale" : reverse('pos:openSale', args=[terminal.id, sale.id]),
            }
            jsonResponse = json.dumps(returnUrls)
            return HttpResponse(jsonResponse)

@access_required('sale')
@login_required()
def printSummaryReceipt(request, sale_id):
    '''
        0 is a summary of the invoices, anything above 0 will be
        the x payment they made to the sale.
    '''
    sale = Sale.objects.get(pk=sale_id)
    saleLines = SalesLine.objects.filter(sale=sale)
    context = {
        "sale": sale,
        "saleLines": saleLines,
        "payments": sale.getPayments(),
        "servedBy": sale.salesPerson.name
    }
    return render(request, 'pos/sales/print/storeSummary.html', context)

@access_required('sale')
@login_required()
def printPaymentReceipt(request, sale_id, payment_grouping):
    sale = Sale.objects.get(pk=sale_id)
    saleLines = SalesLine.objects.filter(sale=sale)
    groupedBy = int(payment_grouping)
    context = {
        "sale": sale,
        "saleLines": saleLines,
        "payments": sale.getGroupedPayments(groupedBy),
        "paidBefore": sale.getSalePaymentsTill(groupedBy),
        "balanceAfter": sale.getSaleBalanceAfter(groupedBy+1),
        "groupedBy": groupedBy,
        "servedBy": sale.getPaymentServedBy(groupedBy)
    }
    return render(request, 'pos/sales/print/customerReceipt.html', context)

@access_required('sale')
@login_required()
def printLedgerPaymentReceipt(request, customer_id, payment_grouping):
    customer = get_object_or_404(Customer, pk=customer_id)
    account = customer.account
    groupedBy = int(payment_grouping)
    payments = LedgerAccountPayment.objects.all().filter(groupedBy=groupedBy, account=account)
    snapshot = LedgerAccountPaymentSnapshot.objects.get(paymentGrouping=groupedBy)
    context = {
        "snapshot": snapshot,
        "customer": customer,
        "payments": payments,
    }
    return render(request, 'pos/customers/print/accountReceipt.html', context)

@access_required('sale')
@login_required()
def printLedgerAccountSummary(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    account = customer.account
    lines = account.getCurrentEntries().exclude(balance=0)
    context = {
        "snapshot": account,
        "customer": customer,
        "lines": lines,
    }
    return render(request, 'pos/customers/print/accountSummary.html', context)

@access_required('sale')
@login_required()
def adjustCreditLimit(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    account = customer.account
    if request.POST:
        if 'limit' in request.POST:
            account.creditLimit = Decimal(request.POST['limit'])
            account.save()
            return HttpResponseRedirect(reverse('pos:viewCustomer', args=[customer.id]))

@access_required('sale')
@login_required()
def printProformaInvoice(request, sale_id):
    sale = Sale.objects.get(pk=sale_id)
    saleLines = SalesLine.objects.filter(sale=sale)
    context = {
        "sale": sale,
        "saleLines": saleLines,
    }
    return render(request, 'pos/sales/print/proformaInvoice.html', context)

@access_required('sale')
@login_required()
def printDeliveryDocket(request, sale_id):
    sale = Sale.objects.get(pk=sale_id)
    saleLines = SalesLine.objects.filter(sale=sale)
    context = {
        "sale": sale,
        "saleLines": saleLines,
    }
    return render(request, 'pos/sales/print/deliveryDocket.html', context)

@access_required('sale')
@login_required()
def printTaxInvoice(request, invoice_id):
    invoice = SaleInvoice.objects.get(pk=invoice_id)
    invoiceLines = SaleInvoiceLine.objects.filter(invoice=invoice)
    context = {
        "sale": invoice.sale,
        "saleInvoice": invoice,
        "invoiceLines": invoiceLines
    }
    return render(request, 'pos/sales/print/taxInvoice.html', context)

@access_required('sale')
@login_required()
def deleteSale(request, sale_id):
    sale = get_object_or_404(Sale,pk=sale_id)
    if sale.status == "QUOTE":
        SalesLine.objects.filter(sale=sale).delete()
        sale.delete()
    return HttpResponseRedirect(reverse('pos:home'))

@access_required('sale')
@login_required()
def searchSales(request, sale_type):
    sales = Sale.objects.all().filter(terminal__store=request.store) #filter stores sales.

    if sale_type =="PENDING":
        sales = sales.filter(status="PENDING")
    else:
        sales = sales.filter(status=sale_type)

    context = filterGenericSearchQuery(sales, ['code', 'note', 'customer__firstName', 'customer__lastName', 'salesline__item__model'], request.GET)

    context.update({
        'salesFilter' : sale_type,
        'entityName' : "Sale"
    })

    return render(request, 'pos/sales/search.html', context)

@access_required('sale')
@login_required()
def customerPayment(request, customer_id):
    staffMember = get_object_or_404(Staff, pk=request.session['staff_id'])
    customer = get_object_or_404(Customer, pk=customer_id)
    account = customer.account
    now = timezone.now()
    groupedBy = account.getMostRecentGroupedBy() + 1
    if 'accountPayments' in request.POST:
        accountsPayments = json.loads(request.POST['accountPayments'])
        payments = accountsPayments['paymentLines']
        ledgerEntries = accountsPayments['ledgerEntries']
        for payment in payments:
            paymentMethod = PaymentMethod.objects.get(pk=payment['method_id'])
            ledgerPayment = LedgerAccountPayment(
                account=account,
                amount=payment['amount'],
                date=now,
                receivedBy=staffMember,
                paymentMethod=paymentMethod,
                groupedBy=groupedBy,
            )
            if paymentMethod.id == settings.CREDIT_ID:
                note = CreditNote.objects.get(pk=payment['note_id'])
                note.active = False
                note.save()
                ledgerPayment.notes = payment['note']
            ledgerPayment.save()
        snapshot = LedgerAccountPaymentSnapshot(
            account=account,
            accountTotal=account.getAccountTotal(),
            paidToDate=account.getPaidToDate(),
            balanceDue=account.getAccountBalance(),
            paymentGrouping=groupedBy
        )
        for ledgerEntry in ledgerEntries:
            dbLedgerEntry = LedgerAccountEntry(
                account=account,
                status=ledgerEntry['status'],
                referenceID=ledgerEntry['referenceID'] if ledgerEntry['referenceType'] != 'invoice' else groupedBy,
                referenceNum=ledgerEntry['referenceNum'],
                referenceType=ledgerEntry['referenceType'],
                total=ledgerEntry['total'],
                balance=ledgerEntry['balance'],
                comment=ledgerEntry['comment']
            )
            dbLedgerEntry.save()
            if ledgerEntry['referenceType'] == 'entry':
                relatedTo = LedgerAccountEntry.objects.get(pk=ledgerEntry['referenceID'])
                relatedTo.balance = relatedTo.balance + Decimal(ledgerEntry['total']) #correct the balance of the original entry
                if relatedTo.balance == Decimal('0.00') and ledgerEntry['status'] == 'FINALISED':
                    relatedTo.status = 'FINALISED'
                    for entry in relatedTo.getReferenceEntries(): #change all payments towards this balance to finalised.
                        entry.status = 'FINALISED'
                        entry.save()
                relatedTo.save()
        snapshot.balanceCarried = account.getAccountBalance()
        snapshot.save()
    return HttpResponse(json.dumps({'success': True}))

@access_required('sale')
@login_required()
def newEOD(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    try: #last terminal closure
        lastTerminalClosure = TerminalClosure.objects.filter(terminal=terminal).order_by('-endDate')[:1].get()
        firstDate = lastTerminalClosure.endDate
    except TerminalClosure.DoesNotExist: #first Payment
        try:
            lastPayment = SalesPayment.objects.filter(sale__terminal=terminal).order_by('date')[:1].get()
            firstDate = lastPayment.date
        except SalesPayment.DoesNotExist:
            return HttpResponseServerError()
    endDate = timezone.now()

    excludeMethods = [settings.ACCOUNTS_ID, settings.CREDIT_ID]
    salesPayments = SalesPayment.objects.filter(sale__terminal=terminal, date__range=(firstDate, endDate)).exclude(sale__status="QUOTE")
    readableCustomers = Customer.objects.all().filterReadAll(request.store)
    ledgerAccountPayments = LedgerAccountPayment.objects.filter(date__range=(firstDate, endDate), account__customer__in=readableCustomers)

    allTerminalPaymentsToday = list(chain(salesPayments, ledgerAccountPayments))

    salesPayments = salesPayments.filter(~Q(paymentMethod__in=excludeMethods) & ~Q(paymentMethod__parentMethod__in=excludeMethods))
    ledgerAccountPayments = ledgerAccountPayments.filter(~Q(paymentMethod__in=excludeMethods) & ~Q(paymentMethod__parentMethod__in=excludeMethods))
    NonAccountCreditTerminalPaymentsToday = list(chain(salesPayments, ledgerAccountPayments))

    terminalCounts = []
    paymentLogs = []
    completeTotal = Decimal('0.00')

    for paymentMethod in PaymentMethod.objects.all().filterReadAll(request.store).filter(~Q(id__in=excludeMethods) & ~Q(parentMethod__in=excludeMethods)).exclude(id=settings.CARD_ID):
        filteredPayments = filter(lambda x: x.paymentMethod.id == paymentMethod.id, NonAccountCreditTerminalPaymentsToday)
        if len(filteredPayments) > 1:
            total = reduce(lambda x, y: x.amount + y.amount if hasattr(x, 'amount') else x + y.amount, filteredPayments)
        elif len(filteredPayments) == 1:
            total = filteredPayments[0].amount
        else:
            total = None
        if total is None: total = Decimal('0.00')
        terminalCount = {
            "name": paymentMethod.name,
            "total": total,
            "id": paymentMethod.id,
        }
        completeTotal += total
        terminalCounts.append(terminalCount)

    for payment in allTerminalPaymentsToday:
        paymentLog = {
            "ReceivedBy" : payment.receivedBy.name,
            "PaymentAmount" : payment.amount,
            "PaymentMethod" : payment.paymentMethod.name,
            "DateTime" : payment.date,
        }
        if hasattr(payment, 'sale'):
            paymentLog["InvoiceNum"] = payment.sale.code
        paymentLogs.append(paymentLog)

    context = {
        "endDate" : endDate,
        "startDate" : firstDate,
        "totals" : terminalCounts,
        "completeTotal" : completeTotal,
        "paymentLogs" : paymentLogs,
        "terminal" : terminal,
    }

    return render(request, 'pos/eod/new.html', context)

@access_required('sale')
@login_required()
def saveEOD(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    staffMember = get_object_or_404(Staff, pk=request.session['staff_id'])
    if request.method == "POST":
        if ('EODData' in request.POST) and request.POST['EODData'].strip():
            EODData = json.loads(request.POST['EODData'],encoding="utf-8")
            neweod = TerminalClosure()
            neweod.comment = decodeReceivedText(EODData['comment'])
            neweod.count = EODData['count']
            neweod.difference = EODData['difference']
            neweod.endDate = datetime.now()
            neweod.startDate = EODData['startDate']
            neweod.terminal = terminal
            neweod.status = EODData['status']
            neweod.total = EODData['total']
            neweod.closedBy = staffMember
            neweod.save()
            for count in EODData['TerminalCounts']:
                paymentMethod = get_object_or_404(PaymentMethod,pk=count['id'])
                dbcount = TerminalCount(paymentMethod=paymentMethod)
                dbcount.count = count['count']
                dbcount.difference = count['difference']
                dbcount.eod = neweod
                dbcount.total = count['total']
                dbcount.save()
            term = TerminalActivity.objects.get_or_create(closure=neweod, terminal=terminal)[0]
            term.save()
    returnUrls = {
        "openEOD" : reverse('pos:openEOD', args=[neweod.id]),
    }
    jsonResponse = json.dumps(returnUrls)
    return HttpResponse(jsonResponse)

@access_required('sale')
@login_required()
def openEOD(request, EOD_id):
    eod = get_object_or_404(TerminalClosure, pk=EOD_id)
    terminal = eod.terminal
    terminalPaymentsRange= SalesPayment.objects.filter(sale__terminal=terminal, date__range=(eod.startDate, eod.endDate))
    terminalCounts = []
    paymentLogs = []

    for count in TerminalCount.objects.all().filter(eod=eod):
        terminalCount = {
            "name" : count.paymentMethod.name,
            "total" : count.total,
            "count" : count.count,
            "difference" : count.difference,
            "id" : count.paymentMethod.id,
            }
        terminalCounts.append(terminalCount)

    for payment in terminalPaymentsRange:
        paymentLog = {
            "InvoiceNum" : payment.sale.code,
            "ReceivedBy" : payment.receivedBy.name,
            "PaymentAmount" : payment.amount,
            "PaymentMethod" : payment.paymentMethod.name,
            "DateTime" : payment.date,
            }
        paymentLogs.append(paymentLog)

    context = {
        "endDate" : eod.endDate,
        "startDate" : eod.startDate,
        "comment" : eod.comment,
        "totals" : terminalCounts,
        "completeTotal" : eod.total,
        "paymentLogs" : paymentLogs,
        "terminal" : terminal,
        }

    return render(request, 'pos/eod/load.html', context)

@access_required('sale')
@login_required()
def searchEOD(request):
    storeTerminals = Terminal.objects.filter(store=request.store)
    closures = TerminalClosure.objects.filter(terminal__in=storeTerminals) #filter stores sales.
    startDate = datetime.today() - timedelta(days=120)
    endDate = datetime.today() + timedelta(days=1)
    p = 1

    if ('startDate' in request.POST) and (len(request.POST['startDate'].strip())>0):
        startDate = datetime.strptime(request.POST['startDate'],"%m/%d/%Y")
        endDate = datetime.strptime(request.POST['endDate'],"%m/%d/%Y")
        if startDate > endDate:
            endDate = startDate

    closures = closures.filter(endDate__lte=endDate, endDate__gte=startDate).order_by('-endDate')[:300]

    paginator = Paginator(closures, 30)
    if ('page' in request.POST)  and (len(request.POST['page'].strip())>0):
        p = int(request.POST['page'])
    try:
        closures = paginator.page(p)
    except EmptyPage:
        closures = paginator.page(paginator.num_pages)

    context = {
        'entities': closures,
        'startDate': startDate,
        'endDate': endDate,
        'entityName': "Closure",
        'page': p,
    }

    return render(request, 'pos/eod/search.html', context)

#Payment Methods CRUD
class PaymentMethodCreateView(LoginAndAdminPrivelege, StoreLevelObjectMixin, JSONCreateView):
    model = PaymentMethod
    form_class = PaymentMethodForm

    def form_valid(self, form):
        method = super(PaymentMethodCreateView, self).storeLevelFormSanitize(form)
        method.save()
        return HttpResponse(json.dumps({'success': True, }))

class PaymentMethodUpdateView(LoginAndAdminPrivelege, StoreLevelObjectMixin, JSONUpdateView):
    model = PaymentMethod
    form_class = PaymentMethodForm
    template_name = 'pos/paymentmethod/update.html'

class PaymentMethodDeleteView(LoginAndAdminPrivelege, JSONDeleteView):
    model = PaymentMethod

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        method = self.object
        if SalesPayment.objects.filter(paymentMethod=method).count() or LedgerAccountPayment.objects.filter(paymentMethod=method).count():
            return HttpResponse(json.dumps({'error': 'Payment method has been used in 1 or more Sales - Action Not Completed', }))
        else:
            method.delete()
            return HttpResponse(json.dumps({'success': True, }))
#end of payment methods CRUD

#Customer Crud

class CustomerCreateView(LoginAndSalePrivelege, StoreLevelObjectMixin, JSONCreateView):
    model = Customer
    form_class = CustomerForm

    def form_valid(self, form):
        customer = super(CustomerCreateView, self).storeLevelFormSanitize(form)
        customer.save()
        returnData = {
            "firstContactPoint" : customer.firstContactPoint(),
            "fullName" : customer.firstName + " " + customer.lastName,
            "creditLimit": 0,
            "formattedAddress" : customer.htmlFormattedAddress(),
            "id" : customer.id,
        }
        return HttpResponse(json.dumps(returnData))

class CustomerUpdateView(LoginAndSalePrivelege, StoreLevelObjectMixin, JSONUpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'pos/customers/update.html'
    context_object_name = 'customer'

class CustomerDeleteView(LoginAndSalePrivelege, JSONDeleteView):
    model = Customer

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        customer = self.object
        if Sale.objects.filter(customer=customer).count():
            return HttpResponse(json.dumps({'error': 'Customer is attached to one or more Sales - Action Not Completed', }))
        else:
            customer.delete()
            return HttpResponse(json.dumps({'success': True, }))

@access_required('sale')
@login_required()
def viewCustomer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    staffMember = get_object_or_404(Staff, pk=request.session['staff_id'])
    completedSales = Sale.objects.filter(customer=customer, status="COMPLETED")
    allSalesHistory = Sale.objects.filter(customer=customer)
    quotes = allSalesHistory.filter(status="QUOTE")
    openSales = allSalesHistory.filter(status="PENDING")
    creditNotes = CreditNote.objects.filter(customer=customer, active=True) #get only the notes that have not been used.
    paymentMethods = PaymentMethod.objects.all().filterReadAll(request.store)
    form = CustomerForm(instance=customer, store=request.store)
    ledgerAccount = customer.account
    accountPayments = LedgerAccountPayment.objects.filter(account=ledgerAccount).order_by('-date')
    context = {
        'customer': customer,
        'staff': staffMember,
        'ledgerAcc': ledgerAccount,
        'accountPayments': accountPayments,
        'completedSales': completedSales,
        'openSales': openSales,
        'quotes': quotes,
        'paymentMethods': paymentMethods,
        'creditNotes': creditNotes,
        'form': form,
    }
    return render(request, 'pos/customers/view.html', context)

class CustomerSearchView(LoginAndSalePrivelege, BRListView):
    model = Customer
    template_name = 'pos/customers/search.html'
    paginate_by = 30
    context_object_name = 'entities'

    def get_queryset(self):
        #dynamic filter based on request.POST or request.GET
        customers = Customer.objects.all().filterReadAll(self.request.store)
        #search by simple query
        q = self.request.GET.get('q') or self.request.POST.get('q') or ''
        self.context_append['q'] = q
        if len(q.strip()):
            customers = customers.filter(get_query(q, ['firstName', 'lastName', 'address', 'email', 'homePhone', 'workPhone', 'mobile', 'VCN']))
        return customers.order_by('lastName')[:300]

    def get_context_data(self, **kwargs):
        context = super(CustomerSearchView, self).get_context_data(**kwargs)
        context.update(getGenericCrudURLS("Customer", c=True, u=True, d=True, prepend="pos:"))
        context['form'] = CustomerForm(store=self.request.store)
        return context

class CustomerAjaxSearchView(CustomerSearchView):
    template_name = 'pos/customers/search-ajax-main.html'
    context_object_name = 'customer_list'

    def get_context_data(self, **kwargs):
        context = super(CustomerAjaxSearchView, self).get_context_data(**kwargs)
        format = self.request.GET.get('format') or self.request.POST.get('format') or ''
        context['format'] = format
        return context
#end of customer CRUD