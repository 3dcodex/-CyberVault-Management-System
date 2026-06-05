from django.urls import path
from . import views

urlpatterns = [
    path('login/',       views.login),
    path('logout/',      views.logout),
    path('vault/save/',  views.save_credential),
]
