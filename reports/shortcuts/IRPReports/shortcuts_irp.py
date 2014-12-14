from core.models import *
from pos.models import *
from b2b.models import HeadOfficeInvoiceLine, HeadOfficeInvoice
from reports.shortcuts.shortcuts_global import *


def getIRPObjects(self, params):
    resultSet = getRows(self, self.request.store, params)
    resultSet = applySort(self, resultSet, params)
    return resultSet


def getRows(self, store, params):
    reportType = getReportType(self)
    # trueGP = setTrueGP(self, params)
    uniqueIdentifierObjectsForReport, param1 = getQuerySet(self, reportType, store, params)
    uniqueIdentifierObjectsForReport = applyFilterSwitch(self, reportType, params, uniqueIdentifierObjectsForReport)
    resultSet = convertQueryset(uniqueIdentifierObjectsForReport, reportType, param1)
    self.context_append['params'] = params
    return resultSet


def getQuerySet(self, reportType, store, params):
    param1 = ""
    startDate, endDate = getFilterDates(self, params)
    if reportType == "storePurchases":
        uniqueIdentifierObjectsForReport, param1 = getStorePurchasesData(self, store, params)
    elif reportType == "extended":
        uniqueIdentifierObjectsForReport = Postcode.objects.all()
    elif reportType == "invoiceByDate":
        uniqueIdentifierObjectsForReport = HeadOfficeInvoice.objects.filter(createdDate__range=[startDate, endDate])
    elif reportType == "storeListing":
        uniqueIdentifierObjectsForReport = Store.objects.all()
    elif reportType == "b2b":
        uniqueIdentifierObjectsForReport = Postcode.objects.all()
    elif reportType == "wholesale":
        uniqueIdentifierObjectsForReport = Postcode.objects.all()
    elif reportType == "rebates":
        uniqueIdentifierObjectsForReport, param1 = getRebatesData(self, params, store)
    elif reportType == "IAS":
        uniqueIdentifierObjectsForReport, param1 = getIASData(self, params)
    else:
        uniqueIdentifierObjectsForReport = False
    return uniqueIdentifierObjectsForReport, param1


def getIASData(self, params):
    uniqueIdentifierObjectsForReport = Store.objects.all()
    param1 = []
    purchaseOrderTotals = []
    invoiceTotals = []
    totalPurchaseTotals = []
    extendedCreditTotals = []
    rowCounter = -1
    startDate, endDate = getFilterDates(self, params)
    headOfficeInvoices = HeadOfficeInvoice.objects.filter(createdDate__range=[startDate, endDate])
    for store in uniqueIdentifierObjectsForReport:
        invoiceTotal = 0
        purchaseOrders = 0
        totalPurchases = 0
        extendedCredit = "tba"
        rowCounter += 1
        headOfficeInvoices = headOfficeInvoices.filter(store=store)
        headOfficeInvoiceLines = HeadOfficeInvoiceLine.objects.filter(invoice__in=headOfficeInvoices)
        for line in headOfficeInvoiceLines:
            invoiceTotal += line.invoicePrice
            purchaseOrders += 0
        totalPurchases = invoiceTotal + purchaseOrders
        purchaseOrderTotals.append(purchaseOrders)
        invoiceTotals.append(invoiceTotal)
        totalPurchaseTotals.append(totalPurchases)
        extendedCreditTotals.append(extendedCredit)
    param1.append(purchaseOrderTotals)
    param1.append(invoiceTotals)
    param1.append(totalPurchaseTotals)
    param1.append(extendedCreditTotals)
    return uniqueIdentifierObjectsForReport, param1


def getRebatesData(self, params, store):
        uniqueIdentifierObjectsForReport = Brand.objects.all()
        param1 = []
        dollarDealTotals, percDealTotals, invoiceTotals, CVBTotals, spanNetTotals \
            = getRebateFigures(self, params, uniqueIdentifierObjectsForReport, store)
        param1.append(dollarDealTotals)
        param1.append(percDealTotals)
        param1.append(invoiceTotals)
        param1.append(CVBTotals)
        param1.append(spanNetTotals)
        return uniqueIdentifierObjectsForReport, param1


def getRebateFigures(self, params, uniqueIdentifierObjectsForReport, store):
    percDealTotals = []
    dollarDealTotals = []
    invoiceTotals = []
    spanNetTotals = []
    CVBTotals = []
    HOInvoiceLines, products, deals, classVendorBonuses = getFilteredRebateSets(self, params)
    for brand in uniqueIdentifierObjectsForReport:
        getModelBonusFigures(products, brand, deals, HOInvoiceLines, dollarDealTotals, percDealTotals)
        getTotalSalesFigures(products, brand, HOInvoiceLines, invoiceTotals, spanNetTotals)
        getClassVenBonusFigures(brand, products, HOInvoiceLines, classVendorBonuses, CVBTotals)
    return dollarDealTotals, percDealTotals, invoiceTotals, CVBTotals, spanNetTotals


