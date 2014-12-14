from decimal import *
from django import template
from core.models import *
from pos.models import *
register = template.Library()
import datetime

@register.filter
def getBrand(value, salesLine):
    product = Product.objects.filter(id=salesLine.item_id)
    brand = Brand.objects.filter(id=product[0].brand_id)
    return brand[0].brand

@register.filter
def getModel(value, salesLine):
    product = Product.objects.filter(id=salesLine.item_id)
    return product[0].model

@register.filter
def getDesc(value, salesLine):
    product = Product.objects.filter(id=salesLine.item_id)
    return product[0].description

@register.filter
def getType(value, salesLine):
    product = Product.objects.filter(id=salesLine.item_id)
    category = ProductCategory.objects.filter(id=product[0].category_id)
    return category[0].name

@register.filter
def getSellEx(value, salesLine):
    GST = D(settings.GST)
    minusGST = salesLine.unitPrice / GST
    minusGST *= salesLine.quantity
    minusGST = str(round(minusGST, 2))
    return minusGST

@register.filter
def getNett(value, salesLine):
    product = Product.objects.filter(id=salesLine.item_id)
    return product[0].spanNet * salesLine.quantity

@register.filter
def getSellInc(value, salesLine):
    sellInc = salesLine.unitPrice * salesLine.quantity
    return sellInc

@register.filter
def getPriceMinusGST(price):
    GST = D(settings.GST)
    priceMinusGST = price / GST
    priceMinusGST = str(round(priceMinusGST, 2))
    priceMinusGST = Decimal(priceMinusGST)
    return priceMinusGST

@register.filter
def getGPDollar(value, salesLine):  # GP$ = SellPrice(ex) - SpanNett(ex)
    sellMinusGST = getPriceMinusGST(salesLine.unitPrice)
    product = Product.objects.filter(id=salesLine.item_id)
    spanNet = product[0].spanNet
    spanNet = Decimal(spanNet)
    sellMinusGST *= salesLine.quantity
    spanNet *= salesLine.quantity
    GPDollar = sellMinusGST - spanNet
    return GPDollar

@register.filter
def getGPPerc(value, salesLine):  # GP% = ((sell ex - nett ex) / sell ex) x 100
    GST = D(settings.GST)
    sellEx = salesLine.unitPrice / GST
    sellEx = Decimal(sellEx)
    product = Product.objects.filter(id=salesLine.item_id)
    nettEx = product[0].spanNet
    if sellEx == 0:
        GPPerc = 0
    else:
        GPPerc = ((sellEx-nettEx) / sellEx) * 100
    GPPerc = str(round(GPPerc, 2))
    return GPPerc


#  from sales class-----------------------------------------------
class Sales():
    pass


@register.filter
def getSalesExWarrantiesPerSalesperson(value, salesPerson, filteredSalesByDate):
    numberOfWarranties = getWarrantiesPerSalesperson(value, salesPerson, filteredSalesByDate)
    numberOfSales = getNumSalesPerSalesperson(value, salesPerson, filteredSalesByDate)
    numberOfSalesExWarranties = numberOfSales - numberOfWarranties
    return numberOfSalesExWarranties

@register.filter
def getStrikeRate(value, salesPerson, filteredSalesByDate):
    numberOfSalesExWarranties = getSalesExWarrantiesPerSalesperson(value, salesPerson, filteredSalesByDate)
    numberOfWarranties = getWarrantiesPerSalesperson(value, salesPerson, filteredSalesByDate)
    if len(filteredSalesByDate) == 0:
        strikeRate = "na"
    else:
        strikeRate = "{0:.0f}%".format(float(numberOfWarranties)/numberOfSalesExWarranties * 100)
    return strikeRate

@register.filter
def getNumSalesPerSalesperson(value, salesPerson, filteredSalesByDate):
    sales = filteredSalesByDate.filter(salesPerson=salesPerson)
    salesLines = SalesLine.objects.filter(sale__in=sales)
    return salesLines.count()

@register.filter
def getWarrantiesPerSalesperson(value, salesPerson, filteredSalesByDate):
    sales = filteredSalesByDate.filter(salesPerson=salesPerson)
    salesLines = SalesLine.objects.filter(sale__in=sales)
    warranties = Warranty.objects.all()
    warrantyList = []
    for warranty in warranties:
        warrantyList.append(warranty.product_ptr)
    salesLines = salesLines.filter(item__in=warrantyList)
    return salesLines.count()

@register.filter
def getRep(value, salesLine):
    sale = Sale.objects.filter(id=salesLine.sale_id)
    user_id = sale[0].salesPerson_id
    user = Staff.objects.filter(id=user_id)
    return user[0].name

@register.filter
def getRepForWarranty(value, salesLine):
    salesLine = SalesLine.objects.get(id=int(salesLine))
    sale = Sale.objects.filter(id=str(salesLine.sale))
    user_id = sale[0].salesPerson_id
    user = Staff.objects.filter(id=user_id)
    return user[0].name

@register.filter
def getInvoiceRef(value, salesLine):
    sale = Sale.objects.filter(id=salesLine.sale_id)
    sale_id = sale[0].id
    saleInvoice = SaleInvoice.objects.filter(sale_id=sale_id)
    invoiceRef = saleInvoice[0].reference
    return invoiceRef

