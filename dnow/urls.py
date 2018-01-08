from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /dnow/
    url(r'^$', views.index, name='index'),
    url(r'^spreadsheet/.*', views.spreadsheet, name='spreadsheet'),
    url(r'^spreadsheetLog/$', views.viewSpreadSheetLog, name='spreadsheetLog'),
    url(r'^email/$', views.email, name='email'),
    url(r'^all_hosthomes/$', views.all_hosthomes, name='all_hosthomes'),
    url(r'^all_drivers/$', views.all_drivers, name='all_drivers'),
    url(r'^all_cooks/$', views.all_cooks, name='all_cooks'),
    url(r'^all_leaders/$', views.all_leaders, name='all_leaders'),
    # ex: /polls/parent/5/
    url(r'^hosthomes/(?P<hosthome_id>[0-9]+)/$', views.hosthome, name='hosthome'),
    # ex: /dnow/parent/5/
    url(r'^parent/(?P<parent_id>[0-9]+)/$', views.parent, name='parent'),
    # ex: /dnow/student/5/
    url(r'^student/(?P<student_id>[0-9]+)/$', views.student, name='student'),
    url(r'^driver/(?P<driver_id>[0-9]+)/$', views.driver, name='driver'),
    url(r'^cook/(?P<cook_id>[0-9]+)/$', views.cook, name='cook'),
    url(r'^leader/(?P<leader_id>[0-9]+)/$', views.leader, name='leader'),
]
