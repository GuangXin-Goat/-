from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from apps.sales.models import Order, Opportunity, Lead
from apps.inventory.models import InventoryItem, StockMovement


class DashboardView(LoginRequiredMixin, TemplateView):
    """管理后台首页看板"""
    template_name = "analytics/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        monthly_orders = Order.objects.filter(
            created_at__gte=first_of_month,
            status__in=["confirmed", "in_production", "shipped", "installed", "completed"]
        )
        context["monthly_sales_amount"] = monthly_orders.aggregate(
            total=Sum("total_amount")
        )["total"] or 0
        context["monthly_order_count"] = monthly_orders.count()
        context["new_leads_count"] = Lead.objects.filter(
            created_at__gte=first_of_month
        ).count()
        context["pipeline_count"] = Opportunity.objects.exclude(
            stage__in=["closed_won", "closed_lost"]
        ).count()
        context["pipeline_value"] = Opportunity.objects.exclude(
            stage__in=["closed_won", "closed_lost"]
        ).aggregate(total=Sum("expected_amount"))["total"] or 0
        context["total_inventory_items"] = InventoryItem.objects.filter(is_active=True).count()
        context["low_stock_count"] = InventoryItem.objects.filter(
            quantity__lte=F("min_quantity")
        ).exclude(min_quantity=0).count()

        return context


class SalesAnalyticsView(LoginRequiredMixin, TemplateView):
    """销售数据分析页"""
    template_name = "analytics/sales_analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context["product_sales_ranking"] = []

        stages_data = []
        for stage_code, stage_name in Opportunity.STAGES:
            count = Opportunity.objects.filter(stage=stage_code).count()
            stages_data.append({"name": stage_name, "count": count})
        context["funnel_data"] = stages_data

        trends = []
        for i in range(5, -1, -1):
            month_start = (now.replace(day=1) - timedelta(days=30 * i)).replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            total = Order.objects.filter(
                created_at__gte=month_start,
                created_at__lte=month_end,
                status__in=["confirmed", "in_production", "shipped", "installed", "completed"]
            ).aggregate(total=Sum("total_amount"))["total"] or 0
            trends.append({
                "month": month_start.strftime("%Y-%m"),
                "amount": float(total),
            })
        context["monthly_trends"] = trends

        return context


class InventoryAnalyticsView(LoginRequiredMixin, TemplateView):
    """库存数据分析页"""
    template_name = "analytics/inventory_analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = InventoryItem.objects.filter(is_active=True)

        total_stock_value = sum(
            (item.quantity * item.cost_price) for item in items if item.cost_price
        )
        context["total_stock_value"] = total_stock_value
        context["total_items"] = items.count()
        context["low_stock_items"] = items.filter(
            quantity__lte=F("min_quantity")
        ).exclude(min_quantity=0).order_by("quantity")[:20]
        context["recent_movements"] = StockMovement.objects.all().order_by("-created_at")[:20]

        return context
