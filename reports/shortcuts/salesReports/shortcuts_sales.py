from core.models import *
from reports.shortcuts.shortcuts_global import *
from core.models import Postcode


class ItemisedSummaryFunctions(object):
    pass


def getObjects(self, params):
    resultSet = getRows(self, self.request.store, params)
    resultSet = applySort(self, resultSet, params)
    return resultSet


def getRows(self, store, params):
    reportType = getReportType(self)
    # startDate = getStartDate(self, params)
    # endDate = getEndDate(self, params)
    # trueGP = setTrueGP(self, params)
    uniqueIdentifierObjectsForReport, param1 = getQuerySet(self, params, reportType, store)
    uniqueIdentifierObjectsForReport = applyFilterSwitch(self, reportType, params, uniqueIdentifierObjectsForReport)
    resultSet = convertQueryset(self, params, uniqueIdentifierObjectsForReport, reportType, param1)
    self.context_append['params'] = params
    return resultSet


def getQuerySet(self, params, reportType, store):
    param1 = ""
    if reportType == "distribution":
        uniqueIdentifierObjectsForReport = getDistroData()
    elif reportType == "salesByCustomer":
        uniqueIdentifierObjectsForReport = Customer.objects.filter(store=store)
    elif reportType == "salesperson":
        uniqueIdentifierObjectsForReport = Staff.objects.filter(store=store)
    elif reportType == "warranties":
        uniqueIdentifierObjectsForReport, param1 = getWarrantySales(self, params, store)
    else:
        uniqueIdentifierObjectsForReport = False
    return uniqueIdentifierObjectsForReport, param1


def getSaleObjects(self, params):
    reportType = getReportType(self)
    if reportType == 'salesperson':
        objects = getObjects(self, params)
    elif reportType == "brandanalysis" or reportType == "brandanalysisdetailed" or reportType == "drill":
        objects = getSalesAnalysisResults(self)
    elif reportType == 'categoryanalysis' or reportType == 'categoryanalysisdetailed':
        objects = getSalesAnalysisResults(self)
    elif reportType == "itemised":
        params = {}
        objects = getSalesLinesPerStoreOrHO(self, params)
        self.context_append['params'] = params
    elif reportType == "itemisedsummary":
        params = {}
        objects = getItemisedSummary(self, params)
        self.context_append['params'] = params
    elif reportType == "monthly":
        params = {}
        objects = getMonthlySalesObjects(self.request.store, params)
        self.context_append['params'] = params
    elif reportType == "distribution":
        objects = getObjects(self, params)
    elif reportType == "salesByCustomer":
        objects = getObjects(self, params)
    elif reportType == "warranties":
        objects = getObjects(self, params)
    elif reportType == "itemisedsummary":
        objects = getObjects(self, params)
    return objects


