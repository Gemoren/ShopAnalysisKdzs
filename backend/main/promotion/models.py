from django.db import models
from django_db_views.db_view import DBView

# Create your models here.
class SysPromotion(models.Model):
    date = models.DateField(verbose_name="日期")
    product_id = models.CharField(max_length=255, verbose_name="商品ID")
    product_name = models.CharField(max_length=255, verbose_name="商品名称", blank=True, null=True)
    promotion_scene = models.CharField(max_length=255, verbose_name="推广场景", blank=True, null=True)
    promotion_name = models.CharField(max_length=255, verbose_name="推广名称", blank=True, null=True)
    bidding_method = models.CharField(max_length=255, verbose_name="出价方式", blank=True, null=True)
    total_cost = models.DecimalField(verbose_name="总花费(元)", max_digits=10, decimal_places=2, blank=True, null=True)
    transaction_cost = models.DecimalField(verbose_name="成交花费(元)", max_digits=10, decimal_places=2, blank=True,
                                           null=True)
    transaction_amount = models.DecimalField(verbose_name="交易额(元)", max_digits=10, decimal_places=2, blank=True,
                                             null=True)
    actual_roi = models.DecimalField(verbose_name="实际投产比", max_digits=10, decimal_places=2, blank=True, null=True)
    net_actual_roi = models.DecimalField(verbose_name="净实际投产比", max_digits=10, decimal_places=2, blank=True,
                                         null=True)
    net_transaction_amount = models.DecimalField(verbose_name="净交易额(元)", max_digits=10, decimal_places=2,
                                                 blank=True, null=True)
    net_transaction_count = models.IntegerField(verbose_name="净成交笔数", blank=True, null=True)
    cost_per_net_transaction = models.DecimalField(verbose_name="每笔净成交花费(元)", max_digits=10, decimal_places=2,
                                                   blank=True, null=True)
    net_transaction_ratio = models.DecimalField(verbose_name="净交易额占比", max_digits=10, decimal_places=2,
                                                blank=True, null=True)
    transaction_count = models.IntegerField(verbose_name="成交笔数", blank=True, null=True)
    cost_per_transaction = models.DecimalField(verbose_name="每笔成交花费(元)", max_digits=10, decimal_places=2,
                                               blank=True, null=True)
    amount_per_transaction = models.DecimalField(verbose_name="每笔成交金额(元)", max_digits=10, decimal_places=2,
                                                 blank=True, null=True)
    direct_transaction_amount = models.DecimalField(verbose_name="直接交易额(元)", max_digits=10, decimal_places=2,
                                                    blank=True, null=True)
    indirect_transaction_amount = models.DecimalField(verbose_name="间接交易额(元)", max_digits=10, decimal_places=2,
                                                      blank=True, null=True)
    direct_transaction_count = models.IntegerField(verbose_name="直接成交笔数", blank=True, null=True)
    indirect_transaction_count = models.IntegerField(verbose_name="间接成交笔数", blank=True, null=True)
    direct_amount_per_transaction = models.DecimalField(verbose_name="每笔直接成交金额(元)", max_digits=10,
                                                        decimal_places=2, blank=True, null=True)
    indirect_amount_per_transaction = models.DecimalField(verbose_name="每笔间接成交金额(元)", max_digits=10,
                                                          decimal_places=2, blank=True, null=True)
    site_promotion_ratio = models.DecimalField(verbose_name="全站推广费比", max_digits=10, decimal_places=2, blank=True,
                                               null=True)
    exposure_count = models.IntegerField(verbose_name="曝光量", blank=True, null=True)
    click_count = models.IntegerField(verbose_name="点击量", blank=True, null=True)
    inquiry_cost = models.DecimalField(verbose_name="询单花费(元)", max_digits=10, decimal_places=2, blank=True,
                                       null=True)
    inquiry_count = models.IntegerField(verbose_name="询单量", blank=True, null=True)
    avg_inquiry_cost = models.DecimalField(verbose_name="平均询单成本(元)", max_digits=10, decimal_places=2, blank=True,
                                           null=True)
    favorite_cost = models.DecimalField(verbose_name="收藏花费(元)", max_digits=10, decimal_places=2, blank=True,
                                        null=True)
    favorite_count = models.IntegerField(verbose_name="收藏量", blank=True, null=True)
    avg_favorite_cost = models.DecimalField(verbose_name="平均收藏成本(元)", max_digits=10, decimal_places=2,
                                            blank=True, null=True)
    follow_cost = models.DecimalField(verbose_name="关注花费(元)", max_digits=10, decimal_places=2, blank=True,
                                      null=True)
    follow_count = models.IntegerField(verbose_name="关注量", blank=True, null=True)
    avg_follow_cost = models.DecimalField(verbose_name="平均关注成本(元)", max_digits=10, decimal_places=2, blank=True,
                                          null=True)

    class Meta:
        db_table = "sys_promotion"
        constraints = [
            models.UniqueConstraint(fields=['date', 'product_id'], name='unique_date_product')
        ]


# 推广数据汇总视图
class PromotionSummaryMonthView(DBView):
    id = models.IntegerField(db_column='id', primary_key=True)
    store = models.CharField(max_length=255, verbose_name="店铺名", blank=True, null=True)
    month = models.CharField(max_length=7, verbose_name="月份", blank=True, null=True)
    total_cost = models.DecimalField(verbose_name="总花费(元)", max_digits=10, decimal_places=2, blank=True, null=True)

    view_definition = """
        SELECT
        ROW_NUMBER() OVER () AS id,
        shop_info.store AS store,
        strftime('%Y-%m', p.date) AS month,
        ROUND(SUM(p.total_cost), 2) AS total_cost
    FROM
        sys_promotion p
        LEFT JOIN (
            SELECT DISTINCT product_id, store
            FROM sys_shop
        ) shop_info ON p.product_id = shop_info.product_id
    GROUP BY
        shop_info.store,
        strftime('%Y-%m', p.date)
    ORDER BY
        month DESC,
        total_cost DESC;
    """

    class Meta:
        db_table = "promotion_summary_month_view"
        managed = False

