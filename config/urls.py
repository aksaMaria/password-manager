from django.contrib import admin
from django.urls import path
from vault import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("vault/", views.vault_view, name="vault"),
    path(
    "reveal/<int:password_id>/",
    views.reveal_password,
    name="reveal_password"
),
    path(
    "delete/<int:password_id>/",
    views.delete_password,
    name="delete_password"
),
path(
    "edit/<int:password_id>/",
    views.edit_password,
    name="edit_password"
),
path(
    "favorite/<int:password_id>/",
    views.toggle_favorite,
    name="toggle_favorite"
),
]