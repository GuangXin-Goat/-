from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Lead, Opportunity, Quote, Order


class LeadListView(LoginRequiredMixin, ListView):
    """销售线索列表"""
    model = Lead
    template_name = "sales/lead_list.html"
    context_object_name = "leads"
    paginate_by = 20

    def get_queryset(self):
        qs = Lead.objects.all()
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Lead.LEAD_STATUS
        return context


class OpportunityListView(LoginRequiredMixin, ListView):
    """商机列表（销售管道）"""
    model = Opportunity
    template_name = "sales/opportunity_list.html"
    context_object_name = "opportunities"
    paginate_by = 20

    def get_queryset(self):
        qs = Opportunity.objects.all()
        stage = self.request.GET.get("stage")
        if stage:
            qs = qs.filter(stage=stage)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stage_choices"] = Opportunity.STAGES
        return context


class QuoteListView(LoginRequiredMixin, ListView):
    """报价单列表"""
    model = Quote
    template_name = "sales/quote_list.html"
    context_object_name = "quotes"
    paginate_by = 20


class OrderListView(LoginRequiredMixin, ListView):
    """销售订单列表"""
    model = Order
    template_name = "sales/order_list.html"
    context_object_name = "orders"
    paginate_by = 20
