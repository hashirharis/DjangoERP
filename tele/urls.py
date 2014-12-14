from django.conf.urls import patterns, url

from tele import views

urlpatterns = patterns('',
    url(r'^home/$', views.HomeView.as_view(), name="home"),
    #url(r'^$', views.index, name='home')

    #local contact CRUD
    url(r'^local-contact-lookup/$', views.LocalContactLookupView.as_view(), name='localContactLookup'),
    url(r'^create-local-contact/$', views.LocalContactCreateView.as_view(), name='createLocalContact'),
    url(r'^view-contact/(?P<pk>\d+)$', views.LocalContactDetailView.as_view(), name='viewLocalContact'),
    url(r'^update-local-contact/(?P<pk>\d+)$', views.LocalContactUpdateView.as_view(), name='updateLocalContact'),
    url(r'^delete-local-contact/(?P<pk>\d+)/$', views.deleteLocalContact, name="deleteLocalContact"),

    #local brand rep CRUD
    url(r'^(?P<object_id>\d+)/create-local-brand-rep/$', views.LocalBrandRepCreateView.as_view(), name='createLocalBrandRep'),
    url(r'^update-local-brand-rep-/(?P<pk>\d+)$', views.LocalBrandRepUpdateView.as_view(), name='updateLocalBrandRep'),
    url(r'^delete-local-brand-rep/(?P<pk>\d+)/$', views.deleteLocalBrandRep, name="deleteLocalBrandRep"),

    #head office contact CRUD
    url(r'^head-office-contact-lookup/$', views.HeadOfficeContactLookupView.as_view(), name='headOfficeContactLookup'),
    url(r'^create-head-office-contact/$', views.HeadOfficeContactCreateView.as_view(), name='createHeadOfficeContact'),
    url(r'^update-head-office-contact/(?P<pk>\d+)$', views.HeadOfficeContactUpdateView.as_view(), name='updateHeadOfficeContact'),
    url(r'^delete-head-office-contact/(?P<pk>\d+)/$', views.deleteHeadOfficeContact, name="deleteHeadOfficeContact"),
    url(r'^view-head-office-contact/(?P<pk>\d+)$', views.HeadOfficeContactDetailView.as_view(), name='viewHeadOfficeContact'),

    #store CRUD
    url(r'^store-lookup/$', views.StoreLookupView.as_view(), name='storeLookup'),
    url(r'^view-store/(?P<pk>\d+)$', views.StoreDetailView.as_view(), name='viewStore'),

    #brand CRUD
    url(r'^brand-lookup/$', views.BrandLookupView.as_view(), name='brandLookup'),
    url(r'^view-brand/(?P<pk>\d+)$', views.BrandDetailView.as_view(), name='viewBrand'),

    #supplier CRUD
    #url(r'^supplier-lookup/$', views.SupplierLookupView.as_view(), name='supplierLookup'),
    #url(r'^view-supplier/(?P<pk>\d+)$', views.SupplierDetailView.as_view(), name='viewSupplier'),

)





