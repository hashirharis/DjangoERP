#!/usr/bin/env python
import datetime
import xlwt
from django.db.models.query import QuerySet, ValuesQuerySet
from django.http import HttpResponse


class ExcelResponseReport(HttpResponse):

    def __init__(self, storeName, report_type, report_class, data, output_name='excel_data', headers=None,
                 force_csv=False, encoding='utf8', title='BIRITE generated report'):
        self.headers = headers
        if not headers:
            raise AttributeError('headers must be specified')
        else:
            self.set_headers(headers, encoding)
            self.set_title(title, report_type, report_class, storeName)
            self.set_data(report_type, data, output_name, force_csv, encoding)

    def set_title(self, title, report_type, report_class, storeName):
        if report_class == 'tax':
            title = createTaxTitle(self, report_type, storeName)
        elif report_class == "customer":
            title = createCustTitle(self, report_type, storeName)
        elif report_class == "banking":
            title = createBankTitle(self, report_type, storeName)
        elif report_class == "ledger":
            title = createLedgerTitle(self, report_type, storeName)
        elif report_class == "jsb":
            title = createJSBTitle(self, report_type, storeName)
        elif report_class == "warranties":
            title = createWarrTitle(self, report_type, storeName)
        elif report_class == "irp":
            title = createIRPTitle(self, report_type, storeName)
        elif report_class == "inward":
            title = createInwardTitle(self, report_type, storeName)
        else:  # is Sales
            title = createSalesTitle(self, report_type, report_class, storeName)
        self.sheet.write_merge(0, 0, 0, len(self.headers)-1, title, xlwt.easyxf("align: horiz left, vert center;font:bold True"))
            #self.sheet.write(0,0, title,xlwt.easyxf("align: horiz center;font:bold True"))

    def set_headers(self, headers, encoding='utf8'):
        #sets table headers
        self.book = xlwt.Workbook(encoding=encoding)
        self.sheet = self.book.add_sheet('Sheet 1')
        self.styles = {'datetime': xlwt.easyxf(num_format_str='yyyy-mm-dd hh:mm:ss'),
                      'date': xlwt.easyxf(num_format_str='yyyy-mm-dd'),
                      'time': xlwt.easyxf(num_format_str='hh:mm:ss'),
                      'default': xlwt.Style.default_style}
        for colx, value in enumerate(headers):
                self.sheet.write(1, colx, value,xlwt.easyxf("pattern: pattern solid ; align: horiz center;font:bold True, colour white"))

    def set_data(self, report_type, data, output_name='excel_data', headers=None,
                 force_csv=False, encoding='utf8'):
        # Make sure we've got the right type of data to work with
        valid_data = False
        if isinstance(data, ValuesQuerySet):
            data = list(data)
        elif isinstance(data, QuerySet):
            data = list(data.values())
        if hasattr(data, '__getitem__'):
            if isinstance(data[0], dict):
                if headers is None:
                    headers = data[0].keys()
                data = [[row[col] for col in headers] for row in data]
                data.insert(0, headers)
            if hasattr(data[0], '__getitem__'):
                valid_data = True
        assert valid_data is True, "ExcelResponse requires a sequence of sequences"

        import StringIO
        output = StringIO.StringIO()
        # Excel has a limit on number of rows; if we have more than that, make a csv
        use_xls = False
        if len(data) <= 65536 and force_csv is not True:
            try:
                import xlwt
            except ImportError:
                # xlwt doesn't exist; fall back to csv
                pass
            else:
                use_xls = True
        if use_xls:
            for rowx, row in enumerate(data):
                for colx, value in enumerate(row):
                    # set the column centre/left alignment
                    if report_type == 'brandanalysis':
                        self.sheet.write(rowx+2, colx, value, xlwt.easyxf("align: horiz center;font:bold False"))
                    elif report_type == 'categoryanalysis':
                        self.sheet.write(rowx+2, colx, value, xlwt.easyxf("align: horiz center;font:bold False"))
                    elif report_type == 'itemised':
                        if colx == 1 or colx == 2 or colx == 3 or colx == 4 or colx == 12 or colx == 13:
                            self.sheet.write(rowx+2, colx, value, xlwt.easyxf("align: vert center;font:bold False"))
                        else:
                            self.sheet.write(rowx+2, colx, value, xlwt.easyxf("align: horiz center;font:bold False"))
                    else:
                        self.sheet.write(rowx+2, colx, value, xlwt.easyxf("align: horiz center;font:bold False"))
            # set column width
            if report_type == 'brandanalysis':
                self.sheet.col(0).width = 8256
            elif report_type == 'brandanalysisdetailed':
                self.sheet.col(0).width = 8256
                self.sheet.col(1).width = 8256
            elif report_type == 'categoryanalysis':
                self.sheet.col(0).width = 8256
            elif report_type == 'categoryanalysisdetailed':
                self.sheet.col(0).width = 8256
                self.sheet.col(1).width = 8256
            elif report_type == 'itemised':
                self.sheet.col(1).width = 4000
                self.sheet.col(2).width = 6000
                self.sheet.col(3).width = 4000
                self.sheet.col(4).width = 8000
                self.sheet.col(12).width = 6000
                self.sheet.col(13).width = 6000
                self.sheet.col(14).width = 6000
                self.sheet.col(15).width = 6000
            elif report_type == 'itemisedsummary':
                self.sheet.col(0).width = 6000
                self.sheet.col(1).width = 10000
                self.sheet.col(7).width = 6000
            # else:
            #     self.sheet.col(0).width = 6000
            #     self.sheet.col(1).width = 10000
            #     self.sheet.col(2).width = 10000
            #     self.sheet.col(3).width = 10000
            #     self.sheet.col(4).width = 10000
            #     self.sheet.col(5).width = 10000
            #     self.sheet.col(6).width = 10000
            #     self.sheet.col(7).width = 10000
            #     self.sheet.col(8).width = 10000
            #     self.sheet.col(9).width = 10000
            #     self.sheet.col(10).width = 10000
            #     self.sheet.col(11).width = 10000
            #     self.sheet.col(12).width = 10000
            #     self.sheet.col(13).width = 10000
            self.book.save(output)
            mimetype = 'application/vnd.ms-excel'
            file_ext = 'xls'
        else:
            for row in data:
                out_row = []
                for value in row:
                    if not isinstance(value, basestring):
                        value = unicode(value)
                    value = value.encode(encoding)
                    out_row.append(value.replace('"', '""'))
                output.write('"%s"\n' %
                             '","'.join(out_row))
            mimetype = 'text/csv'
            file_ext = 'csv'
        output.seek(0)
        super(ExcelResponseReport, self).__init__(content=output.getvalue(),
                                            mimetype=mimetype)
        self['Content-Disposition'] = 'attachment;filename="%s.%s"' % \
            (output_name.replace('"', '\"'), file_ext)


