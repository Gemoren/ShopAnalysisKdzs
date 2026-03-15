from django.db import models
from django_db_views.db_view import DBView


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


# 每笔成功交易订单的毛利视图
class OrderGrossMarginView(DBView):
    id = models.IntegerField(db_column='id', primary_key=True)
    order_time = models.DateTimeField(verbose_name="下单时间")
    store_name = models.CharField(max_length=255, verbose_name="店铺名称")
    order_no = models.CharField(max_length=255, verbose_name="订单编号")
    platform_sku_id = models.CharField(max_length=255, verbose_name="平台skuID")
    alias = models.CharField(max_length=255, verbose_name="别名")
    gross_margin = models.DecimalField(verbose_name="毛利", max_digits=10, decimal_places=2)

    view_definition = """
        SELECT
            ROW_NUMBER() OVER () AS id,
            order_time,
            store_name,
            order_no,
            platform_sku_id,
            alias,
            ROUND(o.actual_received - s.cost_price * o.product_count, 2) AS gross_margin
        FROM
            sys_order o
            LEFT JOIN (
                SELECT DISTINCT spec_id, cost_price
                FROM sys_shop
            ) s ON o.platform_sku_id = s.spec_id
        WHERE
            o.platform = '拼多多'
            AND o.order_status = '交易成功'
    """

    class Meta:
        managed = False
        db_table = 'order_gross_margin_view'


# 每月成功交易订单的毛利视图
class OrderGrossMarginMonthView(DBView):
    id = models.IntegerField(db_column='id', primary_key=True)
    store_name = models.CharField(max_length=255, verbose_name="店铺名称")
    month = models.CharField(max_length=7, verbose_name="月份")
    month_gross_margin = models.DecimalField(verbose_name="月度毛利", max_digits=10, decimal_places=2)

    view_definition = """
        SELECT
            ROW_NUMBER() OVER () AS id,
            store_name,
            strftime('%Y-%m', order_time) AS month,
            ROUND(SUM(gross_margin), 2) AS month_gross_margin
        FROM
            order_gross_margin_view
        GROUP BY
            store_name,
            strftime('%Y-%m', order_time)
        ORDER BY
            month DESC,
            month_gross_margin DESC;
    """

    class Meta:
        managed = False
        db_table = 'order_gross_margin_month_view'
