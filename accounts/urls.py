from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='login/', permanent=False)),
    path('register/',                        views.register_view,       name='register'),
    path('login/',                           views.login_view,          name='login'),
    path('logout/',                          views.logout_view,         name='logout'),
    path('profile/',                         views.profile_view,        name='profile'),
    path('dashboard/',                       views.dashboard_view,      name='dashboard'),
    # Admin user management
    path('manage/users/',                    views.admin_user_list,     name='admin_user_list'),
    path('manage/users/<int:pk>/toggle/',    views.admin_toggle_user,   name='admin_toggle_user'),
    path('manage/users/<int:pk>/delete/',    views.admin_delete_user,   name='admin_delete_user'),
]
