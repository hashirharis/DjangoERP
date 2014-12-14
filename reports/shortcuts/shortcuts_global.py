from datetime import timedelta
from django.utils.timezone import utc
from django.utils import timezone
from users.models import Staff
from pos.models import Sale, Terminal
import datetime
from dateutil.relativedelta import relativedelta
from brutils.templatetags import reportTags
from decimal import *
from pos.models import *
from b2b.models import HeadOfficeInvoice,  HeadOfficeInvoiceLine


class GlobalFunctions(object):
    pass


def setStartEndDates(self):
    startDateList = self.request.GET.getlist('startDate') or self.request.POST.getlist('startDate') or []
    endDateList = self.request.GET.getlist('endDate') or self.request.POST.getlist('endDate') or []
    self.request.session['startDateList'] = startDateList
    self.request.session['endDateList'] = endDateList


def getStoreSales(store):
    terminals = Terminal.objects.filter(store=store)
    sales = Sale.objects.filter(terminal__in=terminals)
    return sales


def getStoreHOInvLines(self, store, params):
    startDate, endDate = getFilterDates(self, params)
    headOfficeInvoices = HeadOfficeInvoice.objects.filter(createdDate__range=[startDate, endDate])
    headOfficeInvoices = headOfficeInvoices.filter(store=store)
    headOfficeInvoiceLines = HeadOfficeInvoiceLine.objects.filter(invoice__in=headOfficeInvoices)
    return headOfficeInvoiceLines


def filterByStore(store, queryset):
    queryset = queryset.filter(store=store)
    return queryset


def getPriceMinusGST(price):
    GST = D(settings.GST)
    priceMinusGST = price / GST
    priceMinusGST = str(round(priceMinusGST, 2))
    priceMinusGST = Decimal(priceMinusGST)
    return priceMinusGST


def getFilterDates(self, params):
    start = getStartDate(params, self.request.session['startDateList'])
    end = getEndDate(params, self.request.session['endDateList'])
    return start, end


def getStartDate(params, startDateList):
    # get start date for report
    startDate = "2000-04-01 09:11:24.880000"  # default dates
    # startDateList = self.request.GET.getlist('startDate') or self.request.POST.getlist('startDate') or []
    startDateList = filter(len, startDateList)
    if len(startDateList):
        try:
            startDate = startDateList[0]
            startDate = datetime.datetime.strptime(startDate, "%m/%d/%Y")
            startDate = startDate.replace(tzinfo=utc)  # convert naive to aware
            startDate = timezone.localtime(startDate)  # converts an aware datetime.datetime to local time
            # startDate = applyOffset(startDate)   # this takes into account filtering by brisbane times as opposed...
                                                       # to UTC dates because the database holds UTC dates
        except IndexError:
            pass
    params['startDate'] = ','.join([x for x in startDateList]) if len(startDateList) else ''
    return startDate


def getEndDate(params, endDateList):
    endDate = "3014-04-01 09:11:24.880000"  # default dates
    # endDateList = self.request.GET.getlist('endDate') or self.request.POST.getlist('endDate') or []
    endDateList = filter(len, endDateList)
    if len(endDateList):
        try:
            endDate = endDateList[0]
            endDate = datetime.datetime.strptime(endDate, "%m/%d/%Y")
            endDate = endDate.replace(tzinfo=utc)  # convert naive to aware
            endDate = timezone.localtime(endDate)  # converts an aware datetime.datetime to local time
            endDate = endDate + timedelta(days=1)
            # endDate = applyOffset(endDate)   # this takes into account filtering by brisbane times as opposed...
                                                   # to UTC dates because the database holds UTC dates
        except IndexError:
            pass
    params['endDate'] = ','.join([x for x in endDateList]) if len(endDateList) else ''
    return endDate


def getSalesPeople(self, params):
    salesPeople = []
    salesPeopleList = self.request.GET.getlist('salesPerson') or self.request.POST.getlist('salesPerson') or []
    salesPeopleList = filter(len, salesPeopleList)
    params['salesPeople'] = ','.join([x for x in salesPeopleList]) if len(salesPeopleList) else ''
    if len(salesPeopleList):
        try:
            salesPeople = Staff.objects.filter(id__in=salesPeopleList)
        except IndexError:
            pass
        return salesPeople
    return False


def applyOffset(userInputUTC):
    from datetime import datetime
    from pytz import timezone
    # Current time in UTC
    userInputUTC = datetime.now(timezone('UTC'))
    # Convert to Australia/Brisbane time zone for filtering
    brisbaneTime = userInputUTC.astimezone(timezone('Australia/Brisbane'))
    return brisbaneTime