def getItemisedSummary(self, params):
    # startDate = getStartDate(self, params)
    # endDate = getEndDate(self, params)
    startDate = getStartDate(params, self.request.session['startDateList'])
    endDate = getEndDate(params, self.request.session['endDateList'])
    resultSet = []
    tableRow = {}
    staffPeople = Staff.objects.filter(store_id=self.request.store.id)
    for staff in staffPeople:
        totalPriceOverall = 0
        totalOverallQuantity = 0
        totalReturnedPriceOverall = 0
        totalOverallReturnedQuantity = 0
        tableRow['staffName'] = staff.name
        resultSet.append(tableRow)
        level2Categories = ProductCategory.objects.filter(depth=2)
        for level2Category in level2Categories:
            tableRow = {}
            level3Categories = ProductCategory.objects.filter(parentCategory_id=level2Category.id)
            level4Categories = ProductCategory.objects.filter(parentCategory_id__in=level3Categories)
            allItemsPerLevelOneCategory = level2Categories | level3Categories
            allItemsPerLevelOneCategory = allItemsPerLevelOneCategory | level4Categories
            allProductsPerCategory = Product.objects.filter(category_id__in=allItemsPerLevelOneCategory)
            #  SALES
            salesLinesPerCategory = SalesLine.objects.filter(item_id__in=allProductsPerCategory)
            salesByStaff = Sale.objects.filter(salesPerson_id=staff.id)
            salesByStaff = salesByStaff.filter(purchaseDate__range=[startDate, endDate])
            salesLinesPerCategory = salesLinesPerCategory.filter(sale_id__in=salesByStaff)
            totalPrice = 0
            totalQuantity = 0
            totalReturnedPrice = 0
            totalReturnedQuantity = 0
            isUsed = False
            for saleLine in salesLinesPerCategory:
                if saleLine.price >= 0:
                    isUsed = True
                    totalQuantity += saleLine.quantity
                    totalPrice += saleLine.price
                elif saleLine.price < 0:
                    isUsed = True
                    totalReturnedQuantity += saleLine.quantity
                    totalReturnedPrice += saleLine.price
                else:
                    pass
            if not isUsed:
                pass
            else:
                tableRow['level2Category'] = level2Category.name
                tableRow['totalPrice'] = totalPrice
                tableRow['totalQuantity'] = totalQuantity
                tableRow['totalReturnedPrice'] = int(abs(totalReturnedPrice))
                tableRow['totalReturnedQuantity'] = int(abs(totalReturnedQuantity))
                tableRow['isDataRow'] = "isDataRow"
                totalPriceOverall += totalPrice
                totalOverallQuantity += totalQuantity
                totalReturnedPriceOverall += int(abs(totalReturnedPrice))
                totalOverallReturnedQuantity += int(abs(totalReturnedQuantity))
                resultSet.append(tableRow)
        totalsRow = {'level2Category': "Total", 'totalPrice': totalPriceOverall,
                        'totalQuantity': totalOverallQuantity, 'totalReturnedPrice': totalReturnedPriceOverall,
                        'totalReturnedQuantity': totalOverallReturnedQuantity,
                        'isDataRow': "isDataRow"}
        resultSet.append(totalsRow)
        resultSet.append("")
    return resultSet


class SalesAnalysisFunctions(object):
    pass


def getSalesAnalysisResults(self):
    params = {}
    saleLineObjects = getResultsRows(self, params)
    saleLineObjects = applySort(self, saleLineObjects, params)
    self.context_append['params'] = params
    return saleLineObjects


def getResultsRows(self, params):
    startDate = getStartDate(params, self.request.session['startDateList'])
    endDate = getEndDate(params, self.request.session['endDateList'])
    # startDate = getStartDate(self, params)
    # endDate = getEndDate(self, params)
    saleObjectsInDateRange = Sale.objects.filter(purchaseDate__range=[startDate, endDate])
    report_type = self.kwargs.get('report_type') or self.request.GET.get('report_type')\
                     or self.request.POST.get('report_type') or ''
    resultSet = []
    second_style = self.kwargs.get('second_style') or self.request.GET.get('second_style')\
                     or self.request.POST.get('second_style') or ''
    if second_style == '1' or second_style == '2':
        staffPeople = Staff.objects.all()
    else:
        staffPeople = Staff.objects.filter(store_id=self.request.store.id)
    if report_type == 'brandanalysisdetailed' or report_type == 'categoryanalysisdetailed':
        for staff in staffPeople:
            allSalesPerStore = getSalesPerStoreOrHO(self)
            allSalesPerStore = allSalesPerStore.filter(salesPerson=staff.id)
            getResultSet(self, params, report_type, allSalesPerStore, staff, resultSet, saleObjectsInDateRange)
            saleObjectsPerSalesman = saleObjectsInDateRange.filter(salesPerson=staff.id)
            if len(saleObjectsPerSalesman) == 0:
                pass
            else:
                sortTypes = self.request.GET.getlist('sortTypes') or self.request.POST.getlist('sortTypes') or []
                if not sortTypes:
                    row = {}
                    row['name'] = ""
                    if report_type == 'brandanalysisdetailed':
                        row['brand'] = ""
                    else:
                        row['category'] = ""
                    row['quantity'] = ""
                    row['totalSalesSell'] = ""
                    row['totalSalesNett'] = ""
                    row['GP'] = ""
                    row['GPPerc'] = ""
                    resultSet.append(row)
                else:
                    pass
    else:
        staff = 0
        allSalesPerStore = getSalesPerStoreOrHO(self)
        getResultSet(self, params, report_type, allSalesPerStore, staff, resultSet, saleObjectsInDateRange)
    return resultSet


