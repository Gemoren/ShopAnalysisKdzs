from django.db import models

# Create your models here.
class SysShop(models.Model):
    spec_id = models.CharField(max_length=255, primary_key=True, verbose_name="规格ID")
    spec_name = models.CharField(max_length=255, verbose_name="规格名称")
    spec_alias = models.CharField(max_length=255, verbose_name="规格别名")
    spec_code = models.CharField(max_length=255, verbose_name="规格编码")
    cost_price = models.DecimalField(verbose_name="成本价", max_digits=10, decimal_places=2)
    market = models.CharField(max_length=255, verbose_name="市场")
    shop = models.CharField(max_length=255, verbose_name="档口")
    supplier = models.CharField(max_length=255, verbose_name="供应商")
    platform = models.CharField(max_length=255, verbose_name="平台")
    store = models.CharField(max_length=255, verbose_name="店铺")
    product_id = models.CharField(max_length=255, verbose_name="商品ID")
    product_name = models.CharField(max_length=255, verbose_name="商品")
    merchant_code = models.CharField(max_length=255, verbose_name="商家编码")
    abbreviation = models.CharField(max_length=255, verbose_name="简称")
    picture_url = models.CharField(max_length=255, verbose_name="图片URL")

    class Meta:
        db_table = "sys_shop"

