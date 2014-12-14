from core.models import Product
from django import template
from django.conf import settings
from decimal import Decimal as D
from datetime import timedelta

register = template.Library()

@register.filter
def incGST(value):
    incGSTVal = D(value) * D(settings.GST)
    return '%.2f' % incGSTVal

@register.filter
def exGST(value):
    exGSTVal = D(value) / D(settings.GST)
    return '%.2f' % exGSTVal

@register.filter
def fullPercentFromDecimal(value):
    percentVal = D(value) * 100
    return '%.1f' % percentVal

@register.filter
def unsigned(value):
    if D(value) >= 0.00:
        return D(value)
    else:
        return D(value) * -1

@register.filter
def canEdit(value, arg):
#to check whether store specific model is editable by 'value' store
    return arg.can_write(value)

@register.filter
def getChildrenForPayment(value, arg):
#used to get the store specific payment children
    return arg.getChildren(value)

@register.filter
def getChildren(value, arg):
#used to get the store specific categories children
    return arg.getChildren(value)

@register.filter
def daysFrom(value, arg):
#calculate the number of days after a certain date. used for quotes
    return arg + timedelta(days=value)

@register.filter
def getAvailable(value, arg):
    return arg.getStockCounts(value).available

from stock.models import StoreInventory

@register.filter
def getStockOnHand(value, arg):
    try:
        inventoryItem = StoreInventory.objects.filter(store=value.id, product=arg)
        onHand = "-"
        onHand = inventoryItem[0].level
    except (StoreInventory.DoesNotExist, IndexError):
        pass
    return onHand


@register.filter
def getStockOrdered(value, arg):
    try:
        inventoryItem = StoreInventory.objects.filter(store=value.id, product=arg)
        ordered = "-"
        ordered = inventoryItem[0].stockOrder
    except (StoreInventory.DoesNotExist, IndexError):
        pass
    return ordered


@register.filter
def getNumItemHeld(value, arg):
    try:
        inventoryItem = StoreInventory.objects.filter(store=value.id, product=arg)
        held = "-"
        held = inventoryItem[0].customerOrder
    except (StoreInventory.DoesNotExist, IndexError):
        pass
    return held

@register.filter
def getRequired(value, arg):
    try:
        inventoryItem = StoreInventory.objects.filter(store=value.id, product=arg)
        required = "-"
        if inventoryItem[0].req:
            required = "N"
        else:
            required = "Y"
    except (StoreInventory.DoesNotExist, IndexError):
        pass
    return required

@register.filter
def getHistory(value, arg):
    from stock.models import SalesHistory
    import datetime
    from dateutil.relativedelta import relativedelta
    from collections import deque
    NOW = datetime.datetime.now()
    # NOW = datetime.datetime.now() + timedelta(days=30)
    currentYear = NOW.strftime('%Y')
    lastYear = NOW + relativedelta(years=-1)
    lastYear = lastYear.strftime('%Y')
    months = []
    currentMonth = True
    allowViewThisYearOnly = False
    firstYearWasntJan = True
    if NOW.strftime('%B') == "January":
        firstYearWasntJan = False

    try:
        for i in range(12):
            month = NOW + relativedelta(months=+i)
            monthName = month.strftime('%B')
            if monthName == "January":
                allowViewThisYearOnly = True
            if currentMonth:
                history = SalesHistory.objects.filter(store=value.id, product=arg, month=monthName, year=currentYear)
                currentMonth = False
                if history:
                    months.append(history[0].purchased)
                    months.append(history[0].sold)
                else:
                    months.append('-')
                    months.append('-')
            else:
                history = SalesHistory.objects.filter(store=value.id, product=arg, month=monthName, year=currentYear)
                if allowViewThisYearOnly and firstYearWasntJan:
                    if history:
                        months.append(history[0].purchased)
                        months.append(history[0].sold)
                    else:
                        months.append('-')
                        months.append('-')
                else:
                    history = SalesHistory.objects.filter(store=value.id, product=arg, month=monthName, year=lastYear)
                    if history:
                        months.append(history[0].purchased)
                        months.append(history[0].sold)
                    else:
                        months.append('-')
                        months.append('-')
    except IndexError:
        pass
    months = deque(months)
    months.rotate(-2)
    return months

