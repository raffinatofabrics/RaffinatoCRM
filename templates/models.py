from django.db import models

class EmailTemplate(models.Model):
    """邮件模板表"""
    
    name = models.CharField('模板名称', max_length=100, unique=True)
    subject = models.CharField('邮件主题', max_length=200, help_text='支持变量：{company_name}, {contact_person}, {country}, {my_name}, {my_company}')
    content = models.TextField('邮件正文', help_text='支持HTML，变量同主题')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'email_templates'
        verbose_name = '邮件模板'
        verbose_name_plural = '邮件模板'
    
    def __str__(self):
        return self.name