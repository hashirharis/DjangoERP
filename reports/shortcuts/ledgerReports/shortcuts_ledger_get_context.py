from reports.shortcuts.shortcuts_global import *


def getLedgerContextData(self, context):
    # sortTypesList = [
    #     {'id': '0', 'name': 'Qty'},
    #     {'id': '1', 'name': 'Sell'},
    #     {'id': '2', 'name': 'Nett'},
    #     {'id': '3', 'name': 'GP'},
    #     {'id': '4', 'name': 'GP%'}
    # ]
    view_style = getReportType(self)
    if view_style == 'statements':
        context['isStatements'] = True
    elif view_style == 'aged':
        context['isAged'] = True
    elif view_style == 'selected':
        context['isSelected'] = True
    context['isLedger'] = True
    # context['sortTypes'] = sortTypesList
    # context['brands'] = Brand.objects.all()
    # context['categories'] = ProductCategory.objects.filter(depth=1)
    return context