@register.filter
def getMonths(value, arg):
    import datetime
    from collections import deque
    months = ["Jan P", "Jan S", "Feb P", "Feb S", "Mar P", "Mar S", "Apr P", "Apr S", "May P", "May S",
              "Jun P", "Jun S", "Jul P", "Jul S", "Aug P", "Aug S", "Sep P", "Sep S", "Oct P", "Oct S",
              "Nov P", "Nov S", "Dec P", "Dec S"]
    months = deque(months)
    today = datetime.datetime.now()
    # today = datetime.datetime.now() + timedelta(days=30)
    currentMonth = today.strftime('%B')
    if currentMonth == "January":
        months.rotate(-2)
    if currentMonth == "February":
        months.rotate(-4)
    if currentMonth == "March":
        months.rotate(-6)
    if currentMonth == "April":
        months.rotate(-8)
    if currentMonth == "May":
        months.rotate(-10)
    if currentMonth == "June":
        months.rotate(-12)
    if currentMonth == "July":
        months.rotate(-14)
    if currentMonth == "August":
        months.rotate(-16)
    if currentMonth == "September":
        months.rotate(-18)
    if currentMonth == "October":
        months.rotate(-20)
    if currentMonth == "November":
        months.rotate(-22)
    if currentMonth == "December":
        months.rotate(-24)
    return months

#bulletin board
@register.filter
def hasRead(value, arg):
    return arg.hasRead(value)

@register.assignment_tag()
def getOrderFor(store, month):
    return month.getOrder(store)

#uploads module
from uploads.models import CSVUpload
import csv
from uploads import dynamicCSV
from core.models import Brand

@register.filter()
def getSaved(saved, arg):
    if saved:
        return "Yes"
    else:
        return "Not yet"


@register.filter()
def getCount(uploadId, arg):
    try:
        csvUpload = CSVUpload.objects.get(id=uploadId)
        open(csvUpload.csvFile.path, "rb")
        f = open(csvUpload.csvFile.path, "rb")
        csvRows = csv.DictReader(f)
        totalRows = 0
        for row in csvRows:
            totalRows += 1
        totalRows -= 1
        return totalRows
    except CSVUpload.DoesNotExist:
        return False


@register.filter()
def getCatalogueImage(val, uploadId):
    firstRowFromUpload = dynamicCSV.getFirstRowFromUpload(uploadId)
    end_date = ""
    loopCounter = 0
    for row in firstRowFromUpload:
        if loopCounter == 0:
            frontpage_image_URL = row.frontpage_image_URL
        loopCounter += 1
    return frontpage_image_URL


@register.filter()
def getCreationDate(val, uploadId):
    try:
        csvUpload = CSVUpload.objects.get(id=uploadId)
        return csvUpload.creationDate
    except CSVUpload.DoesNotExist:
        return False


@register.filter()
def getId(val, uploadId):
    try:
        csvUpload = CSVUpload.objects.get(id=uploadId)
        return csvUpload.id
    except CSVUpload.DoesNotExist:
        return False


@register.filter()
def getName(val, uploadId):
    try:
        csvUpload = CSVUpload.objects.get(id=uploadId)
        return csvUpload.name
    except CSVUpload.DoesNotExist:
        return False


@register.filter()
def getBrandName(val, brandId):
    try:
        brand = Brand.objects.get(id=brandId)
        return brand
    except Brand.DoesNotExist:
        return False


@register.filter
def getBrand(value, arg):
    product = Product.objects.filter(id=arg.item_id)
    return product[0]





