from django.contrib import admin
from django.urls import path
from vault import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("save/", views.save_password, name="save_password"),
    path("vault/", views.vault_list, name="vault_list"),
path("vault/<int:pk>/reveal/", views.reveal_password, name="reveal_password"),
path("vault/<int:pk>/edit/", views.edit_password, name="edit_password"),
path("vault/<int:pk>/favorite/", views.toggle_favorite, name="toggle_favorite"),
path("vault/<int:pk>/delete/", views.delete_password, name="delete_password"),
]