def getClassVenBonusFigures(brand, products, HOInvoiceLines, classVendorBonuses, CVBTotals):
    filteredProducts = products.filter(brand=brand)
    filteredHOInvoiceLines = HOInvoiceLines.filter(item__in=filteredProducts)
    CVBBrandTotal = 0
    for line in filteredHOInvoiceLines:
        CVBs = classVendorBonuses
        categoryId = line.item.category.id
        productCategory = ProductCategory.objects.get(id=categoryId)
        CVBs = CVBs.filter(type=productCategory, brand=brand)
        for CVB in CVBs:
            CVBBrandTotal += CVB.amount * line.quantity
    CVBTotals.append(CVBBrandTotal)


def getTotalSalesFigures(products, brand, HOInvoiceLines, invoiceTotals, spanNetTotals):
    filteredProducts = products.filter(brand=brand)
    filteredHOInvoiceLines = HOInvoiceLines.filter(item__in=filteredProducts)
    brandTotalPurchases = 0
    spanNetTotal = 0
    for line in filteredHOInvoiceLines:
        brandTotalPurchases += line.invoicePrice
        spanNetTotal += line.storeNet * line.quantity
    invoiceTotals.append(brandTotalPurchases)
    spanNetTotals.append(spanNetTotal)


def getModelBonusFigures(products, brand, deals, HOInvoiceLines, dollarDealTotals, percDealTotals):
    filteredProducts = products.filter(brand=brand)
    dealsPerBrand = deals.filter(product__in=filteredProducts)
    dollarTotal = 0
    percTotal = 0
    for deal in dealsPerBrand:
        if deal.percent == 0:
            filteredHOInvoiceLines = HOInvoiceLines.filter(item=deal.product)
            qtyCounter = 0
            for HOInvoiceLine in filteredHOInvoiceLines:
                qtyCounter += HOInvoiceLine.quantity
            dollarTotal += deal.amount * qtyCounter
        else:
            filteredHOInvoiceLines = HOInvoiceLines.filter(item=deal.product)
            for salesLine in filteredHOInvoiceLines:
                lineTotal = salesLine.unitPrice * salesLine.quantity
                linePerc = lineTotal * (deal.amount / 100)
                percTotal += linePerc
    dollarDealTotals.append(dollarTotal)
    percDealTotals.append(percTotal)


def getFilteredRebateSets(self, params):
    startDate, endDate = getFilterDates(self, params)
    HOInvoices = HeadOfficeInvoice.objects.filter(createdDate__range=[startDate, endDate])  # filter by period
    HOInvoiceLines = HeadOfficeInvoiceLine.objects.filter(invoice__in=HOInvoices)
    classVendorBonuses = ClassVendorBonus.objects.filter(createdOn__range=[startDate, endDate])  # filter by period
    prodIds = []
    for HOInvoiceLine in HOInvoiceLines:
        prodIds.append(str(HOInvoiceLine.item.id))
    products = Product.objects.filter(id__in=prodIds)
    deals = Deal.objects.filter(product__in=products)
    return HOInvoiceLines, products, deals, classVendorBonuses


def getStorePurchasesData(self, store, params):
    allLevels = []
    headOfficeInvoiceLines = getStoreHOInvLines(self, store, params)
    for i in headOfficeInvoiceLines:
        level4 = i.item.category
        level3 = i.item.category.parentCategory
        level2 = ProductCategory.objects.get(id=i.item.category.parentCategory.id).parentCategory
        allLevels.append(level2.name + "/" + level3.name + "/" + level4.name)
    return headOfficeInvoiceLines, allLevels


def applyFilterSwitch(self, reportType, params, uniqueIdentifierObjectsForReport):
    if reportType == "storePurchases":
        pass
    elif reportType == "extended":
        pass
    elif reportType == "invoiceByDate":
        uniqueIdentifierObjectsForReport = applyFilter(self, params, uniqueIdentifierObjectsForReport, reportType)
    elif reportType == "storeListing":
        pass
    elif reportType == "b2b":
        pass
    elif reportType == "wholesale":
        pass
    elif reportType == "rebates":
        pass
    elif reportType == "IAS":
        pass
    else:
        pass
    return uniqueIdentifierObjectsForReport


def applyFilter(self, params, resultSet, reportType):
    if reportType == "invoiceByDate":
        store = self.request.GET.getlist('store') or self.request.POST.getlist('store') or []
        store = filter(len, store)
        if len(store):
            storeList = [int(x) for x in store]
            resultSet = resultSet.filter(store__in=storeList)
        params['store'] = ','.join([x for x in store]) if len(store) else ''
    return resultSet


