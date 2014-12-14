from django.conf.urls import patterns, url
from reports import views
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^home/$', views.MainDashboardView.as_view(), name="home"),
    url(r'^sales/(?P<report_type>\w+)/(?P<second_style>\w+)/$', views.ReportsView.as_view(), name="salesReportsView"),
    url(r'^export/(?P<report_type>\w+)/(?P<report_class>\w+)/', views.CreateExcel.as_view(), name='export'),
    url(r'^export-itemised/(?P<report_type>\w+)/(?P<second_style>\w+)/', views.CreateExcel.as_view(), name='export'),
    url(r'^goods-inward/(?P<report_type>\w+)/(?P<report_class>\w+)/$', views.ReportsView.as_view(), name="inwardReportsView"),
    url(r'^irp/(?P<report_type>\w+)/(?P<report_class>\w+)/$', views.ReportsView.as_view(), name="IRPReportsView"),
    url(r'^tax/(?P<report_type>\w+)/(?P<report_class>\w+)/$', views.ReportsView.as_view(), name="taxReportsView"),
    url(r'^customer/(?P<report_type>\w+)/(?P<report_class>\w+)/$', views.ReportsView.as_view(), name="customerReportsView"),
    url(r'^banking/(?P<report_type>\w+)/(?P<report_class>\w+)/$', views.ReportsView.as_view(), name="bankingReportsView"),
    url(r'^ledger/(?P<report_type>\w+)/(?P<report_class>\w+)/$', views.ReportsView.as_view(), name="ledgerReportsView"),
    url(r'^jsb/(?P<report_type>\w+)/(?P<report_class>\w+)/$', views.ReportsView.as_view(), name="jsbReportsView"),
    url(r'^warranties/(?P<report_type>\w+)/(?P<report_class>\w+)/$', views.ReportsView.as_view(), name="warrantyReportsView"),
)









