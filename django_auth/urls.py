from django.urls import path

from django_auth.views import (
    AdminUserDetailView,
    AdminUserListView,
    LoginView,
    LogoutView,
    MeUpdateView,
    RegisterView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("me/", MeUpdateView.as_view()),
    path("admin/users/", AdminUserListView.as_view()),
    path("admin/users/<int:user_id>/", AdminUserDetailView.as_view()),
]