@register.filter
def getSaleCode(value, salesLine):
    sale = Sale.objects.filter(id=salesLine.sale_id)
    code = sale[0].code
    return code

@register.filter
def getCust(value, salesLine):
    sale = Sale.objects.filter(id=salesLine.sale_id)
    customer_id = sale[0].customer_id
    customer = Customer.objects.filter(id=customer_id)
    firstName = customer[0].firstName
    lastName = customer[0].lastName
    return firstName + " " + lastName

@register.filter
def getDateSold(value, salesLine):
    sale = Sale.objects.filter(id=salesLine.sale_id)
    purchaseDate = sale[0].purchaseDate
    return purchaseDate

@register.filter
def getPaymentDate(value, salesLine):
    sale = Sale.objects.filter(id=salesLine.sale_id)
    fullPaymentDate = sale[0].fullPaymentDate
    return fullPaymentDate


#  Distribution_SalesbyCustomer-----------------------------------------------
class Distribution_SalesbyCustomer():
    pass


@register.filter
def filterSalesByDate(startDate, endDate):
    filteredSales = Sale.objects.filter(created__range=[startDate, endDate])
    return filteredSales

@register.filter
def getSalesTotalInc(reportType, arg, filteredSalesByDate):
    salesTotal = 0
    salesLines = getReportSalesLines(reportType, arg, filteredSalesByDate)
    for salesLine in salesLines:
        unitPrice = salesLine.unitPrice
        unitPrice *= salesLine.quantity
        unitPrice = round(unitPrice, 2)
        salesTotal += unitPrice
    return salesTotal

@register.filter
def getState(postcode):
    postcodes = Postcode.objects.filter(code=postcode)
    return postcodes[0].state

@register.filter
def getType(postcode):
    return "tba"

@register.filter
def getSalesTotalEx(reportType, arg, filteredSalesByDate):
    salesTotal = 0
    salesLines = getReportSalesLines(reportType, arg, filteredSalesByDate)
    for salesLine in salesLines:
        GST = D(settings.GST)
        minusGST = salesLine.unitPrice / GST
        minusGST *= salesLine.quantity
        minusGST = round(minusGST, 2)
        salesTotal += minusGST
    return salesTotal

@register.filter
def getCostPriceTotal(reportType, arg, filteredSalesByDate):
    costPriceTotal = 0
    salesTotal = getSalesTotalEx(reportType, arg, filteredSalesByDate)
    if salesTotal < 0:
        costPriceTotal = "NA"
    else:
        salesLines = getReportSalesLines(reportType, arg, filteredSalesByDate)
        for salesLine in salesLines:
            product = Product.objects.get(id=salesLine.item.id)
            costPrice = product.costPrice
            costPrice *= salesLine.quantity
            costPriceTotal += costPrice
    return costPriceTotal

@register.filter
def getGPDollarTotal(reportType, arg, filteredSalesByDate):
    GPDollarTotal = 0
    salesTotal = getSalesTotalEx(reportType, arg, filteredSalesByDate)
    if salesTotal < 0:
        GPDollarTotal = "NA"
    else:
        salesLines = getReportSalesLines(reportType, arg, filteredSalesByDate)
        for salesLine in salesLines:
            GPDollar = getGPDollar(True, salesLine)
            GPDollarTotal += GPDollar
    return GPDollarTotal

@register.filter
def getGPPercTotal(reportType, arg, filteredSalesByDate):
    GPPercentTotal = 0
    totalProducts = 0
    salesTotal = getSalesTotalEx(reportType, arg, filteredSalesByDate)
    if salesTotal < 0:
        GPPercentTotal = "NA"
    else:
        salesLines = getReportSalesLines(reportType, arg, filteredSalesByDate)
        for salesLine in salesLines:
            GPPerc = getGPPerc(True, salesLine)
            GPPerc = float(GPPerc)
            GPPerc *= salesLine.quantity
            GPPercentTotal += GPPerc
            totalProducts += salesLine.quantity
        if totalProducts == 0:
            GPPercentTotal = 0
        else:
            GPPercentTotal /= totalProducts
    return GPPercentTotal

def getReportSalesLines(reportType, arg, filteredSalesByDate):
    if reportType == 1:  # Distribution
        postcode = arg
        customersPerPostcode = Customer.objects.filter(ppostcode=postcode)
        salesPerPostcode = filteredSalesByDate.filter(customer__in=customersPerPostcode)
        salesLines = SalesLine.objects.filter(sale__in=salesPerPostcode)
    elif reportType == 2:  # Sales By Customer
        customer = arg
        salesPerCustomer = filteredSalesByDate.filter(customer=customer)
        salesLines = SalesLine.objects.filter(sale__in=salesPerCustomer)
    elif reportType == 3:  # Sales Person
        salesPerson = arg
        salesPerSalesPerson = filteredSalesByDate.filter(salesPerson=salesPerson)
        salesLines = SalesLine.objects.filter(sale__in=salesPerSalesPerson)
    else:
        salesLines = []
    return salesLines

@register.filter
def getQuantityOfSalesByCust(reportType, arg, filteredSalesByDate):
    qtyTotal = 0
    salesLines = getReportSalesLines(reportType, arg, filteredSalesByDate)
    for salesLine in salesLines:
        if not salesLine.quantity < 0:
            qtyTotal += salesLine.quantity
    return qtyTotal




