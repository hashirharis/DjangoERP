from core.models import *
from reports.shortcuts.shortcuts_global import *


def getTaxObjects(self, params):
    reportType = getReportType(self)
    resultSet = []
    counter = -1
    startDate = getStartDate(params, self.request.session['startDateList'])
    endDate = getEndDate(params, self.request.session['endDateList'])
    # startDate = getStartDate(self, params)
    # endDate = getEndDate(self, params)
    # trueGP = setTrueGP(self, params)
    if reportType == "dailysnapshot":
        uniqueIdentifierObjectsForReport = Postcode.objects.all()
    elif reportType == "taxReport":
        uniqueIdentifierObjectsForReport = Postcode.objects.all()
    else:
        uniqueIdentifierObjectsForReport = False
    for uniqueIdentifierObject in uniqueIdentifierObjectsForReport:
        row = {}
        if reportType == "dailysnapshot":
            row['id'] = uniqueIdentifierObject.id
            row['code'] = uniqueIdentifierObject.code
            row['locality'] = uniqueIdentifierObject.locality
            row['state'] = uniqueIdentifierObject.state
            row['deliveryOffice'] = uniqueIdentifierObject.deliveryOffice
        elif reportType == "taxReport":
            row['id'] = uniqueIdentifierObject.id
            row['code'] = uniqueIdentifierObject.code
            row['locality'] = uniqueIdentifierObject.locality
            row['state'] = uniqueIdentifierObject.state
            row['deliveryOffice'] = uniqueIdentifierObject.deliveryOffice
        else:
            counter = 0
        if not counter == 0:
            resultSet.append(row)
    self.context_append['params'] = params
    return resultSet