def convertQueryset(uniqueIdentifierObjectsForReport, reportType, param1=[]):
    resultSet = []
    rowNumber = -1
    appendCounter = -1
    #convert this queryset to list so we can use sort method in the next sort function
    for uniqueIdentifierObject in uniqueIdentifierObjectsForReport:
        rowNumber += 1
        row = {}
        if reportType == "storePurchases":
            row['id'] = uniqueIdentifierObject.id
            row['Distributor'] = uniqueIdentifierObject.invoice.distributor.brand
            row['StoreName'] = uniqueIdentifierObject.invoice.store.name
            row['State'] = uniqueIdentifierObject.invoice.store.state
            row['Date'] = str(uniqueIdentifierObject.invoice.createdDate.strftime("%d/%m/%y %H:%M"))
            row['Invoice'] = uniqueIdentifierObject.invoice.invoiceNumber
            row['InvType'] = uniqueIdentifierObject.invoice.type
            row['Ref'] = uniqueIdentifierObject.invoice.orderReference
            row['Class'] = param1[rowNumber]
            row['item'] = uniqueIdentifierObject.item.model
            row['quantity'] = uniqueIdentifierObject.quantity
            row['invoicePrice'] = uniqueIdentifierObject.invoicePrice
            row['TotalInvinc'] = uniqueIdentifierObject.invoicePrice
            row['TotalNetinc'] = uniqueIdentifierObject.storeNet * uniqueIdentifierObject.quantity
        elif reportType == "extended":
            row['id'] = uniqueIdentifierObject.id
        elif reportType == "invoiceByDate":
            row['invoiceNumber'] = uniqueIdentifierObject.invoiceNumber
            row['type'] = uniqueIdentifierObject.type
            row['distributor'] = uniqueIdentifierObject.distributor.distributor
            row['invoiceDate'] = uniqueIdentifierObject.invoiceDate.strftime("%d/%m/%y %H:%M")
            row['invTotalExGST'] = uniqueIdentifierObject.invTotalExGST
            row['orderReference'] = uniqueIdentifierObject.orderReference
            row['store'] = uniqueIdentifierObject.store.name
            row['createdBy'] = uniqueIdentifierObject.createdBy.name
            row['createdDate'] = uniqueIdentifierObject.createdDate.strftime("%d/%m/%y %H:%M")
        elif reportType == "storeListing":
            row['name'] = uniqueIdentifierObject.name
            row['address'] = uniqueIdentifierObject.address + ". " + \
                             uniqueIdentifierObject.suburb + ". " + \
                             uniqueIdentifierObject.city + ". " + \
                             uniqueIdentifierObject.postcode + "."
            row['landphone'] = uniqueIdentifierObject.phone
            row['mobphone'] = uniqueIdentifierObject.phone
            row['email'] = uniqueIdentifierObject.email
            row['fax'] = uniqueIdentifierObject.fax
        elif reportType == "b2b":
            row['id'] = uniqueIdentifierObject.id
        elif reportType == "wholesale":
            row['id'] = uniqueIdentifierObject.id
        elif reportType == "rebates":
            totInv = param1[2][rowNumber]
            HORebateDollarFigure = ((param1[2][rowNumber] / 100) * uniqueIdentifierObject.actualRebate)
            storeNet = param1[4][rowNumber]
            HONet = totInv - HORebateDollarFigure
            row['distributor'] = uniqueIdentifierObject.brand
            row['totInv'] = totInv
            row['storeNet'] = storeNet
            row['HORebate'] = HORebateDollarFigure
            row['HODollarBonus'] = param1[0][rowNumber]
            row['HOPercBonus'] = param1[1][rowNumber]
            row['HOVCBonus'] = param1[3][rowNumber]
            row['HONet'] = HONet
            row['diff'] = HONet - storeNet
        elif reportType == "IAS":
            row['name'] = uniqueIdentifierObject.name
            row['purchaseOrders'] = param1[0][rowNumber]
            row['iRPInvoices'] = param1[1][rowNumber]
            row['totalPurchase'] = param1[2][rowNumber]
            row['extendedCredit'] = "tba"
            row['creditDebt'] = "tba"
            row['limit'] = "tba"
            row['openBuy'] = "tba"
            row['permit'] = "tba"
        else:
            appendCounter = 0
        if not appendCounter == 0:
            resultSet.append(row)
    return resultSet


def applySort(self, objects, params):
    reportType = getReportType(self)
    sortTypes = self.request.GET.getlist('sortTypes') or self.request.POST.getlist('sortTypes') or []
    if not sortTypes:
        pass
    try:
        if reportType == "storePurchases":
            pass
        elif reportType == "extended":
            pass
        elif reportType == "invoiceByDate":
            if sortTypes[0] == "0":
                objects.sort(key=operator.itemgetter('invTotalExGST'), reverse=True)
            elif sortTypes[0] == "1":
                objects.sort(key=operator.itemgetter('invoiceNumber'), reverse=True)
            elif sortTypes[0] == "2":
                objects.sort(key=operator.itemgetter('createdDate'), reverse=True)
        elif reportType == "storeListing":
            pass
        elif reportType == "b2b":
            pass
        elif reportType == "wholesale":
            pass
        elif reportType == "rebates":
            pass
        elif reportType == "IAS":
            pass
        else:
            pass
    except IndexError:
        pass
    params['sortTypes'] = ','.join([x for x in sortTypes]) if len(sortTypes) else ''
    return objects