class CreateExcelFunctions(object):
    pass


def get_current_path(request):
    # just a small context processor , to be used in the reports export page
    if "?" in request.get_full_path():
        return {
           'search_string':''+request.get_full_path().split('?').pop()
         }
    else:
        return {
            'search_string': ''
        }


def createDict(results, report_type):
    holder = []
    if report_type == "itemised":
        for saleLine in results:
            objHolder = {}
            objHolder['1'] = saleLine.sale.code
            objHolder['2'] = saleLine.item.brand.brand
            objHolder['3'] = saleLine.modelNum
            objHolder['4'] = reportTags.getType(saleLine, saleLine)
            objHolder['5'] = saleLine.item.description
            objHolder['6'] = saleLine.quantity
            objHolder['7'] = reportTags.getInvoiceRef(saleLine, saleLine)
            objHolder['8'] = saleLine.unitPrice
            objHolder['9'] = reportTags.getSellEx(saleLine, saleLine)
            objHolder['10'] = saleLine.item.spanNet
            objHolder['11'] = reportTags.getGPDollar(saleLine, saleLine)
            objHolder['12'] = reportTags.getGPPerc(saleLine, saleLine)
            objHolder['13'] = reportTags.getRep(saleLine, saleLine)
            objHolder['14'] = reportTags.getCust(saleLine, saleLine)
            objHolder['15'] = str(reportTags.getDateSold(saleLine, saleLine).replace(tzinfo=None).strftime('%Y/%m/%d %I:%M %p'))
            objHolder['16'] = str(reportTags.getPaymentDate(saleLine, saleLine).replace(tzinfo=None).strftime('%Y/%m/%d %I:%M %p'))
            holder.append(objHolder)
        return holder
    elif report_type == "itemisedsummary":
        pass


def createCSVDataObject(self, CSV_data, report_type, report_class):
    if report_class == 'tax':
        headers = createTaxData(self, report_type, CSV_data)
    elif report_class == "customer":
        headers = createCustData(self, report_type, CSV_data)
    elif report_class == "banking":
        headers = createBankData(self, report_type, CSV_data)
    elif report_class == "ledger":
        headers = createLedgerData(self, report_type, CSV_data)
    elif report_class == "jsb":
        headers = createJSBData(self, report_type, CSV_data)
    elif report_class == "warranties":
        headers = createWarrData(self, report_type, CSV_data)
    elif report_class == "irp":
        headers = createIRPData(self, report_type, CSV_data)
    elif report_class == "inward":
        headers = createInwardData(self, report_type, CSV_data)
    else:  # if is sales
        headers = createSalesData(self, report_type, CSV_data)
    return headers


def createCustData(self, report_type, CSV_data):
    headers = ['Number', 'Title', 'First', 'Last', 'Address',
               'Suburb', 'City', 'Postcode', 'Email', 'Password']
    for obj in self.result:
        row = [obj['code'], obj['locality'], obj['state'], obj['deliveryOffice']]
        CSV_data.append(row)
    return headers


def createBankData(self, report_type, CSV_data):
    if report_type == "bankingReport":
        headers = ['id', 'Checked', 'Date', 'Store',
                   'Cash/Chq', 'Cards', 'Direct Deposit',
                   'Discrepancy', 'Retention', 'Ledger', 'Bad Debt']
        for obj in self.result:
            row = [obj['code'], obj['locality'], obj['state'], obj['deliveryOffice']]
            CSV_data.append(row)
    return headers


def createLedgerData(self, report_type, CSV_data):
    if report_type == "statements":
        headers = ['Cust', 'Type', 'Account', 'Name',
                   'Date', 'Type', 'Acc Balance', 'Cred Balance',
                   'Acc/Credit Balance', 'Money Held']
        for obj in self.result:
            row = [obj['code'], obj['locality'], obj['state'], obj['deliveryOffice']]
            CSV_data.append(row)
    elif report_type == "aged":
        headers = ['Last Name', 'First Name', 'Amt Owed', '30 day', '60 day', '90 day']
        for obj in self.result:
            row = [obj['code'], obj['locality'], obj['state'], obj['deliveryOffice']]
            CSV_data.append(row)
    elif report_type == "selected":
        headers = ['Cust', 'Acc Date', 'Type', 'Total', 'Status']
        for obj in self.result:
            row = [obj['code'], obj['locality'], obj['state'], obj['deliveryOffice']]
            CSV_data.append(row)
    return headers


