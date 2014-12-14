from reports.shortcuts.shortcuts_global import *


def getIRPContextData(self, context):
    sortTypesList = [
        {'id': '0', 'name': 'invTotalExGST'},
        {'id': '1', 'name': 'invoicve'},
        {'id': '2', 'name': 'createdDate'},
        {'id': '3', 'name': 'xxx'},
        {'id': '4', 'name': '%'}
    ]
    # context['sortTypes'] = sortTypesList
    # context['brands'] = Brand.objects.all()
    # context['categories'] = ProductCategory.objects.filter(depth=1)
    report_type = getReportType(self)
    if report_type == 'storePurchases':
        context['isStorePurchases'] = True
    elif report_type == 'extended':
        context['isExtended'] = True
    elif report_type == 'invoiceByDate':
        context['isInvoiceByDate'] = True
    elif report_type == 'storeListing':
        context['isStoreListing'] = True
    elif report_type == 'b2b':
        context['isB2B'] = True
    elif report_type == 'wholesale':
        context['isWholesale'] = True
    elif report_type == 'rebates':
        context['isRebates'] = True
    elif report_type == 'IAS':
        context['isIAS'] = True
    context['isIRP'] = True
    context['sortTypes'] = sortTypesList
    context['stores'] = Store.objects.all()
    return context