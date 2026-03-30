from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    # Warden management (admin-only)
    path("wardens/", views.warden_list, name="warden_list"),
    path("wardens/add/", views.warden_add, name="warden_add"),
    path("wardens/<int:pk>/edit/", views.warden_edit, name="warden_edit"),
    path("wardens/<int:pk>/delete/", views.warden_delete, name="warden_delete"),
]