def getResultSet(self, params, report_type, allSalesPerStore, staff, resultSet, saleObjectsInDateRange):
    trueGP = setTrueGP(self, params)
    brands = Brand.objects.all()
    brands = filterBrands(self, params, brands)
    productCategories = ProductCategory.objects.filter(depth=1)
    productCategories = filterCategories(self, params, productCategories)
    second_style = self.kwargs.get('second_style') or self.request.GET.get('second_style')\
                     or self.request.POST.get('second_style') or ''
    if report_type == 'brandanalysis' or report_type == 'brandanalysisdetailed':
        for brand in brands:  # get the queryset, run calculations, create dict of results
            allProductsPerBrand = Product.objects.filter(brand_id=brand.id)
            salesLinesPerBrand = SalesLine.objects.filter(item_id__in=allProductsPerBrand)
            salesLinesPerBrand = salesLinesPerBrand.filter(sale_id__in=saleObjectsInDateRange)
            salesLinesPerBrand = salesLinesPerBrand.filter(sale_id__in=allSalesPerStore)
            brandRow = calculationsOnQueryset(self, salesLinesPerBrand, brand, trueGP, report_type, staff)
            if report_type == 'brandanalysisdetailed':
                if brandRow["quantity"] == 0:
                    pass
                else:
                    resultSet.append(brandRow)
            else:
                resultSet.append(brandRow)
    else:
        for productCategory in productCategories:  # get the queryset, run calculations, create dict of results
            secondLevelCategories = ProductCategory.objects.filter(parentCategory_id=productCategory.id)
            thirdLevelCategories = ProductCategory.objects.filter(parentCategory_id__in=secondLevelCategories)
            forthLevelCategories = ProductCategory.objects.filter(parentCategory_id__in=thirdLevelCategories)
            allItemsPerLevelOneCategory = secondLevelCategories | thirdLevelCategories
            allItemsPerLevelOneCategory = allItemsPerLevelOneCategory | forthLevelCategories
            allProductsPerCategory = Product.objects.filter(category_id__in=allItemsPerLevelOneCategory)
            if report_type == 'drill':
                allProductsPerCategory = allProductsPerCategory.filter(brand=second_style)
            salesLinesPerCategory = SalesLine.objects.filter(item_id__in=allProductsPerCategory)
            salesLinesPerCategory = salesLinesPerCategory.filter(sale_id__in=saleObjectsInDateRange)
            salesLinesPerCategory = salesLinesPerCategory.filter(sale_id__in=allSalesPerStore)
            categoryRow = calculationsOnQueryset(self, salesLinesPerCategory, productCategory, trueGP, report_type, staff)
            if report_type == 'categoryanalysisdetailed':
                if categoryRow["quantity"] == 0:
                    pass
                else:
                    resultSet.append(categoryRow)
            else:
                resultSet.append(categoryRow)
    return resultSet


def applySort(self, objects, params):
    report_type = self.kwargs.get('report_type') or self.request.GET.get('report_type')\
                     or self.request.POST.get('report_type') or ''
    if report_type == 'brandanalysis' or report_type == '2' or report_type == 'brandanalysisdetailed':
        sortTypes = self.request.GET.getlist('sortTypes') or self.request.POST.getlist('sortTypes') or []
        if not sortTypes:
            if report_type == 'brandanalysisdetailed' or report_type == 'categoryanalysisdetailed':
                pass
            else:
                objects.sort(key=operator.itemgetter('quantity'), reverse=True)
        try:
            if sortTypes[0] == "0":
                objects.sort(key=operator.itemgetter('quantity'), reverse=True)
            elif sortTypes[0] == "1":
                objects.sort(key=operator.itemgetter('totalSalesSell'), reverse=True)
            elif sortTypes[0] == "2":
                objects.sort(key=operator.itemgetter('totalSalesNett'), reverse=True)
            elif sortTypes[0] == "3":
                objects.sort(key=operator.itemgetter('GP'), reverse=True)
            elif sortTypes[0] == "4":
                objects.sort(key=operator.itemgetter('GPPerc'), reverse=True)
            else:
                if report_type == 'brandanalysis' or report_type == 'brandanalysisdetailed':
                    objects.sort(key=operator.itemgetter('brand'))
                else:
                    objects.sort(key=operator.itemgetter('category'))
        except IndexError:
            pass
        params['sortTypes'] = ','.join([x for x in sortTypes]) if len(sortTypes) else ''
        return objects
    else:
        return objects