def createJSBData(self, report_type, CSV_data):
    if report_type == "jsb1":
        headers = ['Model', 'status']
        for obj in self.result:
            row = [obj['model'], obj['status']]
            CSV_data.append(row)
    elif report_type == "jsb2":
        headers = ['Model',
                   'Brand',
                   'Category',
                   'Name',
                   'Web Price',
                   'Short Desc',
                   'Web Desc',
                   'Specifications',
                   'Man Warranty',
                   'Cat Price',
                   'Cat Start Date',
                   'Cat End Date',
                   ]
        for obj in self.result:
            row = [obj['product'],
                   obj['brand'],
                   obj['category'],
                   obj['name'],
                   obj['webPrice'],
                   obj['shortDesc'],
                   obj['webDesc'],
                   obj['specifications'],
                   obj['manWarranty'],
                   obj['catPrice'],
                   obj['catStartDate'],
                   obj['catEndDate']]
            CSV_data.append(row)
    return headers


def createWarrData(self, report_type, CSV_data):
    if report_type == "warranty":
        headers = ['Model Code', 'Cust', 'Store', 'Sales Person', 'Description', 'Purchase Date',
                   'Brand', 'Purchase inc', 'Warr Price', 'Comment']
        for obj in self.result:
            row = [obj['modelNum'], obj['cust'], obj['store'], obj['salesPerson'], obj['description'], obj['purchaseDate'],
                   obj['brand'], obj['purchasePrice'], obj['unitPrice'], obj['comment']]
            CSV_data.append(row)
    return headers


def createIRPData(self, report_type, CSV_data):
    if report_type == "storePurchases":
        headers = ['Distributor',
                   'Store Name',
                   'State',
                   'Date',
                   'Invoice',
                   'Type',
                   'Ref',
                   'Class/Type/Cat',
                   'Model',
                   'Qty',
                   'Unit Price ex',
                   'Total Inv inc',
                   'Total Net inc']
        for obj in self.result:
            row = [obj['Distributor'],
                   obj['StoreName'],
                   obj['State'],
                   obj['Date'],
                   obj['Invoice'],
                   obj['InvType'],
                   obj['Ref'],
                   obj['Class'],
                   obj['item'],
                   obj['quantity'],
                   obj['invoicePrice'],
                   obj['TotalInvinc'],
                   obj['TotalNetinc'],
                   ]
            CSV_data.append(row)
    elif report_type == "extended":
        headers = ['Store', 'Distributor', 'Invoice', 'Net Price inc', 'Due Date']
        for obj in self.result:
            row = [obj['code'], obj['locality'], obj['state'], obj['deliveryOffice']]
            CSV_data.append(row)
    elif report_type == "invoiceByDate":
        headers = ['Invoice', 'Type', 'Distributor', 'Invoice Date',
                   'Invoice Amt', 'Order', 'Store', 'Operator', 'Date Entered']
        for obj in self.result:
            row = [obj['invoiceNumber'],
                   obj['type'],
                   # "brand",
                   obj['distributor'],
                   obj['invoiceDate'],
                   obj['invTotalExGST'],
                   obj['orderReference'],
                   # "store",
                   obj['store'],
                   # "staff",
                   obj['createdBy'],
                   obj['createdDate']]
            CSV_data.append(row)
    elif report_type == "storeListing":
        headers = ['Name',
                   'Address',
                   'Land line',
                   'Mobile',
                   'Email',
                   'Fax']
        for obj in self.result:
            row = [obj['name'],
                   obj['address'],
                   obj['landphone'],
                   obj['mobphone'],
                   obj['email'],
                   obj['fax'],
                   ]
            CSV_data.append(row)
    elif report_type == "b2b":
        headers = ['Supplier', 'Invoice', 'Date', 'Order Ref ',
                   'Store', 'Invoice Amt', 'Printed']
        for obj in self.result:
            row = [obj['code'], obj['locality'], obj['state'], obj['deliveryOffice']]
            CSV_data.append(row)
    elif report_type == "wholesale":
        headers = ['Manufacturer', 'Model', 'Desc', 'Price', 'RRP Price', 'Last Change']
        for obj in self.result:
            row = [obj['code'], obj['locality'], obj['state'], obj['deliveryOffice']]
            CSV_data.append(row)
    elif report_type == "rebates":
        headers = ['Distributor',
                   'TotInv inc',
                   'Store Net inc',
                   'HO Rebate',
                   'HO $Bonus inc',
                   'HO %Bonus inc',
                   'HO VC Bonus inc',
                   'HO Net inc',
                   'Diff']
        for obj in self.result:
            row = [obj['distributor'],
                   obj['totInv'],
                   obj['storeNet'],
                   obj['HORebate'],
                   obj['HODollarBonus'],
                   obj['HOPercBonus'],
                   obj['HOVCBonus'],
                   obj['HONet'],
                   obj['diff']]
            CSV_data.append(row)
    elif report_type == "IAS":
        headers = ['Store',
                   'Purchase Orders',
                   'IRP Invoices',
                   'Total Purchase',
                   'Extended Credit',
                   'Credit Debt',
                   'Limit',
                   'Open to Buy',
                   'Permit',
                   ]
        for obj in self.result:
            row = [obj['name'],
                   obj['purchaseOrders'],
                   obj['iRPInvoices'],
                   obj['totalPurchase'],
                   obj['extendedCredit'],
                   obj['creditDebt'],
                   obj['limit'],
                   obj['openBuy'],
                   obj['permit'],
                   ]
            CSV_data.append(row)
    return headers


