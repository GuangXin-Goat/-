from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.InventoryListView.as_view(), name="list"),
    path("movements/", views.StockMovementListView.as_view(), name="movements"),
    path("purchase-orders/", views.PurchaseOrderListView.as_view(), name="purchase_orders"),
    path("alerts/", views.LowStockAlertView.as_view(), name="alerts"),
]
