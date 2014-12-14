from core.models import *
from reports.shortcuts.shortcuts_global import *


def getCustomerObjects(self, params):
    reportType = getReportType(self)
    resultSet = []
    appendCounter = -1
    startDate = getStartDate(params, self.request.session['startDateList'])
    endDate = getEndDate(params, self.request.session['endDateList'])

    # startDate = getStartDate(self, params)
    # endDate = getEndDate(self, params)
    # trueGP = setTrueGP(self, params)
    if reportType == "all":
        uniqueIdentifierObjectsForReport = Postcode.objects.all()
    elif reportType == "email":
        uniqueIdentifierObjectsForReport = Postcode.objects.all()
    elif reportType == "birthdays":
        uniqueIdentifierObjectsForReport = Postcode.objects.all()
    elif reportType == "orders":
        uniqueIdentifierObjectsForReport = Postcode.objects.all()
    elif reportType == "attendance":
        uniqueIdentifierObjectsForReport = Postcode.objects.all()
    elif reportType == "onlySales":
        uniqueIdentifierObjectsForReport = Postcode.objects.all()
    elif reportType == "new":
        uniqueIdentifierObjectsForReport = Brand.objects.all()
    else:
        uniqueIdentifierObjectsForReport = False
    for uniqueIdentifierObject in uniqueIdentifierObjectsForReport:
        row = {}
        if reportType == "all":
            row['id'] = uniqueIdentifierObject.id
            row['code'] = uniqueIdentifierObject.code
            row['locality'] = uniqueIdentifierObject.locality
            row['state'] = uniqueIdentifierObject.state
            row['deliveryOffice'] = uniqueIdentifierObject.deliveryOffice
        elif reportType == "email":
            row['id'] = uniqueIdentifierObject.id
            row['code'] = uniqueIdentifierObject.code
            row['locality'] = uniqueIdentifierObject.locality
            row['state'] = uniqueIdentifierObject.state
            row['deliveryOffice'] = uniqueIdentifierObject.deliveryOffice
        elif reportType == "birthdays":
            row['id'] = uniqueIdentifierObject.id
            row['code'] = uniqueIdentifierObject.code
            row['locality'] = uniqueIdentifierObject.locality
            row['state'] = uniqueIdentifierObject.state
            row['deliveryOffice'] = uniqueIdentifierObject.deliveryOffice
        elif reportType == "orders":
            row['id'] = uniqueIdentifierObject.id
            row['code'] = uniqueIdentifierObject.code
            row['locality'] = uniqueIdentifierObject.locality
            row['state'] = uniqueIdentifierObject.state
            row['deliveryOffice'] = uniqueIdentifierObject.deliveryOffice
        elif reportType == "attendance":
            row['id'] = uniqueIdentifierObject.id
            row['code'] = uniqueIdentifierObject.code
            row['locality'] = uniqueIdentifierObject.locality
            row['state'] = uniqueIdentifierObject.state
            row['deliveryOffice'] = uniqueIdentifierObject.deliveryOffice
        elif reportType == "onlySales":
            row['id'] = uniqueIdentifierObject.id
            row['code'] = uniqueIdentifierObject.code
            row['locality'] = uniqueIdentifierObject.locality
            row['state'] = uniqueIdentifierObject.state
            row['deliveryOffice'] = uniqueIdentifierObject.deliveryOffice
        elif reportType == "new":
            row['id'] = uniqueIdentifierObject.id
            row['code'] = uniqueIdentifierObject.code
            row['locality'] = uniqueIdentifierObject.locality
            row['state'] = uniqueIdentifierObject.state
            row['deliveryOffice'] = uniqueIdentifierObject.deliveryOffice
        else:
            appendCounter = 0
        if not appendCounter == 0:
            resultSet.append(row)
    self.context_append['params'] = params
    return resultSet

