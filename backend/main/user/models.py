from django.db import models

# Create your models here.

class SysUser(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=100, verbose_name="密码")
    login_date = models.DateField(null=True, verbose_name="最后登录时间")
    status = models.IntegerField(null=True, verbose_name="帐号状态(0正常 1停用)")
    create_time = models.DateField(null=True, verbose_name="创建时间")
    update_time = models.DateField(null=True, verbose_name="更新时间")
    remark = models.CharField(max_length=500, null=True, verbose_name="备注")

    class Meta:
        db_table = "sys_user"


# 文件导入任务模型（通用）
class ImportTask(models.Model):
    task_id = models.CharField(max_length=255, primary_key=True, verbose_name="任务ID")
    file_name = models.CharField(max_length=255, verbose_name="文件名")
    file_path = models.CharField(max_length=500, verbose_name="文件路径")
    status = models.CharField(max_length=50, default='pending', verbose_name="状态")  # pending, processing, completed, failed
    total_rows = models.IntegerField(default=0, verbose_name="总行数")
    processed_rows = models.IntegerField(default=0, verbose_name="已处理行数")
    error_message = models.TextField(null=True, blank=True, verbose_name="错误信息")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "import_task"
