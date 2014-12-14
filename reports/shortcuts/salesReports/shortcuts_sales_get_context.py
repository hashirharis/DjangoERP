from reports.shortcuts.shortcuts_global import *
from core.models import *


class SalesViewFunctions(object):
    pass


def getSalesContextData(self, context):
    context['isSales'] = True
    report_type = self.kwargs.get('report_type') or self.request.GET.get('report_type') or self.request.POST.get('report_type') or ''
    if report_type == 'salesperson':
        return getSalesPersonData(context)
    elif report_type == 'brandanalysis' or report_type == 'brandanalysisdetailed' or report_type == 'drill':
        return getSalesAnalysisData(self, context)
    elif report_type == 'categoryanalysis' or report_type == 'categoryanalysisdetailed':
        return getSalesAnalysisData(self, context)
    elif report_type == "itemised":
        return getItemisedData(self, context)
    elif report_type == "itemisedsummary":
        return getItemisedSummarySalesData(context)
    elif report_type == "monthly":
        return getMonthlySalesData(context)
    elif report_type == "distribution":
        return getDistributionData(context)
    elif report_type == "salesByCustomer":
        return getSalesByCustomerData(context)
    elif report_type == "warranties":
        return getWarrantiesData(context)
    elif report_type == "itemisedsummary":
        return getItemisedSummarySalesData(context)
    else:
        return context


def getSalesPersonData(context):
    # sortTypesList = [
    #     {'id': '0', 'name': 'Qty'},
    #     {'id': '1', 'name': 'Sell'},
    #     {'id': '2', 'name': 'Nett'},
    #     {'id': '3', 'name': 'GP'},
    #     {'id': '4', 'name': 'GP%'}
    # ]
    context['isSalesPersonView'] = True
    # context['sortTypes'] = sortTypesList
    # context['brands'] = Brand.objects.all()
    # context['categories'] = ProductCategory.objects.filter(depth=1)
    return context


def getDistributionData(context):
    # sortTypesList = [
    #     {'id': '0', 'name': 'Qty'},
    #     {'id': '1', 'name': 'Sell'},
    #     {'id': '2', 'name': 'Nett'},
    #     {'id': '3', 'name': 'GP'},
    #     {'id': '4', 'name': 'GP%'}
    # ]
    context['isDistributionView'] = True
    # context['sortTypes'] = sortTypesList
    # context['brands'] = Brand.objects.all()
    # context['categories'] = ProductCategory.objects.filter(depth=1)
    return context


def getSalesByCustomerData(context):
    # sortTypesList = [
    #     {'id': '0', 'name': 'Qty'},
    #     {'id': '1', 'name': 'Sell'},
    #     {'id': '2', 'name': 'Nett'},
    #     {'id': '3', 'name': 'GP'},
    #     {'id': '4', 'name': 'GP%'}
    # ]
    context['isSalesByCustomerView'] = True
    # context['sortTypes'] = sortTypesList
    # context['brands'] = Brand.objects.all()
    # context['categories'] = ProductCategory.objects.filter(depth=1)
    return context


def getWarrantiesData(context):
    # sortTypesList = [
    #     {'id': '0', 'name': 'Qty'},
    #     {'id': '1', 'name': 'Sell'},
    #     {'id': '2', 'name': 'Nett'},
    #     {'id': '3', 'name': 'GP'},
    #     {'id': '4', 'name': 'GP%'}
    # ]
    context['isWarrantiesView'] = True
    # context['sortTypes'] = sortTypesList
    # context['brands'] = Brand.objects.all()
    # context['categories'] = ProductCategory.objects.filter(depth=1)
    return context


def getMonthlySalesData(context):
    # sortTypesList = [
    #     {'id': '0', 'name': 'Qty'},
    #     {'id': '1', 'name': 'Sell'},
    #     {'id': '2', 'name': 'Nett'},
    #     {'id': '3', 'name': 'GP'},
    #     {'id': '4', 'name': 'GP%'}
    # ]
    context['isMonthlySalesView'] = True
    context['isPanelAtTopView'] = False
    # context['sortTypes'] = sortTypesList
    # context['brands'] = Brand.objects.all()
    # context['categories'] = ProductCategory.objects.filter(depth=1)
    return context




def getSalesAnalysisData(self, context):
    report_type = self.kwargs.get('report_type') or self.request.GET.get('report_type') or \
                    self.request.POST.get('report_type') or ''
    second_style = self.kwargs.get('second_style') or self.request.GET.get('second_style') or \
                    self.request.POST.get('second_style') or ''
    sortTypesList = [
        {'id': '0', 'name': 'Qty'},
        {'id': '1', 'name': 'Sell'},
        {'id': '2', 'name': 'Nett'},
        {'id': '3', 'name': 'GP'},
        {'id': '4', 'name': 'GP%'}
    ]
    if report_type == 'brandanalysis' or report_type == 'brandanalysisdetailed':
        context['isBrandsView'] = True
        sortTypesList.append({'id': '5', 'name': 'Brand'})
    elif report_type == 'categoryanalysis' or report_type == 'categoryanalysisdetailed':
        context['isBrandsView'] = False
        sortTypesList.append({'id': '5', 'name': 'Category'})
    elif report_type == 'drill':
        context['isDrillView'] = False
        sortTypesList.append({'id': '5', 'name': 'Category'})
    if report_type == 'brandanalysisdetailed':
        context['isbrandanalysisdetailedView'] = True
    elif report_type == 'categoryanalysisdetailed':
        context['iscategoryanalysisdetailedView'] = True
    if report_type == 'drill':
        brand = Brand.objects.filter(id=second_style)
        context['drillParentName'] = brand[0].brand
    else:
        if second_style == '1':
            context['isBrandsView_allStores'] = True
        elif second_style == '2':
            context['isCatView_allStores'] = True
    context['isSalesAnalysisView'] = True
    context['sortTypes'] = sortTypesList
    context['brands'] = Brand.objects.all()
    context['categories'] = ProductCategory.objects.filter(depth=1)
    return context


def getItemisedData(self, context):
    second_style = self.kwargs.get('second_style') or self.request.GET.get('second_style') or \
            self.request.POST.get('second_style') or ''
    context['isItemisedView'] = True
    if second_style == '1':
        context['isItemisedViewAllStores'] = True
    context['brands'] = Brand.objects.all()
    context['products'] = Product.objects.all()
    context['salesPeople'] = Staff.objects.filter(store=self.request.store)
    return context


def getItemisedSummarySalesData(context):
    context['isItemisedSummaryView'] = True
    return context


