from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('vault/', include('vault.urls')),
    path('vulnerabilities/', include('vulnerabilities.urls')),
    path('api/', include('api.urls')),
    path('', include('accounts.urls')),
]
