from django.urls import path
from . import views

app_name = "sales"

urlpatterns = [
    path("leads/", views.LeadListView.as_view(), name="lead_list"),
    path("opportunities/", views.OpportunityListView.as_view(), name="opportunity_list"),
    path("quotes/", views.QuoteListView.as_view(), name="quote_list"),
    path("orders/", views.OrderListView.as_view(), name="order_list"),
]