def createSalesTitle(self, report_type, report_class, storeName):
    if report_type == 'brandanalysis' or report_type == 'categoryanalysis' or report_type == 'brandanalysisdetailed' \
            or report_type == 'categoryanalysisdetailed':
        if report_class == '1' or report_class == '2':
            if storeName == 'Head Office':
                storeName = 'All Stores'
        else:
            pass
        if report_type == 'brandanalysisdetailed' or report_type == 'categoryanalysisdetailed':
            title = 'Reports - Detailed Sales Analysis of ', storeName
        else:
            title = 'Reports - Sales Analysis of ', storeName
    elif report_type == 'itemised':
        if report_class == '1':
            if storeName == 'Head Office':
                storeName = 'All Stores'
        else:
            pass
        title = 'Reports - Itemised Sales of ', storeName
    elif report_type == 'itemisedsummary':
        title = 'Reports - Itemised Summary by Category - Sales for ', storeName, ' - Note: GST excluded'
    elif report_type == 'monthly':
        title = 'Reports - Monthly Sales for ', storeName
    elif report_type == 'distribution':
        title = 'Reports - Sales Distribution (per customer\'s address postcode)'
    elif report_type == 'salesByCustomer':
        title = 'Reports - Sales by Customer for ', storeName
    elif report_type == 'warranties':
        title = 'Reports - Cust Care Plans by salesperson for ', storeName
    elif report_type == 'salesperson':
        title = 'Reports - Sales People at ', storeName
    else:
        title = 'Reports'
    return title


def createTaxTitle(self, report_type, storeName):
    if report_type == "dailysnapshot":
        title = 'Reports - Daily Snapshot for ', storeName
    elif report_type == "taxReport":
        title = 'Reports - Tax for ', storeName
    else:
        title = 'Reports - tax xxx by xxx - xxx for ', storeName
    return title


def createCustTitle(self, report_type, storeName):
    if report_type == "all":
        title = 'Reports - All Customers for ', storeName
    elif report_type == "email":
        title = 'Reports - Only customers with email for ', storeName
    elif report_type == "birthdays":
        title = 'Reports - Customer Birthdays for ', storeName
    elif report_type == "orders":
        title = 'Reports - Customer Orders for ', storeName
    elif report_type == "attendance":
        title = 'Reports - Customer Attendance for ', storeName
    elif report_type == "onlySales":
        title = 'Reports - Only customers with sales for ', storeName
    elif report_type == "new":
        title = 'Reports - New Customers for ', storeName
    else:
        title = 'Reports - customer xxx by xxx - xxx for ', storeName
    return title


def createBankTitle(self, report_type, storeName):
    if report_type == "bankingReport":
        title = 'Reports - Banking for ', storeName
    else:
        title = 'Reports - Banking for ', storeName
    return title


def createLedgerTitle(self, report_type, storeName):
    if report_type == "statements":
        title = 'Reports - Statements for ', storeName
    elif report_type == "aged":
        title = 'Reports - Aged account for ', storeName
    elif report_type == "selected":
        title = 'Reports - Selected account type for ', storeName
    else:
        title = 'Reports - ledger xxx by xxx - xxx for ', storeName
    return title


def createJSBTitle(self, report_type, storeName):
    if report_type == "jsb1":
        title = 'Reports - JSB - Products without writeup'
    elif report_type == "jsb2":
        title = 'Reports - JSB - Website Product Information'
    else:
        title = 'Reports - xxx by xxx - xxx for ', storeName
    return title


def createWarrTitle(self, report_type, storeName):
    if report_type == "warranty":
        title = 'Reports - Cust Care Plans for ', storeName
    else:
        title = 'Reports - Cust Care Plans for ', storeName
    return title


def createIRPTitle(self, report_type, storeName):
    if report_type == "storePurchases":
        title = 'Reports - Store Purchases'
    elif report_type == "extended":
        title = 'Reports - Extended Credit'
    elif report_type == "invoiceByDate":
        title = 'Reports - Invoice By Date'
    elif report_type == "storeListing":
        title = 'Reports - BiRite Store Listing'
    elif report_type == "b2b":
        title = 'Reports - B2B'
    elif report_type == "wholesale":
        title = 'Reports - Wholesale Price List'
    elif report_type == "rebates":
        title = 'Reports - Rebates'
    elif report_type == "IAS":
        title = 'Reports - IAS'
    else:    
        title = 'Reports - IRP'
    return title


def createInwardTitle(self, report_type, storeName):
    if report_type == "goodsInward":
        title = 'Reports - Goods Inward for ', storeName
    else:
        title = 'Reports - Goods Inward for ', storeName
    return title