def calculationsOnQueryset(self, salesLinesPerBrand, typeChoice, trueGP, report_type, staff):
    quantityTotal = 0
    sellTotal = 0
    nettTotal = 0
    for saleLine in salesLinesPerBrand:
        quantityTotal += saleLine.quantity
        sellMinusGST = getPriceMinusGST(saleLine.unitPrice)
        sellMinusGST *= saleLine.quantity
        sellTotal += sellMinusGST
        nettTotal += Decimal(saleLine.item.spanNet) * saleLine.quantity
    GP = sellTotal - nettTotal
    if sellTotal == 0:
        GPPerc = 0
    else:
        GPPerc = ((sellTotal-nettTotal) / sellTotal) * 100
        GPPerc = str(round(GPPerc, 2))
    if len(trueGP):
        GP = sellTotal - (nettTotal + 10)
    row = {}
    if report_type == 'brandanalysisdetailed' or report_type == 'categoryanalysisdetailed':
        row['name'] = staff.name
    if report_type == 'brandanalysis' or report_type == 'brandanalysisdetailed':
        row['brand'] = typeChoice.brand
    else:
        row['category'] = typeChoice.name
    row['quantity'] = quantityTotal
    row['totalSalesSell'] = sellTotal
    row['totalSalesNett'] = nettTotal
    row['GP'] = GP
    row['GPPerc'] = GPPerc
    row['isDataRow'] = "isDataRow"
    row['brandId'] = typeChoice.id
    return row


def getWarrantySales(self, params, store):
    staffs = Staff.objects.filter(store=store)
    startDate, endDate = getFilterDates(self, params)
    filteredSalesByDate = reportTags.filterSalesByDate(startDate, endDate)
    sales = filteredSalesByDate.filter(salesPerson__in=staffs)
    uniqueIdentifierObjectsForReport = SalesLine.objects.filter(sale__in=sales)
    warranties = Warranty.objects.all()
    warrantyList = []
    for warranty in warranties:
        warrantyList.append(warranty.product_ptr)
    uniqueIdentifierObjectsForReport = uniqueIdentifierObjectsForReport.filter(item__in=warrantyList)
    param1 = []
    date, invoice = getWarrantyFigures(uniqueIdentifierObjectsForReport)
    param1.append(date)
    param1.append(invoice)
    return uniqueIdentifierObjectsForReport, param1


def getWarrantyFigures(uniqueIdentifierObjectsForReport):
    date = []
    invoice = []
    for i in uniqueIdentifierObjectsForReport:
        sale = Sale.objects.get(id=i.sale.id)
        date.append(sale.created)
        invoice.append(sale.code)
    return date, invoice


def getDistroData():
    uniqueIdentifierObjectsForReport = Postcode.objects.all()
    postCodes = []
    for uniqueIdentifierObject2 in uniqueIdentifierObjectsForReport:
        postCodes.append(int(uniqueIdentifierObject2.code))
    sortedUniquePostcodes = sorted(set(postCodes))
    return sortedUniquePostcodes


def applyFilterSwitch(self, reportType, params, uniqueIdentifierObjectsForReport):
    if reportType == "invoiceByDate":
        pass
    return uniqueIdentifierObjectsForReport


def convertQueryset(uniqueIdentifierObjectsForReport, reportType, param1=[]):
    resultSet = []
    rowNumber = -1
    appendCounter = -1
    #convert this queryset to list so we can use sort method in the next sort function
    for uniqueIdentifierObject in uniqueIdentifierObjectsForReport:
        row = {}
        rowNumber += 1
        if reportType == "distribution":
            row['code'] = uniqueIdentifierObject
            row['state'] = reportTags.getState(uniqueIdentifierObject)
            row['salesTotalInc'] = reportTags.getSalesTotalInc(1, uniqueIdentifierObject)
            row['salesTotalEx'] = reportTags.getSalesTotalEx(1, uniqueIdentifierObject)
            row['costPriceTotal'] = reportTags.getCostPriceTotal(1, uniqueIdentifierObject)
            row['gpDollarTotal'] = reportTags.getGPDollarTotal(1, uniqueIdentifierObject)
            row['gpPercTotal'] = reportTags.getGPPercTotal(1, uniqueIdentifierObject)
        elif reportType == "salesByCustomer":
            row['firstName'] = uniqueIdentifierObject.firstName
            row['lastName'] = uniqueIdentifierObject.lastName
            row['salesTotalInc'] = reportTags.getSalesTotalInc(2, uniqueIdentifierObject.id)
            row['salesTotalEx'] = reportTags.getSalesTotalEx(2, uniqueIdentifierObject.id)
            row['costPriceTotal'] = reportTags.getCostPriceTotal(2, uniqueIdentifierObject.id)
            row['gpDollarTotal'] = reportTags.getGPDollarTotal(2, uniqueIdentifierObject.id)
            row['gpPercTotal'] = reportTags.getGPPercTotal(2, uniqueIdentifierObject.id)
            row['quantityOfSalesByCust'] = reportTags.getQuantityOfSalesByCust(2, uniqueIdentifierObject.id)
        elif reportType == "salesperson":
            row['id'] = uniqueIdentifierObject.id
            row['name'] = uniqueIdentifierObject.name
        elif reportType == "warranties":
            row['salesPerson'] = reportTags.getRepForWarranty(0, uniqueIdentifierObject.id)
            row['date'] = str(param1[0][rowNumber])
            row['sale'] = param1[1][rowNumber]
            row['invoice'] = param1[1][rowNumber]
            row['warranty'] = uniqueIdentifierObject.modelNum
            row['for'] = uniqueIdentifierObject.warrantyRef
            row['price'] = uniqueIdentifierObject.unitPrice
        else:
            appendCounter = 0
        if not appendCounter == 0:
            resultSet.append(row)
    resultSet = applyReportSort(reportType, resultSet)
    return resultSet


