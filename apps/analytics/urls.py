from django.urls import path
from . import views

app_name = "analytics"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("sales/", views.SalesAnalyticsView.as_view(), name="sales"),
    path("inventory/", views.InventoryAnalyticsView.as_view(), name="inventory"),
]
