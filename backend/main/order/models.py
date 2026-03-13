from django.db import models


# Create your models here.
class SysOrder(models.Model):
    order_no = models.CharField(max_length=255, verbose_name="订单编号", primary_key=True)
    platform = models.CharField(max_length=255, verbose_name="平台")
    store_name = models.CharField(max_length=255, verbose_name="店铺名称")
    order_time = models.DateTimeField(verbose_name="下单时间")
    order_status = models.CharField(max_length=255, verbose_name="订单状态")
    courier_company = models.CharField(max_length=255, verbose_name="快递公司")
    tracking_no = models.CharField(max_length=255, verbose_name="运单号")
    product_total_price = models.DecimalField(verbose_name="商品总价", max_digits=10, decimal_places=2)
    product_count = models.IntegerField(verbose_name="宝贝数量")
    product_types = models.IntegerField(verbose_name="宝贝种类")
    actual_payment = models.DecimalField(verbose_name="实付金额", max_digits=10, decimal_places=2)
    actual_received = models.DecimalField(verbose_name="实收金额", max_digits=10, decimal_places=2)
    store_discount = models.DecimalField(verbose_name="店铺优惠金额", max_digits=10, decimal_places=2)
    platform_discount = models.DecimalField(verbose_name="平台优惠金额", max_digits=10, decimal_places=2)
    system_no = models.CharField(max_length=255, verbose_name="系统单号")
    platform_product_id = models.CharField(max_length=255, verbose_name="平台商品ID")
    platform_sku_id = models.CharField(max_length=255, verbose_name="平台skuID")
    spec_name = models.CharField(max_length=255, verbose_name="规格名称")
    alias = models.CharField(max_length=255, verbose_name="别名")

    class Meta:
        db_table = "sys_order"

