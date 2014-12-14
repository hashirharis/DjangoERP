import calendar
from datetime import datetime, timedelta
from b2b.models import HeadOfficeInvoice, HeadOfficeInvoiceLine
from models import ProductRange, StoreRange , StoreDetail
from dateutil import tz
from core.models import Product

def checkRangedItem(invoice): 
    #checks if invoiced item has a range, adds it to the storeDetail table
    if invoice.type == "Purchase of stock":
        date = utc_to_local(invoice.invoiceDate.split('T')[0])
        month = date.month
        year = date.year
        invoice_month = str('{:02d}'.format(month))+'/'+str(year)
        try:
            store_range = StoreRange.objects.get(store=invoice.store, month=invoice_month)
            store_range_type = store_range.rangeType
            products_in_invoice = [Product.objects.get(id=i.get('item'))\
                                   for i in HeadOfficeInvoiceLine.objects.values('item').prefetch_related('item').filter(invoice=invoice)]
            ranged_products_in_invoice = ProductRange.objects.filter(product__in=products_in_invoice,
                                                                     month=invoice_month, productRange=store_range_type)
            for ranged_item in ranged_products_in_invoice:
                print 'iterating started ....'
                exists = StoreDetail.objects.filter(product=ranged_item.product,
                                                    month=invoice_month, storeRange=store_range).exists()
                print 'exists value ', exists
                if not exists:
                    storedetail = StoreDetail(product=ranged_item.product, storeRange=store_range, passed=True,
                                              month=invoice_month, guaranteed=ranged_item.guaranteed,
                                              bonus=ranged_item.bonus)
                    print storedetail
                    storedetail.save()
        except StoreRange.DoesNotExist:
            pass


def utc_to_local(utc_dt):
        print utc_dt,' inside utc'
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        utc = datetime.strptime(utc_dt+" 23", '%Y-%m-%d %H')
        utc = utc.replace(tzinfo=from_zone)
        central = utc.astimezone(to_zone)
        return central


def aslocaltimestr(utc_dt):
    return utc_to_local(utc_dt).strftime('%Y-%m-%d')

def is_current_month(rangedmonth):
    date = datetime.now()
    month = "%02d" % int(date.month)
    year = int(date.year)
    if str(month)+'/'+str(year)==rangedmonth:
        return True
    else:
        return False