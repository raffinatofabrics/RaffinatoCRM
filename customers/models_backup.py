from django.db import models
from django.core.validators import EmailValidator

class Customer(models.Model):
    """客户表"""
    
    LEVEL_CHOICES = [
        ('potential', '潜在客户'),
        ('intermediate', '中级客户'),
        ('advanced', '高级客户'),
        ('vip', 'VIP客户'),
    ]
    
    SOURCE_CHOICES = [
        ('manual', '手动导入'),
        ('excel_import', 'Excel导入'),
        ('search_import', '搜索导入'),
        ('supabase_migration', 'Supabase迁移'),
    ]
    
    BUSINESS_TYPE_CHOICES = [
        ('international', '外贸'),
        ('domestic', '内贸'),
    ]
    
    # 基本信息
    company_name = models.CharField('公司名称', max_length=200, db_index=True)
    contact_person = models.CharField('联系人', max_length=100, blank=True, null=True)
    email = models.CharField('邮箱', max_length=100, unique=True, validators=[EmailValidator()])
    phone = models.CharField('电话', max_length=50, blank=True, null=True)
    country = models.CharField('国家', max_length=50, blank=True, null=True, db_index=True)
    address = models.TextField('地址', blank=True, null=True)
    website = models.URLField('公司网站', blank=True, null=True)
    
    # 内贸专用字段
    province = models.CharField('省份', max_length=50, blank=True, null=True)
    city = models.CharField('城市', max_length=50, blank=True, null=True)
    
    # 业务类型
    business_type = models.CharField('业务类型', max_length=20, choices=BUSINESS_TYPE_CHOICES, default='international')
    
    # 客户评分
    score = models.IntegerField('客户评分', default=0, help_text='0-100分')
    
    # 邮箱验证
    email_verified = models.BooleanField('邮箱已验证', default=False)
    email_verify_status = models.CharField('邮箱验证状态', max_length=20, default='pending',
        choices=[('pending', '待验证'), ('valid', '有效'), ('invalid', '无效'), ('unknown', '未知')])
    email_verify_date = models.DateTimeField('邮箱验证时间', blank=True, null=True)
    
    # 分类与状态
    level = models.CharField('客户等级', max_length=20, choices=LEVEL_CHOICES, default='potential', db_index=True)
    source = models.CharField('来源', max_length=50, choices=SOURCE_CHOICES, default='manual')
    
    # 跟进信息
    last_contact_time = models.DateTimeField('上次联系时间', blank=True, null=True, db_index=True)
    is_dormant = models.BooleanField('是否沉睡', default=False)
    is_deleted = models.BooleanField('软删除', default=False, db_index=True)
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'customers'
        verbose_name = '客户'
        verbose_name_plural = '客户'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['level', 'last_contact_time']),
        ]
    
    def __str__(self):
        return f"{self.company_name} - {self.email}"


class SystemSetting(models.Model):
    """系统设置"""
    logo = models.ImageField('网站Logo', upload_to='logo/', blank=True, null=True)
    company_name = models.CharField('公司名称', max_length=100, default='Raffinato')
    subtitle = models.CharField('副标题', max_length=100, default='面料外贸 CRM')
    
    class Meta:
        db_table = 'system_settings'
        verbose_name = '系统设置'
        verbose_name_plural = '系统设置'


# ==================== 二期：自动搜索功能 ====================