def applyReportSort(reportType, objects):
    # if reportType == "distribution":
    #     objects.sort(key=operator.itemgetter('totalSales'), reverse=True)
    # if reportType == "salesByCustomer":
    #     objects.sort(key=operator.itemgetter('totalSales'), reverse=True)
    if reportType == "salesperson":
        objects.sort(key=operator.itemgetter('name'), reverse=True)
    else:
        pass
    return objects


def getWarrantiesObjects(self, params):
    # startDate = getStartDate(self, params)
    # endDate = getEndDate(self, params)
    startDate = getStartDate(params, self.request.session['startDateList'])
    endDate = getEndDate(params, self.request.session['endDateList'])
    trueGP = setTrueGP(self, params)
    report_type = self.kwargs.get('report_type') or self.request.GET.get('report_type')\
                     or self.request.POST.get('report_type') or ''
    objects = SalesLine.objects.all()
    return objects


def getMonthlySalesObjects(store, params):
    resultSet = []
    rowNumber = -1
    appendCounter = -1
    reportType = "monthly"
    #convert this queryset to list so we can use sort method in the next sort function
    # for uniqueIdentifierObject in uniqueIdentifierObjectsForReport:
    for uniqueIdentifierObject in range(12):
        rowNumber += 1
        row = {}
        uniqueIdentifierObject += 1
        if reportType == "monthly":
            row['month'] = getMonthName(0, str(uniqueIdentifierObject))
            row['released'] = getReleased("true", str(uniqueIdentifierObject), store)
            row['gp'] = getGPDollarTotalMonthly("true", str(uniqueIdentifierObject), store)
            row['gpPerc'] = getGPPercTotalMonthly("true", str(uniqueIdentifierObject), store)
            row['income'] = "tba"
            row['accounts'] = "tba"
            row['insert'] = ""
            row['monthLast'] = getMonthName(0, str(uniqueIdentifierObject))
            row['releasedLast'] = getReleased("false", str(uniqueIdentifierObject), store)
            row['gpLast'] = getGPDollarTotalMonthly("false", str(uniqueIdentifierObject), store)
            row['gpPercLast'] = getGPPercTotalMonthly("false", str(uniqueIdentifierObject), store)
            row['incomeLast'] = "tba"
            row['accountsLast'] = "tba"
        else:
            appendCounter = 0
        if not appendCounter == 0:
            resultSet.append(row)
    return resultSet


def getGPPercTotalMonthly(current, monthArg, store):
    salesLines = getMonthlySalesLines(current, monthArg, store)
    GPTotal = 0
    for x in salesLines:
        GST = D(settings.GST)
        sellEx = x.unitPrice / GST
        sellEx = Decimal(sellEx)
        # get nett ex
        product = Product.objects.filter(id=x.item_id)
        nettEx = product[0].spanNet
        if sellEx == 0:
            GPPerc = 0
        else:
            GPPerc = ((sellEx-nettEx) / sellEx) * 100
        GPTotal += GPPerc

    if len(salesLines) == 0:
        GPTotal = 0
    else:
        GPTotal = GPTotal / len(salesLines)
    return GPTotal