def createInwardData(self, report_type, CSV_data):
    if report_type == "goodsInward":
        headers = ['Purchases', 'Ref No', 'Inv Date', 'Booked In', 'Qty', 'Brand',
                   'Model', 'Book Price', 'Act Invoice', 'Book Net inc',
                   'Unit Price inc', 'Total inc', 'Transfer']
        for obj in self.result:
            row = [obj['code'], obj['locality'], obj['state'], obj['deliveryOffice']]
            CSV_data.append(row)
    return headers


def createTaxData(self, report_type, CSV_data):
    if report_type == "dailysnapshot":
        headers = ['Date', 'In Stock', 'Wait', 'Inv', 'Credit Note', 'Held', 'NSBI', 'New Sales', 'Canc Sales', 'Debtor', 'Credits', 'Held Money']
        for obj in self.result:
            row = [obj['code'], obj['locality'], obj['state'], obj['deliveryOffice']]
            CSV_data.append(row)
    elif report_type == "taxReport":
        headers = ['??', '??', '??', '??']
        for obj in self.result:
            row = [obj['code'], obj['locality'], obj['state'], obj['deliveryOffice']]
            CSV_data.append(row)
    return headers


def createSalesData(self, report_type, CSV_data):
    if report_type == 'brandanalysis':
        headers = ['Brand', 'Qty', 'Sell', 'Nett', 'GP', 'GP%']
        for obj in self.result:
            row = [obj['brand'], obj['quantity'], obj['totalSalesSell'], obj['totalSalesNett'], obj['GP'], obj['GPPerc']]
            CSV_data.append(row)
    elif report_type == 'brandanalysisdetailed':
        headers = ['Name', 'Brand', 'Qty', 'Sell', 'Nett', 'GP', 'GP%']
        for obj in self.result:
            row = [obj['name'], obj['brand'], obj['quantity'], obj['totalSalesSell'], obj['totalSalesNett'], obj['GP'], obj['GPPerc']]
            CSV_data.append(row)
    elif report_type == 'categoryanalysis':
        headers = ['Class', 'Qty', 'Sell', 'Nett', 'GP', 'GP%']
        for obj in self.result:
            row = [obj['category'], obj['quantity'], obj['totalSalesSell'], obj['totalSalesNett'], obj['GP'], obj['GPPerc']]
            CSV_data.append(row)
    elif report_type == 'categoryanalysisdetailed':
        headers = ['Name', 'Class', 'Qty', 'Sell', 'Nett', 'GP', 'GP%']
        for obj in self.result:
            row = [obj['name'], obj['category'], obj['quantity'], obj['totalSalesSell'], obj['totalSalesNett'], obj['GP'], obj['GPPerc']]
            CSV_data.append(row)
    elif report_type == "itemised":
        headers = ['Sale id', 'Brand', 'Model', 'Type', 'Desc', 'Quantity', 'Invoice', 'Sell inc',
                   'Sell ex', 'Nett', 'GP', 'GP %', 'Sold by', 'Cust', 'Sold', 'Payment']
        for obj in self.result:
            row = [obj['saleCode'], obj['brand'], obj['model'], obj['type'],
                   obj['desc'], obj['quantity'], obj['invoice'], obj['sellInc'], obj['sellEx'], obj['nett'],
                   obj['gpDollar'], obj['gpPerc'], obj['rep'], obj['cust'], obj['dateSold'], obj['paymentDate']]
            CSV_data.append(row)
    elif report_type == "itemisedsummary":
        headers = createItemisedSummary(self, CSV_data)
    elif report_type == 'monthly':
        headers = createMonthly(self, CSV_data)
    elif report_type == "distribution":
        headers = createDistroSummary(self, CSV_data)


    elif report_type == "salesperson":
        headers = ['Sales Person', 'Sales Total inc', 'Sales Total ex',
                   'Sale Items', 'Cust Care Plans', 'Strike rate']
        for obj in self.result:
            row = [obj['name'],
                   obj['salesTotalInc'],
                   obj['salesTotalEx'],
                   obj['salesExWarrantiesPerSalesperson'],
                   obj['warrantiesPerSalesperson'],
                   obj['strikeRate']]
            CSV_data.append(row)


    elif report_type == "salesByCustomer":
        headers = ['Last Name', 'First Name', 'Sell inc', 'Sell ex', 'Cost', 'GP', 'GP%', 'Qty']
        for obj in self.result:
            row = [obj['lastName'],
                   obj['firstName'],
                   obj['salesTotalInc'],
                   obj['salesTotalEx'],
                   obj['costPriceTotal'],
                   obj['gpDollarTotal'],
                   obj['gpPercTotal'],
                   obj['quantityOfSalesByCust']]
            CSV_data.append(row)
    elif report_type == "warranties":
        headers = ['Sales Person', 'Date', 'Sale', 'Invoice', 'Cust Care Plan', 'For', 'Price']
        for obj in self.result:
            row = [obj['salesPerson'],
                   obj['date'],
                   obj['sale'],
                   obj['invoice'],
                   obj['warranty'],
                   obj['for'],
                   obj['price']]
            CSV_data.append(row)
    return headers


