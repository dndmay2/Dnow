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
    # url('^contact/$', views.contact, name='contact'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^user_details/$', views.user_details, name='user_details'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^emailTemplateCreate/$', views.emailTemplateCreate.as_view()),
    url(r'^emailTemplatesViewAll/$', views.emailTemplatesViewAll, name='emailTemplatesViewAll'),
    url(r'^emailTemplateView/(?P<template_id>[0-9]+)$', views.emailTemplateView, name='emailTemplateView'),
    url(r'^emailTemplateUpdate/(?P<pk>[0-9]+)$', views.emailTemplateUpdate.as_view(), name='emailTemplateUpdate'),
    url(r'^emailTemplateDelete/(?P<template_id>[0-9]+)$', views.emailTemplateDelete, name='emailTemplateDelete'),
    url(r'^sendEmails/$', views.sendEmails, name='sendEmails'),
]