def getGPDollarTotalMonthly(current, monthArg, store):
    currentYear = int(datetime.datetime.now().strftime("%Y"))
    lastYear = int(datetime.datetime.now().strftime("%Y")) - 1
    sales = getStoreSales(store)
    sales = sales.filter(fullPaymentDate__month=monthArg)
    if current == "true":
        sales = sales.filter(fullPaymentDate__year=currentYear)
    else:
        sales = sales.filter(fullPaymentDate__year=lastYear)
    salesLines = SalesLine.objects.filter(sale_id__in=sales)
    GPDollarTotal = 0
    for salesLine in salesLines:
        GPDollarTotal += getGPDollar(salesLine, salesLine)
    return GPDollarTotal


def getGPDollar(value, salesLine):  # GP$ = SellPrice(ex) - SpanNett(ex)
    sellMinusGST = getPriceMinusGST(salesLine.unitPrice)
    product = Product.objects.filter(id=salesLine.item_id)
    spanNet = product[0].spanNet
    spanNet = Decimal(spanNet)
    sellMinusGST *= salesLine.quantity
    spanNet *= salesLine.quantity
    GPDollar = sellMinusGST - spanNet
    return GPDollar


def getReleased(current, monthArg, store):
    salesLines = getMonthlySalesLines(current, monthArg, store)
    salesLines = salesLines.exclude(released=0)
    totalReleased = 0
    for salesLine in salesLines:
        totalReleased += salesLine.released
    return totalReleased


def getMonthlySalesLines(current, monthArg, store):
    currentYear = int(datetime.datetime.now().strftime("%Y"))
    lastYear = int(datetime.datetime.now().strftime("%Y")) - 1
    sales = getStoreSales(store)
    sales = sales.filter(fullPaymentDate__month=monthArg)
    if current == "true":
        sales = sales.filter(fullPaymentDate__year=currentYear)
    else:
        sales = sales.filter(fullPaymentDate__year=lastYear)
    salesLines = SalesLine.objects.filter(sale_id__in=sales)
    return salesLines


def getMonthName(current, month):
    if month == '1':
        month = "January"
    elif month == '2':
        month = "February"
    elif month == '3':
        month = "March"
    elif month == '4':
        month = "April"
    elif month == '5':
        month = "May"
    elif month == '6':
        month = "June"
    elif month == '7':
        month = "July"
    elif month == '8':
        month = "August"
    elif month == '9':
        month = "September"
    elif month == '10':
        month = "October"
    elif month == '11':
        month = "November"
    elif month == '12':
        month = "December"
    else:
        month = "none"
    return month


def getSalesPerStoreOrHO(self):
    second_style = self.kwargs.get('second_style') or self.request.GET.get('second_style')\
                     or self.request.POST.get('second_style') or ''
    if second_style == '1' or second_style == '2':
        allSalesPerStore = Sale.objects.all()
    else:
        terminalsPerStore = Terminal.objects.filter(store_id=self.request.store)
        allSalesPerStore = Sale.objects.filter(terminal_id__in=terminalsPerStore)
    return allSalesPerStore


def filterCategories(self, params, productCategories):
    productCategory = self.request.GET.getlist('category') or self.request.POST.getlist('category') or []
    productCategory = filter(len, productCategory)
    if len(productCategory):
        productCategoryList = [int(x) for x in productCategory]
        productCategories = productCategories.filter(id__in=productCategoryList)
    params['category'] = ','.join([x for x in productCategory]) if len(productCategory) else ''
    return productCategories


def setTrueGP(self, params):
    trueGP = self.request.GET.getlist('chkTrueGP') or self.request.POST.getlist('chkTrueGP') or []
    trueGP = filter(len, trueGP)
    params['chkTrueGP'] = ','.join([x for x in trueGP]) if len(trueGP) else ''
    if len(trueGP):
        self.context_append['isTrueGP'] = True
    return trueGP


def filterBrands(self, params, brands):
    brand = self.request.GET.getlist('brand') or self.request.POST.getlist('brand') or []
    brand = filter(len, brand)
    if len(brand):
        brandList = [int(x) for x in brand]
        brands = brands.filter(id__in=brandList)
    params['brand'] = ','.join([x for x in brand]) if len(brand) else ''
    return brands

