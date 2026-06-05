from django.urls import path
from . import views

app_name = 'vulnerabilities'

urlpatterns = [
    path('',                    views.report_list,   name='report_list'),
    path('add/',                views.report_add,    name='report_add'),
    path('<int:pk>/',           views.report_detail, name='report_detail'),
    path('<int:pk>/edit/',      views.report_edit,   name='report_edit'),
    path('<int:pk>/delete/',    views.report_delete, name='report_delete'),
]
