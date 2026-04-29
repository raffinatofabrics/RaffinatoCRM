from django.db import models
from django.contrib.auth.models import User

class SendLog(models.Model):
    """邮件发送日志"""
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, null=True, blank=True)
    recipient = models.EmailField('收件人')
    subject = models.CharField('主题', max_length=500)
    content = models.TextField('内容')
    status = models.CharField('状态', max_length=20, default='pending')
    error_message = models.TextField('错误信息', blank=True)
    sent_at = models.DateTimeField('发送时间', auto_now_add=True)
    
    # ========== 新增：邮件追踪字段 ==========
    opened_at = models.DateTimeField('首次打开时间', null=True, blank=True)
    clicked_at = models.DateTimeField('首次点击时间', null=True, blank=True)
    click_count = models.IntegerField('点击次数', default=0)
    last_click_at = models.DateTimeField('最后点击时间', null=True, blank=True)
    
    # ========== 新增：退信相关字段 ==========
    is_bounced = models.BooleanField('是否退信', default=False)
    bounce_type = models.CharField('退信类型', max_length=20, blank=True, null=True)
    bounce_reason = models.TextField('退信原因', blank=True)

    class Meta:
        db_table = 'send_logs'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.recipient} - {self.sent_at}"