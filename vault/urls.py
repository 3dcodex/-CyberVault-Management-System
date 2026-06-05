from django.urls import path
from . import views

app_name = 'vault'

urlpatterns = [
    path('',              views.credential_list,   name='credential_list'),
    path('add/',          views.credential_add,    name='credential_add'),
    path('<int:pk>/edit/',   views.credential_edit,   name='credential_edit'),
    path('<int:pk>/delete/', views.credential_delete, name='credential_delete'),
]
