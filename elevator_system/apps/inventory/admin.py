from django.contrib import admin
from .models import Supplier, Warehouse, InventoryItem, StockMovement, PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name", "contact_person", "phone", "rating", "is_active"]
    list_filter = ["is_active", "rating"]
    search_fields = ["name", "contact_person"]


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ["name", "location", "manager"]
    search_fields = ["name", "location"]


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ["sku", "name", "category", "warehouse", "quantity", "min_quantity",
                    "cost_price", "is_low_stock", "stock_value"]
    list_filter = ["category", "warehouse", "is_active"]
    search_fields = ["sku", "name"]
    actions = ["check_low_stock"]

    def check_low_stock(self, request, queryset):
        low = queryset.filter(quantity__lte=models.F("min_quantity")).exclude(min_quantity=0)
        count = low.count()
        self.message_user(request, f"发现 {count} 个低库存物料")
    check_low_stock.short_description = "检查低库存物料"


from django.db import models as models


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ["item", "movement_type", "quantity", "quantity_before", "quantity_after",
                    "reference_number", "operator", "created_at"]
    list_filter = ["movement_type", "created_at"]
    search_fields = ["item__name", "reference_number"]
    readonly_fields = ["quantity_before", "quantity_after", "created_at"]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ["po_number", "supplier", "status", "total_amount", "order_date", "created_by"]
    list_filter = ["status"]
    search_fields = ["po_number", "supplier__name"]
    inlines = [PurchaseOrderItemInline]
