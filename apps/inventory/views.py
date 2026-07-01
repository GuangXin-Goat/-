from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, F
from .models import InventoryItem, StockMovement, PurchaseOrder


class InventoryListView(LoginRequiredMixin, ListView):
    """库存列表"""
    model = InventoryItem
    template_name = "inventory/inventory_list.html"
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):
        qs = InventoryItem.objects.filter(is_active=True)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q))
        return qs


class StockMovementListView(LoginRequiredMixin, ListView):
    """库存流水列表"""
    model = StockMovement
    template_name = "inventory/stock_movement_list.html"
    context_object_name = "movements"
    paginate_by = 30

    def get_queryset(self):
        qs = StockMovement.objects.all()
        mtype = self.request.GET.get("type")
        if mtype:
            qs = qs.filter(movement_type=mtype)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["movement_types"] = StockMovement.MOVEMENT_TYPES
        return context


class PurchaseOrderListView(LoginRequiredMixin, ListView):
    """采购订单列表"""
    model = PurchaseOrder
    template_name = "inventory/purchase_order_list.html"
    context_object_name = "orders"
    paginate_by = 20


class LowStockAlertView(LoginRequiredMixin, TemplateView):
    """低库存预警页面"""
    template_name = "inventory/low_stock_alerts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["low_stock_items"] = InventoryItem.objects.filter(
            quantity__lte=F("min_quantity")
        ).exclude(min_quantity=0).order_by("quantity")
        return context
