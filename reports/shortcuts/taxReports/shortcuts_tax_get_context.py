from reports.shortcuts.shortcuts_global import *


def getTaxContextData(self, context):
    # sortTypesList = [
    #     {'id': '0', 'name': 'Qty'},
    #     {'id': '1', 'name': 'Sell'},
    #     {'id': '2', 'name': 'Nett'},
    #     {'id': '3', 'name': 'GP'},
    #     {'id': '4', 'name': 'GP%'}
    # ]
    report_type = getReportType(self)
    if report_type == 'dailysnapshot':
        context['isDailySnapshot'] = True
    elif report_type == 'taxReport':
        context['isTaxReport'] = True
    context['isTax'] = True
    # context['sortTypes'] = sortTypesList
    # context['brands'] = Brand.objects.all()
    # context['categories'] = ProductCategory.objects.filter(depth=1)
    return context



