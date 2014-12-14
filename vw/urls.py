from django.conf.urls import patterns, url
from vw.views import *

urlpatterns = patterns('',
    url(r'^home/$', VWHomeView, name='home'),
    url(r'^move-stock-without-invoice/$', VWManualStockMovementCreateView.as_view(), name='moveVWStockNoInvoice'),
    url(r'^invoicing/open/(?P<invoice_id>\d+)/$', openVWInvoice, name='openHOInvoice'),
    url(r'^release-stock-with-invoice/$', newVWInvoiceOUTView, name='newVWInvoiceOUT'),
    url(r'^delete-invoice/(?P<pk>\d+)/$', deleteVWInvoice, name='deleteVWInvoice'),
    url(r'^add-stock-with-invoice/$', newVWInvoiceINView, name='newVWInvoiceIN'),
    url(r'^save-invoice/(?P<type>\w+)/$', saveVWInvoice, name='saveVWInvoice'),
)
