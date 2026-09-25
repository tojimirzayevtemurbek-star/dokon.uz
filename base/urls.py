from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    path("profile/", views.profile_view, name="profile"),

    path("customers/", views.customer_list, name="customer_list"),
    path("customers/add/", views.customer_create, name="customer_create"),
    path("customers/<int:pk>/", views.customer_detail, name="customer_detail"),
    path("customers/<int:pk>/edit/", views.customer_edit, name="customer_edit"),
    path("customers/<int:pk>/delete/", views.customer_delete, name="customer_delete"),

    path("debts/", views.debt_list, name="debt_list"),
    path("debts/add/", views.debt_create, name="debt_create"),

    path("payments/", views.payment_list, name="payment_list"),
    path("payments/add/", views.payment_create, name="payment_create"),

    path("stores/", views.store_list, name="store_list"),
    path("stores/add/", views.store_create, name="store_create"),
    path("stores/<int:pk>/delete/", views.store_delete, name="store_delete"),
]
