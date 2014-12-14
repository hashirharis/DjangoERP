from django.conf.urls import patterns, url

from users import views

urlpatterns = patterns('',
    url(r'^settings/$', views.AdminHomeView.as_view(), name='adminSettings'),
    url(r'^sessionConnect/$', views.sessionConnect, name="sessionConnect"),
    url(r'^clearSession/$', views.clearSession, name="clearSession"),
    url(r'^settings/update/(?P<pk>\d+)$', views.StoreSettingsUpdateView.as_view(), name='changeStoreSaleSettings'),
    url(r'^privileges/update/(?P<pk>\d+)$', views.StorePrivelegesUpdateView.as_view(), name='changePrivelegeSettings'),
    url(r'^staff/update/(?P<pk>\d+)$', views.StaffUpdateView.as_view(), name='updateStaff'),
    url(r'^staff/changepassword/(?P<pk>\d+)$', views.StaffResetPasswordView.as_view(), name='updateStaffPassword'),
    url(r'^staff/list/$', views.StaffListView.as_view(), name='listStaff'),
    url(r'^staff/delete/(?P<pk>\d+)$', views.StaffDeleteView.as_view(), name='deleteStaff'),
    url(r'^staff/create$', views.StaffCreateView.as_view(), name='createStaff'),
    #stores
    url(r'^store/update-details/(?P<pk>\d+)$', views.StoreUpdateView.as_view(), name='changeStoreDetails'),
    url(r'^store/update-financials/(?P<pk>\d+)$', views.StoreFinancialsUpdateView.as_view(), name='updateFinancials'),
    url(r'^store/search/$', views.StoreSearchView.as_view(), name='searchStores'),
)