def filterBrands2(self, params, brands):
    brand = self.request.GET.getlist('product') or self.request.POST.getlist('product') or []
    brand = filter(len, brand)
    if len(brand):
        brandList = [int(x) for x in brand]
        brands = brands.filter(id__in=brandList)
    params['product'] = ','.join([x for x in brand]) if len(brand) else ''
    return brands

    # get start date for report
    startDate = "2000-04-01 09:11:24.880000"  # default dates
    startDateList = self.request.GET.getlist('model') or self.request.POST.getlist('model') or []
    startDateList = filter(len, startDateList)
    params['model'] = ','.join([x for x in startDateList]) if len(startDateList) else ''
    return startDate


class itemisedFunctions(object):
    pass


def getSalesLinesPerStoreOrHO(self, params):
    startDate = getStartDate(params, self.request.session['startDateList'])
    endDate = getEndDate(params, self.request.session['endDateList'])
    # startDate = getStartDate(self, params)
    # endDate = getEndDate(self, params)
    salesPeople = getSalesPeople(self, params)
    # trueGP = setTrueGP(self, params)
    second_style = self.kwargs.get('second_style') or self.request.GET.get('second_style') or \
                self.request.POST.get('second_style') or ''
    if second_style == '0':
        terminalsPerStore = Terminal.objects.filter(store_id=self.request.store)
        allSalesPerStore = Sale.objects.filter(terminal_id__in=terminalsPerStore)
        if salesPeople:
            allSalesPerStore = allSalesPerStore.filter(salesPerson__in=salesPeople)
        allSalesPerStore = allSalesPerStore.filter(purchaseDate__range=[startDate, endDate])
        allSalesLinesPerStore = SalesLine.objects.filter(sale_id__in=allSalesPerStore)
    else:
        saleObjectsInDateRange = Sale.objects.filter(purchaseDate__range=[startDate, endDate])
        if salesPeople:
            saleObjectsInDateRange = saleObjectsInDateRange.filter(salesPerson__in=salesPeople)
        allSalesLinesPerStore = SalesLine.objects.filter(sale_id__in=saleObjectsInDateRange)
    allSalesLinesPerStore = doItemisedBrandFilter(self, params, allSalesLinesPerStore)
    allSalesLinesPerStore = doItemisedProductFilter(self, params, allSalesLinesPerStore)
    allSalesLinesPerStore = convertQueryset(self, params, allSalesLinesPerStore, "itemised", param1=[])
    return allSalesLinesPerStore


