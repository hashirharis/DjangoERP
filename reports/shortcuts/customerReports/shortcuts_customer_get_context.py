from reports.shortcuts.shortcuts_global import *


def getCustomerContextData(self, context):
    # sortTypesList = [
    #     {'id': '0', 'name': 'Qty'},
    #     {'id': '1', 'name': 'Sell'},
    #     {'id': '2', 'name': 'Nett'},
    #     {'id': '3', 'name': 'GP'},
    #     {'id': '4', 'name': 'GP%'}
    # ]
    view_style = getReportType(self)
    if view_style == 'all':
        context['isAll'] = True
    elif view_style == 'email':
        context['isEmail'] = True
    elif view_style == 'birthdays':
        context['isBirthdays'] = True
    elif view_style == 'orders':
        context['isOrders'] = True
    elif view_style == 'attendance':
        context['isAttendance'] = True
    elif view_style == 'onlySales':
        context['isOnlySales'] = True
    elif view_style == 'new':
        context['isNew'] = True
    context['isCustomer'] = True
    # context['sortTypes'] = sortTypesList
    # context['brands'] = Brand.objects.all()
    # context['categories'] = ProductCategory.objects.filter(depth=1)
    return context



