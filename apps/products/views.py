from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from .models import Product, Category


class ProductListView(ListView):
    """产品列表页"""
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        # 分类筛选
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        # 电梯类型筛选
        lift_type = self.request.GET.get("lift_type")
        if lift_type:
            queryset = queryset.filter(lift_type=lift_type)
        # 搜索
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(model_number__icontains=q) | Q(summary__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True)
        context["lift_types"] = Product.LIFT_TYPES
        return context


class ProductDetailView(DetailView):
    """产品详情页"""
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_products"] = Product.objects.filter(
            category=self.object.category, is_active=True
        ).exclude(pk=self.object.pk)[:4]
        return context


class ProductCompareView(TemplateView):
    """产品对比页"""
    template_name = "products/product_compare.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_ids = self.request.GET.getlist("ids")
        products = Product.objects.filter(id__in=product_ids, is_active=True) if product_ids else []
        context["products"] = products
        context["compare_fields"] = [
            ("额定速度(m/s)", "rated_speed"),
            ("额定载重(kg)", "rated_capacity"),
            ("最大层站数", "max_floors"),
            ("最大乘员数(人)", "max_passengers"),
            ("能效等级", "energy_rating"),
            ("电梯类型", "lift_type"),
        ]
        return context
