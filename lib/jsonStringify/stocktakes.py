__author__ = 'Yussuf'
from core.models import Product
from stock.models import StockTake, StockTakeLine

def stockTakeFromJson(data, staff):
    if data.get('id', 0) != 0:
        stocktake = StockTake.objects.get(pk=data.get('id'))
    else:
        stocktake = StockTake()
        stocktake.createdBy = staff
        stocktake.store = staff.store
    stocktake.status = data.get('status')
    stocktake.save()
    #print data
    lines = data.get('stockTakeLines')
    #get uniques
    seen = set()
    seen_add = seen.add
    uniqueModels = [{'productID' : x.get('productID'), 'quantity': 0, 'systemQuantity': x.get('systemQuantity')} for x in lines if x.get('productID') not in seen and not seen_add(x.get('productID'))]
    print uniqueModels
    #for each unique get the total
    for model in uniqueModels:
        model['quantity'] = reduce(lambda x, y: x + y.get('quantity') if y.get('productID') == model.get('productID') else x + 0, lines, 0)
    #iterate over unique models
    for model in uniqueModels:
        dbproduct = Product.objects.get(pk=model.get('productID'))
        try:
            dbline = StockTakeLine.objects.get(product=dbproduct, stocktake=stocktake)
        except StockTakeLine.DoesNotExist:
            dbline = StockTakeLine()
            dbline.product = dbproduct
        dbline.quantity = model.get('quantity')
        dbline.stocktake = stocktake
        dbline.systemQuantity = model.get('systemQuantity')
        dbline.save()
        if data.get('status', 'SAVED') == 'COMPLETED' and data.get('clearNSBI', False): # delta stock counts
            dbproduct.deltaStockCounts(staff.store, dbline.variance*-1, reference=stocktake, referenceType='StockTake', purchaseNet=0.00)
    #delete lines not in the final set for saved stocktakes that have had lines removed.
    StockTakeLine.objects.all().filter(stocktake=stocktake).exclude(product__pk__in=seen).delete()
    return stocktake

def jsonFromStockTake(stockTake):
    x = \
    {
        'id': stockTake.id,
        'status': stockTake.status,
        'stockTakeLines': [{'productID': x.product.id, 'quantity': x.quantity, 'systemQuantity': x.systemQuantity, 'description': x.product.model, 'nsbiQuantity': x.product.getNSBICount(stockTake.store)} for x in stockTake.stocktakeline_set.all()]
    }
    #print x
    return x