def convertQueryset(self, params, uniqueIdentifierObjectsForReport, reportType, param1=[]):
    resultSet = []
    rowNumber = -1
    appendCounter = -1
    #convert this queryset to list so we can use sort method in the next sort function
    for uniqueIdentifierObject in uniqueIdentifierObjectsForReport:
        rowNumber += 1
        row = {}
        if reportType == "itemised":
            row['saleCode'] = reportTags.getSaleCode(0, uniqueIdentifierObject)
            row['brand'] = reportTags.getBrand(0, uniqueIdentifierObject)
            row['model'] = reportTags.getModel(0, uniqueIdentifierObject)
            row['type'] = reportTags.getType(uniqueIdentifierObject)
            row['desc'] = reportTags.getDesc(0, uniqueIdentifierObject)
            row['quantity'] = uniqueIdentifierObject.quantity
            row['invoice'] = "na"
            row['sellInc'] = reportTags.getSellInc(0, uniqueIdentifierObject)
            row['sellEx'] = reportTags.getSellEx(0, uniqueIdentifierObject)
            row['nett'] = reportTags.getNett(0, uniqueIdentifierObject)
            row['gpDollar'] = reportTags.getGPDollar(0, uniqueIdentifierObject)
            row['gpPerc'] = reportTags.getGPPerc(0, uniqueIdentifierObject)
            row['rep'] = reportTags.getRep(0, uniqueIdentifierObject)
            row['cust'] = reportTags.getCust(0, uniqueIdentifierObject)
            row['dateSold'] = str(reportTags.getDateSold(0, uniqueIdentifierObject))
            row['paymentDate'] = str(reportTags.getPaymentDate(0, uniqueIdentifierObject))
        elif reportType == "salesperson":
            startDate, endDate = getFilterDates(self, params)
            filteredSalesByDate = reportTags.filterSalesByDate(startDate, endDate)
            row['name'] = uniqueIdentifierObject.name
            row['salesTotalInc'] = reportTags.getSalesTotalInc(3, uniqueIdentifierObject.id, filteredSalesByDate)
            row['salesTotalEx'] = reportTags.getSalesTotalEx(3, uniqueIdentifierObject.id, filteredSalesByDate)
            row['salesExWarrantiesPerSalesperson'] = reportTags.getSalesExWarrantiesPerSalesperson(3, uniqueIdentifierObject.id, filteredSalesByDate)
            row['warrantiesPerSalesperson'] = reportTags.getWarrantiesPerSalesperson(3, uniqueIdentifierObject.id, filteredSalesByDate)
            row['strikeRate'] = reportTags.getStrikeRate(3, uniqueIdentifierObject.id, filteredSalesByDate)
        elif reportType == "distribution":
            startDate, endDate = getFilterDates(self, params)
            filteredSalesByDate = reportTags.filterSalesByDate(startDate, endDate)
            row['code'] = uniqueIdentifierObject
            row['state'] = reportTags.getState(uniqueIdentifierObject)
            row['salesTotalInc'] = reportTags.getSalesTotalInc(1, uniqueIdentifierObject, filteredSalesByDate)
            row['salesTotalEx'] = reportTags.getSalesTotalEx(1, uniqueIdentifierObject, filteredSalesByDate)
            row['costPriceTotal'] = reportTags.getCostPriceTotal(1, uniqueIdentifierObject, filteredSalesByDate)
            row['gpDollarTotal'] = reportTags.getGPDollarTotal(1, uniqueIdentifierObject, filteredSalesByDate)
            row['gpPercTotal'] = reportTags.getGPPercTotal(1, uniqueIdentifierObject, filteredSalesByDate)
            row['type'] = "tba"
        elif reportType == "salesByCustomer":
            startDate, endDate = getFilterDates(self, params)
            filteredSalesByDate = reportTags.filterSalesByDate(startDate, endDate)
            row['lastName'] = uniqueIdentifierObject.lastName
            row['firstName'] = uniqueIdentifierObject.firstName
            row['salesTotalInc'] = reportTags.getSalesTotalInc(2, uniqueIdentifierObject.id, filteredSalesByDate)
            row['salesTotalEx'] = reportTags.getSalesTotalEx(2, uniqueIdentifierObject.id, filteredSalesByDate)
            row['costPriceTotal'] = reportTags.getCostPriceTotal(2, uniqueIdentifierObject.id, filteredSalesByDate)
            row['gpDollarTotal'] = reportTags.getGPDollarTotal(2, uniqueIdentifierObject.id, filteredSalesByDate)
            row['gpPercTotal'] = reportTags.getGPPercTotal(2, uniqueIdentifierObject.id, filteredSalesByDate)
            row['quantityOfSalesByCust'] = reportTags.getQuantityOfSalesByCust(2, uniqueIdentifierObject.id, filteredSalesByDate)
        elif reportType == "warranties":
            row['salesPerson'] = reportTags.getRepForWarranty(0, uniqueIdentifierObject.id)
            row['date'] = str(param1[0][rowNumber])
            row['sale'] = param1[1][rowNumber]
            row['invoice'] = param1[1][rowNumber]
            row['warranty'] = uniqueIdentifierObject.modelNum
            row['for'] = uniqueIdentifierObject.warrantyRef
            row['price'] = uniqueIdentifierObject.unitPrice
        else:
            appendCounter = 0
        if not appendCounter == 0:
            resultSet.append(row)
    return resultSet

def doItemisedBrandFilter(self, params, allSalesLinesPerStore):
    brand = self.request.GET.getlist('brand') or self.request.POST.getlist('brand') or []
    brand = filter(len, brand)
    if len(brand):
        brands = Brand.objects.all()
        brands = filterBrands(self, params, brands)
        products = Product.objects.all()
        products = products.filter(brand__in=brands)
        allSalesLinesPerStore = allSalesLinesPerStore.filter(item_id__in=products)
    return allSalesLinesPerStore



def doItemisedProductFilter(self, params, allSalesLinesPerStore):
    brand = self.request.GET.getlist('product') or self.request.POST.getlist('product') or []
    brand = filter(len, brand)
    if len(brand):
        brands = Product.objects.all()
        brands = filterBrands2(self, params, brands)
        allSalesLinesPerStore = allSalesLinesPerStore.filter(item_id__in=brands)
    return allSalesLinesPerStore





