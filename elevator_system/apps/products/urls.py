from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="list"),
    path("compare/", views.ProductCompareView.as_view(), name="compare"),
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="detail"),
]