def createDistroSummary(self, CSV_data):
    headers = ['Post Code', 'State', 'Sell Price Inc', 'Sell Price Ex', 'Cost', 'GP', 'GP%', 'Type']
    for obj in self.result:
        row = [obj['code'],
               obj['state'],
               obj['salesTotalInc'],
               obj['salesTotalEx'],
               obj['costPriceTotal'],
               obj['gpDollarTotal'],
               obj['gpPercTotal'],
               obj['type']]
        CSV_data.append(row)
    return headers


def createItemisedSummary(self, CSV_data):
    headers = ['Sales Person', 'Category', 'Sold', '$Total', 'Refunded', '$Total', 'Transferred', 'Transferred Price']
    for obj in self.result:
        if len(obj) == 1:
            row = [obj['staffName'], '', '', '', '', '', '', '']

        elif len(obj) == 0:
            row = ['', '', '', '', '', '', '', '']
        else:
            row = ['', obj['level2Category'], obj['totalQuantity'], obj['totalPrice'],
                   obj['totalReturnedQuantity'], obj['totalReturnedPrice'], 'NA', 'NA']
        CSV_data.append(row)
    return headers


def createMonthly(self, CSV_data):
    headers = ['Month',
               'Released',
               'GP',
               'GP%',
               'Income',
               'Accounts',
               '',
               'Month',
               'Released',
               'GP',
               'GP%',
               'Income',
               'Accounts',
               ]
    NOW = datetime.datetime.now()
    currentYear = NOW.strftime('%Y')
    lastYear = NOW + relativedelta(years=-1)
    lastYear = lastYear.strftime('%Y')
    row = [lastYear,
           "",
           "",
           "",
           "",
           "",
           "",
           currentYear,
           "",
           "",
           "",
           "",
           "",
           ]
    CSV_data.append(row)
    for obj in self.result:
        objMonth = obj['month']
        month = str(objMonth)
        monthLast = str(objMonth)
        row = [monthLast,
               obj['releasedLast'],
               obj['gpLast'],
               obj['gpPercLast'],
               obj['incomeLast'],
               obj['accountsLast'],
               obj['insert'],
               month,
               obj['released'],
               obj['gp'],
               obj['gpPerc'],
               obj['income'],
               obj['accounts'],
               ]
        CSV_data.append(row)
    return headers


def getReportClass(self):
        return self.kwargs.get('report_class') or self.request.GET.get('report_class') or self.request.POST.get('report_class') or ''


def getReportType(self):
        return self.kwargs.get('report_type') or self.request.GET.get('report_type') or self.request.POST.get('report_type') or ''
