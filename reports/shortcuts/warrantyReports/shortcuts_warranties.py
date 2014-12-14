from core.models import *
from reports.shortcuts.shortcuts_global import *


def getWarrantyObjects(self, params):
    reportType = getReportType(self)
    resultSet = []
    counter = -1
    startDate = getStartDate(params, self.request.session['startDateList'])
    endDate = getEndDate(params, self.request.session['endDateList'])
    # startDate = getStartDate(self, params)
    # endDate = getEndDate(self, params)
    # trueGP = setTrueGP(self, params)
    if reportType == "warranty":
        warranties = getWarranties()
        sales = getStoreSales(self.request.store)
        uniqueIdentifierObjectsForReport = SalesLine.objects.filter(modelNum__in=warranties)
        uniqueIdentifierObjectsForReport = uniqueIdentifierObjectsForReport.filter(sale__in=sales)
    else:
        uniqueIdentifierObjectsForReport = False
    for uniqueIdentifierObject in uniqueIdentifierObjectsForReport:
        row = {}
        if reportType == "warranty":
            row['modelNum'] = uniqueIdentifierObject.modelNum
            row['id'] = uniqueIdentifierObject.id
            row['cust'] = uniqueIdentifierObject.sale.customer.firstName + " " + uniqueIdentifierObject.sale.customer.lastName
            row['store'] = uniqueIdentifierObject.sale.terminal.store.name
            row['salesPerson'] = uniqueIdentifierObject.sale.salesPerson.name
            row['description'] = uniqueIdentifierObject.item.description
            row['purchaseDate'] = str(uniqueIdentifierObject.sale.purchaseDate)
            row['brand'] = uniqueIdentifierObject.item.brand.brand
            row['purchasePrice'] = ""
            row['unitPrice'] = uniqueIdentifierObject.unitPrice
            row['comment'] = ""
        else:
            counter = 0
        if not counter == 0:
            resultSet.append(row)
    self.context_append['params'] = params
    return resultSet


def getWarranties():
    allWarranties = Warranty.objects.all()
    products = Product.objects.filter(id__in=allWarranties)
    warranties = []
    for product in products:
        warranties.append(product.model)
    return warranties