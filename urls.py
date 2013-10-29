from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from xform_manager import views as xform_manager_views
OPT_GROUP_REGEX = "((?P<group_name>[^/]+)/)?"

from main import views as main_views

from uis_r_us import views as ui
from survey_photos.views import photo_redirect

urlpatterns = patterns('',
    url(r'^~(?P<reqpath>\S*)', ui.dashboard),
    url(r'^$', main_views.index),

    url(r"^%sformList$" % OPT_GROUP_REGEX, xform_manager_views.formList),
    url(r"^%ssubmission$" % OPT_GROUP_REGEX, xform_manager_views.submission),
    url(r'^xform_manager/', include('nmis.xform_manager.urls')),

    url(r'^description/', main_views.site_description),
    url(r'^facilities/', include('facilities.urls')),
    url(r'^facility_variables', ui.variable_data),
    url(r'^lgas/', include('nmis.nga_districts.urls')),
    url(r'^lgas/$', main_views.list_active_lgas),
    url(r'^modes/(?P<mode_data>\S*)$', ui.modes),
    url(r'^new_dashboard/(?P<lga_id>\S+)/$', ui.new_dashboard),
    url(r'^new_dashboard/(?P<lga_id>\S+)/(?P<sector_slug>\S+)$', ui.new_sector_overview),
    url(r'^nmis~/(?P<state_id>\S+)/(?P<lga_id>\S+)/(facilities|summary)/(?P<reqpath>\S*)$', ui.nmis_view),
    url(r'^nmis~/(?P<state_id>\S+)/(?P<lga_id>[^/]+)/?$', ui.nmis_view),
    url(r'^mustache/(?P<template_name>\w+)$', ui.mustache_template),
    url(r'^mustache_templates$', ui.all_mustache_templates),
    url(r'^test/(?P<module_id>\S+)$', ui.test_module),
    url(r'^test_maps$', ui.test_map),
    url(r'^user_management/', include('user_management.urls')),
    url(r'^survey_photos/(?P<size>\S+)/(?P<photo_id>\S+)$', photo_redirect),
    url(r'^gap_sheet/(?P<sector>\S+)/(?P<unique_slug>\S+).pdf$', ui.gap_sheet),

    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)
