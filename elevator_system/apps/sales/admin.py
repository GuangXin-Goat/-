from django.contrib import admin
from .models import (
    Customer, Lead, Opportunity, Quote, QuoteItem,
    Order, OrderItem, Contract, PaymentTerm
)


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class PaymentTermInline(admin.TabularInline):
    model = PaymentTerm
    extra = 1


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["company_name", "company_type", "contact_person", "phone", "assigned_to", "is_active"]
    list_filter = ["company_type", "is_active", "assigned_to"]
    search_fields = ["company_name", "contact_person", "phone"]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["contact_name", "phone", "company", "source", "status", "assigned_to", "created_at"]
    list_filter = ["source", "status", "assigned_to"]
    search_fields = ["contact_name", "phone", "company"]


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ["title", "customer", "stage", "expected_amount", "probability", "assigned_to", "created_at"]
    list_filter = ["stage", "assigned_to"]


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ["quote_number", "customer", "status", "total_amount", "valid_until", "created_by", "created_at"]
    list_filter = ["status"]
    search_fields = ["quote_number", "customer__company_name"]
    inlines = [QuoteItemInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "customer", "status", "total_amount", "paid_amount", "order_date", "created_by"]
    list_filter = ["status"]
    search_fields = ["order_number", "customer__company_name"]
    inlines = [OrderItemInline]
    fieldsets = [
        ("基本信息", {"fields": ["order_number", "quote", "customer", "status", "order_date"]}),
        ("交付信息", {"fields": ["expected_delivery", "actual_delivery"]}),
        ("财务信息", {"fields": ["subtotal", "discount", "tax_amount", "total_amount", "paid_amount"]}),
        ("其他", {"fields": ["notes", "created_by"]}),
    ]


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ["contract_number", "title", "customer", "status", "total_amount", "sign_date"]
    list_filter = ["status"]
    search_fields = ["contract_number", "title", "customer__company_name"]
    inlines = [PaymentTermInline]