class SearchTask(models.Model):
    """搜索任务表"""
    
    BUSINESS_TYPE_CHOICES = [
        ('international', '外贸'),
        ('domestic', '内贸'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '等待执行'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    FREQUENCY_CHOICES = [
        ('daily', '每天'),
        ('weekly', '每周'),
        ('monthly', '每月'),
    ]
    
    # 基本信息
    name = models.CharField('任务名称', max_length=100)
    business_type = models.CharField('业务类型', max_length=20, choices=BUSINESS_TYPE_CHOICES, default='international')
    
    # 搜索参数
    keywords = models.TextField('产品关键词', help_text='每行一个关键词')
    exclude_words = models.TextField('排除词', blank=True, help_text='每行一个排除词，可选')
    max_results = models.IntegerField('搜索数量', default=50, help_text='10-100条')
    
    # 外贸专用
    target_country = models.CharField('目标国家', max_length=100, blank=True, help_text='多个国家用逗号分隔')
    
    # 内贸专用
    target_province = models.CharField('目标省份', max_length=100, blank=True, help_text='多个省份用逗号分隔')
    target_city = models.CharField('目标城市', max_length=100, blank=True)
    
    # 高级搜索选项
    custom_site = models.CharField('自定义搜索范围', max_length=200, blank=True, help_text='如 site:linkedin.com')
    domain_suffix = models.CharField('限定域名后缀', max_length=50, blank=True, help_text='如 .it,.de，多个用逗号分隔')
    
    # 定时任务
    schedule_enabled = models.BooleanField('启用定时执行', default=False)
    schedule_frequency = models.CharField('执行频率', max_length=20, choices=FREQUENCY_CHOICES, blank=True)
    schedule_time = models.TimeField('执行时间', blank=True, null=True, help_text='如 02:00')
    
    # 状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    total_found = models.IntegerField('抓取总数', default=0)
    total_imported = models.IntegerField('已导入数量', default=0)
    
    # 时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    executed_at = models.DateTimeField('执行时间', blank=True, null=True)
    
    class Meta:
        db_table = 'search_tasks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_business_type_display()})"


class SearchResult(models.Model):
    """搜索结果表"""
    
    task = models.ForeignKey(SearchTask, on_delete=models.CASCADE, related_name='results')
    
    # 原始数据
    url = models.URLField('网站URL', max_length=500)
    title = models.CharField('网页标题', max_length=500, blank=True)
    
    # AI提取的结构化数据
    extracted_data = models.JSONField('AI提取数据', default=dict)
    
    # 解析后的字段（便于查询）
    company_name = models.CharField('公司名', max_length=200, blank=True)
    email = models.CharField('邮箱', max_length=200, blank=True)
    phone = models.CharField('电话', max_length=50, blank=True)
    contact_person = models.CharField('联系人', max_length=100, blank=True)
    industry = models.CharField('行业', max_length=200, blank=True)
    confidence = models.FloatField('置信度', default=0)
    
    # 状态
    is_duplicate = models.BooleanField('是否重复', default=False)
    is_imported = models.BooleanField('是否已导入客户库', default=False)
    imported_to = models.IntegerField('导入的客户ID', blank=True, null=True)
    is_ignored = models.BooleanField('是否忽略', default=False)
    
    # 时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'search_results'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company_name or self.url}"


# ==================== 二期：沟通记录 ====================

class CommunicationLog(models.Model):
    """客户沟通记录表（支持多渠道）"""
    
    CHANNEL_CHOICES = [
        ('wechat', '微信'),
        ('phone', '电话'),
        ('email', '邮件'),
        ('whatsapp', 'WhatsApp'),
        ('other', '其他'),
    ]
    
    DIRECTION_CHOICES = [
        ('outgoing', '发出'),
        ('incoming', '收到'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='communications')
    
    # 沟通信息
    channel = models.CharField('沟通渠道', max_length=20, choices=CHANNEL_CHOICES)
    direction = models.CharField('方向', max_length=20, choices=DIRECTION_CHOICES)
    content = models.TextField('沟通内容')
    
    # 附件
    attachments = models.JSONField('附件', default=list, blank=True)
    
    # 跟进
    follow_up_action = models.CharField('跟进动作', max_length=200, blank=True)
    
    # 时间
    communication_time = models.DateTimeField('沟通时间', db_index=True)
    
    # 记录人
    created_by = models.CharField('记录人', max_length=100)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'communication_logs'
        ordering = ['-communication_time']
    
    def __str__(self):
        return f"{self.customer.company_name} - {self.get_channel_display()} - {self.communication_time.strftime('%Y-%m-%d %H:%M')}"


# ==================== 三期：公司文档管理 ====================

class CompanyDocument(models.Model):
    """公司内部文档"""
    
    DOCUMENT_TYPES = [
        ('price_list', '价格表'),
        ('notice', '通知公文'),
        ('product_manual', '产品手册'),
        ('training', '培训资料'),
        ('contract', '合同模板'),
        ('other', '其他'),
    ]
    
    title = models.CharField('文档标题', max_length=200)
    doc_type = models.CharField('文档类型', max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField('文件', upload_to='company_docs/')
    version = models.CharField('版本号', max_length=20, blank=True)
    description = models.TextField('文档说明', blank=True)
    
    # 权限（哪些角色可以查看）
    view_roles = models.JSONField('可见角色', default=list, help_text='如 ["admin", "manager", "sales"]')
    
    # 元信息
    uploaded_by = models.CharField('上传人', max_length=100)
    download_count = models.IntegerField('下载次数', default=0)
    
    # 通知
    notify_users = models.BooleanField('是否通知用户', default=False)
    
    # 时间
    created_at = models.DateTimeField('上传时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'company_documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title