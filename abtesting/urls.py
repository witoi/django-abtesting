from django.conf.urls import patterns, url

urlpatterns = patterns(
    'abtesting.views',
    url(r'^confirm_human/$', 'confirm_human', name="abtesting-confirm-human"),

    url(r'^admin/$', 'experiments_overview', name="abtesting-admin"),
    url(r'^admin/exp/(?P<expname>[^/]+)/$', 'experiment_detail', name="abtesting-experiment-detail"),

    url(r'^admin/exp/(?P<expname>[^/]+)/(?P<report_id>\d+)/$', 'experiment_report', name="abtesting-experiment-report"),

    url(r'^admin/exp/(?P<expname>[^/]+)/(?P<variant>[^/]+)/(?P<goal>[^/]+)/$', 'experiment_log', name="abtesting-experiment-log"),
)
