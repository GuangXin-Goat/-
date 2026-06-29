from django.contrib import admin
from .models import Category, Product, ProductImage, ProductAccessory


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAccessoryInline(admin.TabularInline):
    model = ProductAccessory
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "sort_order", "is_active", "product_count"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "产品数量"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "model_number", "category", "lift_type", "rated_capacity",
                    "base_price", "is_featured", "is_active", "created_at"]
    list_filter = ["category", "lift_type", "energy_rating", "is_featured", "is_active"]
    search_fields = ["name", "model_number", "summary"]
    prepopulated_fields = {"slug": ("model_number",)}
    inlines = [ProductImageInline, ProductAccessoryInline]
    fieldsets = [
        ("基本信息", {"fields": ["category", "name", "model_number", "slug", "lift_type",
                                "summary", "description", "thumbnail"]}),
        ("技术参数", {"fields": ["technical_specs", "rated_speed", "rated_capacity",
                                "max_floors", "max_passengers", "energy_rating"]}),
        ("销售设置", {"fields": ["base_price", "is_featured", "is_active", "sort_order"]}),
    ]
