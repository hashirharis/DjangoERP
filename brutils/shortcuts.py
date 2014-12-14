def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def paginate_queryset(Queryset, page):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(Queryset, 50)
    try:
        page = paginator.page(page)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page


#  Merchandiser
import datetime
from core.models import Product
from stock.models import SalesHistory

def getSalesHistoryPurchase(dbLine, store):
    '''
        Used for Merchandiser to update the SalesHistory table with the new purchase details
    '''
    product = Product.objects.get(pk=dbLine.item.id)

    salesHistory, created = SalesHistory.objects.get_or_create(product=product,
                                         store=store,
                                         year=datetime.datetime.now().strftime("%Y"),
                                         month=datetime.datetime.now().strftime("%B"))
    if created:
        return None
    else:
        return salesHistory.purchased


def updateSalesHistoryPurchase(dbLine, store, session):
    '''
        Used for Merchandiser to update the SalesHistory table with the new purchase details
    '''
    currentPurchaseVal = getSalesHistoryPurchase(dbLine, store)
    product = Product.objects.get(pk=dbLine.item.id)
    salesHistory, created = SalesHistory.objects.get_or_create(product=product,
                                         store=store,
                                         year=datetime.datetime.now().strftime("%Y"),
                                         month=datetime.datetime.now().strftime("%B"))
    if created:
        createdObj = SalesHistory.objects.get(product=product,
                                         store=store,
                                         year=datetime.datetime.now().strftime("%Y"),
                                         month=datetime.datetime.now().strftime("%B"))
        createdObj.purchased = dbLine.quantity
        createdObj.save()
    else:
        if session['editingInvoice']:
            salesHistory.purchased += dbLine.quantity
            if currentPurchaseVal:
                salesHistory.purchased -= int(currentPurchaseVal)
        else:
            salesHistory.purchased += dbLine.quantity
        salesHistory.save()


def updateSalesHistorySales(salesLine, store, product):
    '''
        Used for Merchandiser to update the SalesHistory table with the new sale detail
    '''
    salesHistory, created = SalesHistory.objects.get_or_create(product=product,
                                         store=store,
                                         year=datetime.datetime.now().strftime("%Y"),
                                         month=datetime.datetime.now().strftime("%B"))
    if created:
        createdObj = SalesHistory.objects.get(product=product,
                                         store=store,
                                         year=datetime.datetime.now().strftime("%Y"),
                                         month=datetime.datetime.now().strftime("%B"))
        createdObj.sold = salesLine['quantity']
        createdObj.purchased = 0
        createdObj.save()
    else:
        salesHistory.sold += salesLine['quantity']
        salesHistory.save()


def updateSalesHistorySalesFromVW(line, store, product, session):

    '''
        Used for Merchandiser to update the SalesHistory table with the new sale detail
    '''
    salesHistory, created = SalesHistory.objects.get_or_create(product=product,
                                         store=store,
                                         year=datetime.datetime.now().strftime("%Y"),
                                         month=datetime.datetime.now().strftime("%B"))
    if created:
        createdObj = SalesHistory.objects.get(product=product,
                                         store=store,
                                         year=datetime.datetime.now().strftime("%Y"),
                                         month=datetime.datetime.now().strftime("%B"))
        createdObj.sold = line.quantity
        createdObj.purchased = 0
        createdObj.save()
    else:
        salesHistory.sold += line.quantity
        salesHistory.save()


def initialiseMerchandiserSession(request):
    request.session['editingInvoice'] = False


def initialiseMerchandiserEditSession(request):
    request.session['editingInvoice'] = True
