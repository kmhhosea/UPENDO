from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("transactions/add/", views.add_transaction, name="add_transaction"),
    path("transactions/<int:transaction_id>/delete/", views.delete_transaction, name="delete_transaction"),
    path("categories/add/", views.add_category, name="add_category"),
]
