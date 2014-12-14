from core.models import *
from reports.models import *
from reports.shortcuts.shortcuts_global import *
from uploads.models import ProductExtras

def getJSBObjects(self, params):
    reportType = getReportType(self)
    resultSet = []
    appendCounter = -1
    startDate = getStartDate(params, self.request.session['startDateList'])
    endDate = getEndDate(params, self.request.session['endDateList'])
    # startDate = getStartDate(self, params)
    # endDate = getEndDate(self, params)
    # trueGP = setTrueGP(self, params)
    uniqueIdentifierObjectsForReport = Product.objects.all()
    if reportType == "jsb1":  # all products without writeups
        writeupsSubmitted = ProductExtras.objects.filter(writeupSubmitted=1)
        uniqueIdentifierObjectsForReport = uniqueIdentifierObjectsForReport.exclude(id__in=writeupsSubmitted)
    elif reportType == "jsb2":  # Website Product Information
        hasWebprice = ProductExtras.objects.filter(webPrice__gt=0)
        uniqueIdentifierObjectsForReport = hasWebprice
    else:
        uniqueIdentifierObjectsForReport = False
    for uniqueIdentifierObject in uniqueIdentifierObjectsForReport:
        row = {}
        if reportType == "jsb1":
            row['model'] = uniqueIdentifierObject.model
            row['status'] = uniqueIdentifierObject.status
        elif reportType == "jsb2":
            row['product'] = uniqueIdentifierObject.product.model
            row['brand'] = uniqueIdentifierObject.product.brand.brand
            row['category'] = uniqueIdentifierObject.product.category.name
            row['name'] = uniqueIdentifierObject.name
            row['webPrice'] = str(uniqueIdentifierObject.webPrice)
            row['shortDesc'] = uniqueIdentifierObject.shortDesc
            row['webDesc'] = uniqueIdentifierObject.webDesc
            row['specifications'] = uniqueIdentifierObject.specifications
            row['manWarranty'] = uniqueIdentifierObject.manWarranty
            row['catPrice'] = str(uniqueIdentifierObject.cataloguePrice)
            row['catStartDate'] = "tba"
            row['catEndDate'] = "tba"
        else:
            appendCounter = 0
        if not appendCounter == 0:
            resultSet.append(row)
    self.context_append['params'] = params
    return resultSet

