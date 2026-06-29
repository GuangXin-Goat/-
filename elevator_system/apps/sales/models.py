from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class Customer(models.Model):
    """客户信息"""
    COMPANY_TYPES = [
        ("developer", "房地产开发公司"),
        ("property", "物业公司"),
        ("government", "政府/事业单位"),
        ("individual", "个人业主"),
        ("dealer", "经销商"),
        ("other", "其他"),
    ]

    company_name = models.CharField("公司名称", max_length=200)
    company_type = models.CharField("公司类型", max_length=30, choices=COMPANY_TYPES, default="other")
    contact_person = models.CharField("联系人", max_length=100)
    phone = models.CharField("联系电话", max_length=20)
    email = models.EmailField("邮箱", blank=True)
    address = models.TextField("地址", blank=True)
    website = models.URLField("网站", blank=True)
    tax_id = models.CharField("税号", max_length=50, blank=True)
    notes = models.TextField("备注", blank=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="customers", verbose_name="负责员工"
    )
    is_active = models.BooleanField("是否有效", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "客户"
        verbose_name_plural = "客户"
        ordering = ["-created_at"]

    def __str__(self):
        return self.company_name


class Lead(models.Model):
    """销售线索（来自官网询盘、展会等渠道）"""
    LEAD_SOURCES = [
        ("website", "官网询盘"),
        ("exhibition", "展会"),
        ("referral", "客户推荐"),
        ("cold_call", "电话陌拜"),
        ("social_media", "社交媒体"),
        ("advertisement", "广告投放"),
        ("other", "其他"),
    ]

    LEAD_STATUS = [
        ("new", "新线索"),
        ("contacted", "已联系"),
        ("qualified", "已确认"),
        ("converted", "已转化"),
        ("lost", "已丢失"),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="leads", verbose_name="关联客户"
    )
    contact_name = models.CharField("联系人姓名", max_length=100)
    phone = models.CharField("联系电话", max_length=20)
    email = models.EmailField("邮箱", blank=True)
    company = models.CharField("公司名称", max_length=200, blank=True)
    source = models.CharField("来源渠道", max_length=30, choices=LEAD_SOURCES, default="website")
    status = models.CharField("状态", max_length=30, choices=LEAD_STATUS, default="new")
    product_interest = models.ForeignKey(
        "products.Product", on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="感兴趣产品"
    )
    requirement = models.TextField("需求描述", blank=True)
    budget_range = models.CharField("预算范围", max_length=100, blank=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="leads", verbose_name="跟进人"
    )
    notes = models.TextField("跟进记录", blank=True)
    converted_at = models.DateTimeField("转化时间", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "销售线索"
        verbose_name_plural = "销售线索"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.contact_name} - {self.get_source_display()}"


class Opportunity(models.Model):
    """商机（销售管道阶段）"""
    STAGES = [
        ("prospecting", "初步接洽"),
        ("needs_analysis", "需求分析"),
        ("proposal", "方案报价"),
        ("negotiation", "商务谈判"),
        ("closed_won", "成交"),
        ("closed_lost", "丢单"),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="opportunities", verbose_name="客户"
    )
    title = models.CharField("商机名称", max_length=200)
    stage = models.CharField("阶段", max_length=30, choices=STAGES, default="prospecting")
    expected_amount = models.DecimalField("预计金额(元)", max_digits=12, decimal_places=2, null=True, blank=True)
    probability = models.IntegerField("成交概率(%)", default=10,
                                       help_text="0-100的整数")
    expected_close_date = models.DateField("预计成交日期", null=True, blank=True)
    competitor = models.CharField("主要竞争对手", max_length=200, blank=True)
    notes = models.TextField("备注", blank=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="opportunities", verbose_name="负责人"
    )
    closed_at = models.DateTimeField("成交/丢单时间", null=True, blank=True)
    lost_reason = models.TextField("丢单原因", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "商机"
        verbose_name_plural = "商机"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Quote(models.Model):
    """报价单"""
    STATUS_CHOICES = [
        ("draft", "草稿"),
        ("sent", "已发送"),
        ("accepted", "已确认"),
        ("rejected", "已拒绝"),
        ("expired", "已过期"),
    ]

    quote_number = models.CharField("报价单号", max_length=50, unique=True)
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="quotes", verbose_name="关联商机"
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="quotes", verbose_name="客户"
    )
    status = models.CharField("状态", max_length=30, choices=STATUS_CHOICES, default="draft")
    valid_until = models.DateField("有效期至")
    subtotal = models.DecimalField("产品合计(元)", max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField("折扣(元)", max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField("税额(元)", max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField("总金额(元)", max_digits=12, decimal_places=2, default=0)
    notes = models.TextField("备注", blank=True)
    terms = models.TextField("条款", blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="quotes", verbose_name="创建人"
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "报价单"
        verbose_name_plural = "报价单"
        ordering = ["-created_at"]

    def __str__(self):
        return self.quote_number


class QuoteItem(models.Model):
    """报价单明细"""
    quote = models.ForeignKey(
        Quote, on_delete=models.CASCADE, related_name="items", verbose_name="报价单"
    )
    product = models.ForeignKey(
        "products.Product", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="产品"
    )
    description = models.CharField("描述", max_length=500)
    quantity = models.IntegerField("数量", default=1)
    unit_price = models.DecimalField("单价(元)", max_digits=10, decimal_places=2)
    total_price = models.DecimalField("小计(元)", max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "报价明细"
        verbose_name_plural = "报价明细"

    def __str__(self):
        return f"{self.quote.quote_number} - {self.description}"


class Order(models.Model):
    """销售订单"""
    ORDER_STATUS = [
        ("pending", "待确认"),
        ("confirmed", "已确认"),
        ("in_production", "生产中"),
        ("shipped", "已发货"),
        ("installed", "已安装"),
        ("completed", "已完成"),
        ("cancelled", "已取消"),
    ]

    order_number = models.CharField("订单号", max_length=50, unique=True)
    quote = models.ForeignKey(
        Quote, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="orders", verbose_name="来源报价单"
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="orders", verbose_name="客户"
    )
    status = models.CharField("状态", max_length=30, choices=ORDER_STATUS, default="pending")
    order_date = models.DateField("下单日期", auto_now_add=True)
    expected_delivery = models.DateField("预计交付日期", null=True, blank=True)
    actual_delivery = models.DateField("实际交付日期", null=True, blank=True)
    subtotal = models.DecimalField("产品合计(元)", max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField("折扣(元)", max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField("税额(元)", max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField("订单总额(元)", max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField("已付款金额(元)", max_digits=12, decimal_places=2, default=0)
    notes = models.TextField("备注", blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="orders", verbose_name="创建人"
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "销售订单"
        verbose_name_plural = "销售订单"
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    """订单明细"""
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="订单"
    )
    product = models.ForeignKey(
        "products.Product", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="产品"
    )
    description = models.CharField("描述", max_length=500)
    quantity = models.IntegerField("数量", default=1)
    unit_price = models.DecimalField("单价(元)", max_digits=10, decimal_places=2)
    total_price = models.DecimalField("小计(元)", max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "订单明细"
        verbose_name_plural = "订单明细"

    def __str__(self):
        return f"{self.order.order_number} - {self.description}"


class Contract(models.Model):
    """合同管理"""
    CONTRACT_STATUS = [
        ("draft", "草稿"),
        ("active", "执行中"),
        ("completed", "已完结"),
        ("terminated", "已终止"),
    ]

    contract_number = models.CharField("合同编号", max_length=50, unique=True)
    order = models.OneToOneField(
        Order, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="contract", verbose_name="关联订单"
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="contracts", verbose_name="客户"
    )
    title = models.CharField("合同名称", max_length=200)
    status = models.CharField("状态", max_length=30, choices=CONTRACT_STATUS, default="draft")
    total_amount = models.DecimalField("合同金额(元)", max_digits=12, decimal_places=2)
    sign_date = models.DateField("签订日期", null=True, blank=True)
    start_date = models.DateField("生效日期", null=True, blank=True)
    end_date = models.DateField("终止日期", null=True, blank=True)
    file = models.FileField("合同文件", upload_to="contracts/", blank=True)
    terms = models.TextField("关键条款", blank=True)
    notes = models.TextField("备注", blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="contracts", verbose_name="创建人"
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "合同"
        verbose_name_plural = "合同"
        ordering = ["-created_at"]

    def __str__(self):
        return self.contract_number


class PaymentTerm(models.Model):
    """付款节点"""
    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name="payment_terms", verbose_name="合同"
    )
    milestone = models.CharField("付款节点", max_length=200)
    percentage = models.DecimalField("付款比例(%)", max_digits=5, decimal_places=2)
    amount = models.DecimalField("付款金额(元)", max_digits=12, decimal_places=2)
    due_date = models.DateField("到期日", null=True, blank=True)
    is_paid = models.BooleanField("是否已付", default=False)
    paid_date = models.DateField("付款日期", null=True, blank=True)
    remarks = models.CharField("备注", max_length=300, blank=True)

    class Meta:
        verbose_name = "付款节点"
        verbose_name_plural = "付款节点"
        ordering = ["due_date"]

    def __str__(self):
        return f"{self.contract.contract_number} - {self.milestone}"
