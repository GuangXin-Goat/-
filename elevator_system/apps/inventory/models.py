from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class Supplier(models.Model):
    """供应商"""
    name = models.CharField("供应商名称", max_length=200)
    contact_person = models.CharField("联系人", max_length=100)
    phone = models.CharField("联系电话", max_length=20)
    email = models.EmailField("邮箱", blank=True)
    address = models.TextField("地址", blank=True)
    tax_id = models.CharField("税号", max_length=50, blank=True)
    bank_info = models.CharField("银行账户信息", max_length=300, blank=True)
    rating = models.IntegerField("评级", default=3, help_text="1-5星")
    is_active = models.BooleanField("是否启用", default=True)
    notes = models.TextField("备注", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "供应商"
        verbose_name_plural = "供应商"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    """仓库"""
    name = models.CharField("仓库名称", max_length=100)
    location = models.CharField("位置", max_length=200, blank=True)
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="warehouses", verbose_name="仓库管理员"
    )
    is_active = models.BooleanField("是否启用", default=True)
    notes = models.TextField("备注", blank=True)

    class Meta:
        verbose_name = "仓库"
        verbose_name_plural = "仓库"

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    """库存条目（电梯成品、配件、零部件）"""
    product = models.OneToOneField(
        "products.Product", on_delete=models.CASCADE,
        related_name="inventory", verbose_name="产品", null=True, blank=True
    )
    sku = models.CharField("SKU编码", max_length=100, unique=True)
    name = models.CharField("物料名称", max_length=200)
    category = models.CharField("物料分类", max_length=50, choices=[
        ("elevator", "电梯成品"),
        ("accessory", "配件"),
        ("part", "零部件"),
        ("consumable", "耗材"),
    ], default="elevator")
    unit = models.CharField("单位", max_length=20, default="台",
                            help_text="如：台、个、套、米")
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="items", verbose_name="所在仓库"
    )
    quantity = models.IntegerField("当前库存数量", default=0)
    min_quantity = models.IntegerField("最低库存量", default=0,
                                        help_text="低于此数量触发预警")
    cost_price = models.DecimalField("成本单价(元)", max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField("销售单价(元)", max_digits=10, decimal_places=2, default=0)
    location = models.CharField("库位", max_length=100, blank=True)
    notes = models.TextField("备注", blank=True)
    is_active = models.BooleanField("是否启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "库存条目"
        verbose_name_plural = "库存条目"
        ordering = ["sku"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_quantity if self.min_quantity > 0 else False

    @property
    def stock_value(self):
        return self.quantity * self.cost_price


class StockMovement(models.Model):
    """库存流水记录"""
    MOVEMENT_TYPES = [
        ("purchase_in", "采购入库"),
        ("sale_out", "销售出库"),
        ("return_in", "退货入库"),
        ("return_out", "退供应商"),
        ("transfer", "移库"),
        ("adjustment", "盘点调整"),
        ("scrap", "报废"),
    ]

    item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE,
        related_name="movements", verbose_name="物料"
    )
    movement_type = models.CharField("操作类型", max_length=30, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField("数量")
    quantity_before = models.IntegerField("操作前数量", default=0)
    quantity_after = models.IntegerField("操作后数量", default=0)
    reference_number = models.CharField("关联单号", max_length=100, blank=True,
                                         help_text="关联的采购单号/订单号等")
    notes = models.TextField("备注", blank=True)
    operator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="stock_operations", verbose_name="操作人"
    )
    created_at = models.DateTimeField("操作时间", auto_now_add=True)

    class Meta:
        verbose_name = "库存流水"
        verbose_name_plural = "库存流水"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.item.name} x{self.quantity}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.quantity_before = self.item.quantity
            if self.movement_type in ["purchase_in", "return_in", "adjustment"]:
                if self.movement_type == "adjustment":
                    self.item.quantity = self.quantity
                else:
                    self.item.quantity += self.quantity
            else:
                self.item.quantity -= self.quantity
            self.quantity_after = self.item.quantity
            self.item.save()
        super().save(*args, **kwargs)


class PurchaseOrder(models.Model):
    """采购订单"""
    STATUS_CHOICES = [
        ("draft", "草稿"),
        ("submitted", "已提交"),
        ("approved", "已审批"),
        ("ordered", "已下单"),
        ("partial", "部分到货"),
        ("received", "已入库"),
        ("cancelled", "已取消"),
    ]

    po_number = models.CharField("采购单号", max_length=50, unique=True)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="purchase_orders", verbose_name="供应商"
    )
    status = models.CharField("状态", max_length=30, choices=STATUS_CHOICES, default="draft")
    order_date = models.DateField("采购日期", auto_now_add=True)
    expected_date = models.DateField("预计到货日期", null=True, blank=True)
    received_date = models.DateField("实际到货日期", null=True, blank=True)
    subtotal = models.DecimalField("采购合计(元)", max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField("税额(元)", max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField("总金额(元)", max_digits=12, decimal_places=2, default=0)
    notes = models.TextField("备注", blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="purchase_orders", verbose_name="创建人"
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "采购订单"
        verbose_name_plural = "采购订单"
        ordering = ["-created_at"]

    def __str__(self):
        return self.po_number


class PurchaseOrderItem(models.Model):
    """采购订单明细"""
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="items", verbose_name="采购单"
    )
    item = models.ForeignKey(
        InventoryItem, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="物料"
    )
    description = models.CharField("描述", max_length=500)
    quantity = models.IntegerField("采购数量", default=1)
    received_quantity = models.IntegerField("已收货数量", default=0)
    unit_price = models.DecimalField("单价(元)", max_digits=10, decimal_places=2)
    total_price = models.DecimalField("小计(元)", max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "采购明细"
        verbose_name_plural = "采购明细"

    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.description}"
