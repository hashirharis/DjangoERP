from django.views.generic import TemplateView
from excel_reports import ExcelResponseReport
from brutils.generic.views import *
from reports.shortcuts.salesReports.shortcuts_sales import *
from reports.shortcuts.bankingReports.shortcuts_banking import *
from reports.shortcuts.customerReports.shortcuts_customer import *
from reports.shortcuts.inwardReports.shortcuts_inward import *
from reports.shortcuts.IRPReports.shortcuts_irp import *
from reports.shortcuts.ledgerReports.shortcuts_ledger import *
from reports.shortcuts.JSBReports.shortcuts_jsb import *
from reports.shortcuts.taxReports.shortcuts_tax import *
from reports.shortcuts.warrantyReports.shortcuts_warranties import *
from reports.shortcuts.salesReports.shortcuts_sales_get_context import *
from reports.shortcuts.bankingReports.shortcuts_banking_get_context import *
from reports.shortcuts.customerReports.shortcuts_customer_get_context import *
from reports.shortcuts.inwardReports.shortcuts_inward_get_context import *
from reports.shortcuts.IRPReports.shortcuts_irp_get_context import *
from reports.shortcuts.ledgerReports.shortcuts_ledger_get_context import *
from reports.shortcuts.JSBReports.shortcuts_jsb_get_context import *
from reports.shortcuts.taxReports.shortcuts_tax_get_context import *
from reports.shortcuts.warrantyReports.shortcuts_warranties_get_context import *


class MainDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "reports/dashboard.html"


class ReportsSearchMixin(object):

    def getReportObjects(self, report_class):
        setStartEndDates(self)
        if report_class == 'tax':
            objects = getTaxObjects(self, params={})
        elif report_class == "banking":
            objects = getBankingObjects(self, params={})
        elif report_class == "ledger":
            objects = getLedgerObjects(self, params={})
        elif report_class == "jsb":
            objects = getJSBObjects(self, params={})
        elif report_class == "warranties":
            objects = getWarrantyObjects(self, params={})
        elif report_class == "customer":
            objects = getCustomerObjects(self, params={})
        elif report_class == "irp":
            objects = getIRPObjects(self, params={})
        elif report_class == "inward":
            objects = getInwardObjects(self, params={})
        else:
            objects = getSaleObjects(self, params={})
        return objects


class ReportsView(BRListView, ReportsSearchMixin):
    template_name = 'reports/report.html'
    context_object_name = 'objects'
    paginate_by = 100

    def get_queryset(self):
        return super(ReportsView, self).getReportObjects(getReportClass(self))

    def get_context_data(self, **kwargs):
        context = super(ReportsView, self).get_context_data(**kwargs)
        if getReportClass(self) == 'tax':
            return getTaxContextData(self, context)
        elif getReportClass(self) == "customer":
            return getCustomerContextData(self, context)
        elif getReportClass(self) == "banking":
            return getBankingContextData(self, context)
        elif getReportClass(self) == "ledger":
            return getLedgerContextData(self, context)
        elif getReportClass(self) == "jsb":
            return getJSBContextData(self, context)
        elif getReportClass(self) == "warranties":
            return getWarrantiesContextData(self, context)
        elif getReportClass(self) == "irp":
            return getIRPContextData(self, context)
        elif getReportClass(self) == "inward":
            return getInwardContextData(self, context)
        else:
            return getSalesContextData(self, context)


class CreateExcel(BRListView, ReportsSearchMixin):
    context_object_name = 'objects'

    def get_queryset(self):
        self.result = super(CreateExcel, self).getReportObjects(getReportClass(self))
        return self.result

    def render_to_response(self, context, **response_kwargs):
        return context

    def get_context_data(self, **kwargs):
        CSV_data = []
        headers = createCSVDataObject(self, CSV_data, getReportType(self), getReportClass(self))
        return ExcelResponseReport(self.request.store.name, getReportType(self), getReportClass(self), CSV_data, 'exported_report', headers=headers)



