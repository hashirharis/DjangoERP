from django.conf.urls import patterns, include, url
from bulletins import views
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    #collations
    url(r'^$', views.home, name="home"),
    url(r'^collations/$', views.collations, name="collations"),
    url(r'^collation/(?P<pk>\d+)/$', views.collation, name="collation"),
    url(r'^download/collation/(?P<pk>\d+)/$', views.downloadCollation, name="downloadCollation"),
    url(r'^createCollation/(?P<type>\w+)/$', views.createCollation, name="createCollation"),
    url(r'^saveCollation/(?P<type>\w+)/$', views.saveCollation, name="saveCollation"),
    url(r'^updateCollation/(?P<pk>\d+)/$', views.openCollation, name="updateCollation"),
    url(r'^collationOrder/(?P<pk>\d+)/$', views.collationOrder, name="collationOrder"),
    url(r'^collationOrderForCollation/(?P<collation_pk>\d+)/$', views.collationOrder, name="collationOrderForCollation"),
    #promotions
    url(r'^promotions/(?P<type>\w+)/$', views.promotions, name="promotions"),
    url(r'^createPromotion/(?P<bulletin_type>\w+)/$', views.PromotionCreateView.as_view(), name='createPromotion'),
    url(r'^updatePromotion/(?P<pk>\d+)/$', views.PromotionUpdateView.as_view(), name="updatePromotion"), #update
    #bulletins
    url(r'^bulletins/(?P<pk>\d+)/$', views.bulletin, name="bulletin"), #view, delete
    url(r'^updateBulletin/(?P<pk>\d+)/$', views.BulletinUpdateView.as_view(), name="updateBulletin"), #update
    url(r'^createBulletin/(?P<bulletin_type>\w+)/$', views.BulletinCreateView.as_view(), name="createBulletin"), #create
)