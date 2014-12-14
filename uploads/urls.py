from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    #  views
    url(r'^home/$', views.HomeView.as_view(), name='home'),
    url(r'^home/(?P<pk>\d+)', views.HomeView.as_view(), name='home'),
    #  post request function
    url(r'^WriteOrDeleteUploadIfInvalid/(?P<pk>\d+)/(?P<passedValidation>\w+)/$', views.WriteOrDeleteUploadIfInvalid, name='WriteOrDeleteUploadIfInvalid'),
    #  session functions
    url(r'^add_to_session/$', 'uploads.views.addToSession', name='add_to_session'),
    url(r'^add_to_session/(?P<model>\w+)$', 'uploads.views.addToSession', name='add_to_session'),
    url(r'^add_to_session/(?P<model>\w+)/(?P<pk>\d+)$', 'uploads.views.addToSession', name='add_to_session'),
    url(r'^remove_from_session/$', 'uploads.views.removeFromSession', name='remove_from_session'),
    url(r'^remove_from_session/(?P<model>\w+)$', 'uploads.views.removeFromSession', name='remove_from_session'),
    url(r'^remove_from_session/(?P<model>\w+)/(?P<pk>\d+)$', 'uploads.views.removeFromSession', name='remove_from_session'),
)



