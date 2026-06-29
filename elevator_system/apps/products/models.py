from django.db import models
from django.urls import reverse


class Category(models.Model):
    """电梯分类：乘客电梯、载货电梯、医用电梯、自动扶梯等"""
    name = models.CharField("分类名称", max_length=100)
    slug = models.SlugField("URL别名", max_length=120, unique=True)
    description = models.TextField("分类描述", blank=True)
    image = models.ImageField("分类图片", upload_to="categories/", blank=True)
    sort_order = models.IntegerField("排序", default=0)
    is_active = models.BooleanField("是否启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "产品分类"
        verbose_name_plural = "产品分类"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """电梯型号主表"""
    LIFT_TYPES = [
        ("passenger", "乘客电梯"),
        ("freight", "载货电梯"),
        ("panoramic", "观光电梯"),
        ("hospital", "医用电梯"),
        ("escalator", "自动扶梯"),
        ("moving_walk", "自动人行道"),
        ("home", "家用电梯"),
        ("car", "汽车电梯"),
    ]

    ENERGY_RATINGS = [
        ("A++", "A++"),
        ("A+", "A+"),
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
    ]

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products", verbose_name="分类"
    )
    name = models.CharField("产品名称", max_length=200)
    model_number = models.CharField("型号编号", max_length=100, unique=True)
    slug = models.SlugField("URL别名", max_length=200, unique=True)
    lift_type = models.CharField("电梯类型", max_length=30, choices=LIFT_TYPES)
    summary = models.CharField("简要卖点", max_length=300, blank=True,
                                help_text="首页/列表页展示的短描述")
    description = models.TextField("详细描述", blank=True)
    technical_specs = models.JSONField("技术参数", default=dict, blank=True,
                                        help_text="JSON格式存储详细技术参数")

    # 核心参数
    rated_speed = models.DecimalField("额定速度(m/s)", max_digits=5, decimal_places=2, null=True, blank=True)
    rated_capacity = models.IntegerField("额定载重(kg)", null=True, blank=True)
    max_floors = models.IntegerField("最大层站数", null=True, blank=True)
    max_passengers = models.IntegerField("最大乘员数(人)", null=True, blank=True)

    energy_rating = models.CharField("能效等级", max_length=3, choices=ENERGY_RATINGS, blank=True)
    is_featured = models.BooleanField("是否推荐", default=False)
    is_active = models.BooleanField("是否上架", default=True)
    base_price = models.DecimalField("基础价格(元)", max_digits=12, decimal_places=2, null=True, blank=True)
    thumbnail = models.ImageField("缩略图", upload_to="products/thumbs/", blank=True)

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "电梯产品"
        verbose_name_plural = "电梯产品"
        ordering = ["category", "sort_order", "name"]

    def __str__(self):
        return f"{self.name} ({self.model_number})"

    sort_order = models.IntegerField("排序", default=0)

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"slug": self.slug})


class ProductImage(models.Model):
    """产品图片集"""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name="产品"
    )
    image = models.ImageField("图片", upload_to="products/images/")
    caption = models.CharField("说明", max_length=200, blank=True)
    sort_order = models.IntegerField("排序", default=0)
    is_primary = models.BooleanField("是否主图", default=False)

    class Meta:
        verbose_name = "产品图片"
        verbose_name_plural = "产品图片"
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.product.name} - {self.caption or '图片'}"


class ProductAccessory(models.Model):
    """可选配件/配置"""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="accessories", verbose_name="产品"
    )
    name = models.CharField("配件名称", max_length=200)
    description = models.TextField("配件描述", blank=True)
    price = models.DecimalField("价格(元)", max_digits=10, decimal_places=2, default=0)
    is_optional = models.BooleanField("是否可选", default=True)
    sort_order = models.IntegerField("排序", default=0)

    class Meta:
        verbose_name = "可选配件"
        verbose_name_plural = "可选配件"
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.name} ({self.product.name})"
