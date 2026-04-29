from django.db import models
from django.core.validators import EmailValidator
from django.conf import settings
from django.contrib.auth.models import User

class Customer(models.Model):
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
    company_name = models.CharField('公司名称', max_length=200, db_index=True)
    contact_person = models.CharField('联系人', max_length=100, blank=True, null=True)
    email = models.CharField('邮箱', max_length=100, unique=True, blank=True, null=True, validators=[EmailValidator()])
    phone = models.CharField('电话', max_length=50, blank=True, null=True)
    country = models.CharField('国家', max_length=50, blank=True, null=True, db_index=True)
    address = models.TextField('地址', blank=True, null=True)
    website = models.URLField('公司网站', blank=True, null=True)
    province = models.CharField('省份', max_length=50, blank=True, null=True)
    city = models.CharField('城市', max_length=50, blank=True, null=True)
    business_type = models.CharField('业务类型', max_length=20, choices=BUSINESS_TYPE_CHOICES, default='international')
    score = models.IntegerField('客户评分', default=0, help_text='0-100分')
    email_verified = models.BooleanField('邮箱已验证', default=False)
    email_verify_status = models.CharField('邮箱验证状态', max_length=20, default='pending',
        choices=[('pending', '待验证'), ('valid', '有效'), ('invalid', '无效'), ('unknown', '未知')])
    email_verify_date = models.DateTimeField('邮箱验证时间', blank=True, null=True)
    level = models.CharField('客户等级', max_length=20, choices=LEVEL_CHOICES, default='potential', db_index=True)
    source = models.CharField('来源', max_length=50, choices=SOURCE_CHOICES, default='manual')
    last_contact_time = models.DateTimeField('上次联系时间', blank=True, null=True, db_index=True)
    is_dormant = models.BooleanField('是否沉睡', default=False)
    is_deleted = models.BooleanField('软删除', default=False, db_index=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    notes = models.TextField('备注', blank=True, null=True)
    # 在 Customer 类中添加以下字段
    ai_score = models.FloatField(default=0, verbose_name='AI意向评分')
    ai_tags = models.TextField(blank=True, verbose_name='AI标签', help_text='JSON格式存储')
    last_ai_analysis = models.DateTimeField(blank=True, null=True, verbose_name='上次AI分析时间')
    # 团队协作字段（新增）
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属部门')
    assigned_sales = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_customers', verbose_name='负责销售')
    # ========== 新增：退信处理字段 ==========
    email_bounced = models.BooleanField('邮箱已退信', default=False)
    bounce_type = models.CharField('退信类型', max_length=20, blank=True, null=True)  # hard / soft
    bounce_reason = models.TextField('退信原因', blank=True)
    bounced_at = models.DateTimeField('退信时间', blank=True, null=True)
    email_invalid = models.BooleanField('邮箱无效', default=False)  # 硬退信后标记
    
    class Meta:
        db_table = 'customers'
        verbose_name = '客户'
        verbose_name_plural = '客户'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['level', 'last_contact_time']),
            models.Index(fields=['email_invalid']),  # 新增索引
        ]
    
    def __str__(self):
        return f"{self.company_name} - {self.email}"

class SystemSetting(models.Model):
    logo = models.ImageField('网站Logo', upload_to='logo/', blank=True, null=True)
    company_name = models.CharField('公司名称', max_length=100, default='Raffinato')
    subtitle = models.CharField('副标题', max_length=100, default='面料外贸 CRM')
    class Meta:
        db_table = 'system_settings'

class SearchTask(models.Model):
    BUSINESS_TYPE_CHOICES = [('international', '外贸'), ('domestic', '内贸')]
    STATUS_CHOICES = [('pending', '等待执行'), ('running', '执行中'), ('completed', '已完成'), ('failed', '失败')]
    FREQUENCY_CHOICES = [('daily', '每天'), ('weekly', '每周'), ('monthly', '每月')]
    name = models.CharField('任务名称', max_length=100)
    business_type = models.CharField('业务类型', max_length=20, choices=BUSINESS_TYPE_CHOICES, default='international')
    keywords = models.TextField('产品关键词', help_text='每行一个关键词')
    exclude_words = models.TextField('排除词', blank=True)
    max_results = models.IntegerField('搜索数量', default=50)
    target_country = models.CharField('目标国家', max_length=100, blank=True)
    target_province = models.CharField('目标省份', max_length=100, blank=True)
    target_city = models.CharField('目标城市', max_length=100, blank=True)
    custom_site = models.CharField('自定义搜索范围', max_length=200, blank=True)
    domain_suffix = models.CharField('限定域名后缀', max_length=50, blank=True)
    schedule_enabled = models.BooleanField('启用定时执行', default=False)
    schedule_frequency = models.CharField('执行频率', max_length=20, choices=FREQUENCY_CHOICES, blank=True)
    schedule_time = models.TimeField('执行时间', blank=True, null=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    total_found = models.IntegerField('抓取总数', default=0)
    total_imported = models.IntegerField('已导入数量', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    executed_at = models.DateTimeField('执行时间', blank=True, null=True)
    search_engine = models.CharField('搜索引擎', max_length=10, default='google', choices=[('google', 'Google'), ('baidu', '百度')])  # ← 新增这行    
    class Meta:
        db_table = 'search_tasks'
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.name} ({self.get_business_type_display()})"

class SearchResult(models.Model):
    task = models.ForeignKey(SearchTask, on_delete=models.CASCADE, related_name='results')
    url = models.URLField('网站URL', max_length=500)
    title = models.CharField('网页标题', max_length=500, blank=True)
    extracted_data = models.JSONField('AI提取数据', default=dict)
    company_name = models.CharField('公司名', max_length=200, blank=True)
    email = models.CharField('邮箱', max_length=200, blank=True)
    phone = models.CharField('电话', max_length=50, blank=True)
    contact_person = models.CharField('联系人', max_length=100, blank=True)
    industry = models.CharField('行业', max_length=200, blank=True)
    confidence = models.FloatField('置信度', default=0)
    is_duplicate = models.BooleanField('是否重复', default=False)
    is_imported = models.BooleanField('是否已导入客户库', default=False)
    imported_to = models.IntegerField('导入的客户ID', blank=True, null=True)
    is_ignored = models.BooleanField('是否忽略', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    class Meta:
        db_table = 'search_results'
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.company_name or self.url}"

class CommunicationLog(models.Model):
    CHANNEL_CHOICES = [('wechat', '微信'), ('phone', '电话'), ('email', '邮件'), ('whatsapp', 'WhatsApp'), ('other', '其他')]
    DIRECTION_CHOICES = [('outgoing', '发出'), ('incoming', '收到')]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='communications')
    channel = models.CharField('沟通渠道', max_length=20, choices=CHANNEL_CHOICES)
    direction = models.CharField('方向', max_length=20, choices=DIRECTION_CHOICES)
    content = models.TextField('沟通内容')
    attachments = models.JSONField('附件', default=list, blank=True)
    follow_up_action = models.CharField('跟进动作', max_length=200, blank=True)
    communication_time = models.DateTimeField('沟通时间', db_index=True)
    created_by = models.CharField('记录人', max_length=100)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    class Meta:
        db_table = 'communication_logs'
        ordering = ['-communication_time']
    def __str__(self):
        return f"{self.customer.company_name} - {self.get_channel_display()}"

class CompanyDocument(models.Model):
    DOCUMENT_TYPES = [('price_list', '价格表'), ('notice', '通知公文'), ('product_manual', '产品手册'), ('training', '培训资料'), ('contract', '合同模板'), ('other', '其他')]
    title = models.CharField('文档标题', max_length=200)
    doc_type = models.CharField('文档类型', max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField('文件', upload_to='company_docs/')
    version = models.CharField('版本号', max_length=20, blank=True)
    description = models.TextField('文档说明', blank=True)
    view_roles = models.JSONField('可见角色', default=list)
    uploaded_by = models.CharField('上传人', max_length=100)
    download_count = models.IntegerField('下载次数', default=0)
    notify_users = models.BooleanField('是否通知用户', default=False)
    created_at = models.DateTimeField('上传时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    class Meta:
        db_table = 'company_documents'
        ordering = ['-created_at']
    def __str__(self):
        return self.title

class CompanySeal(models.Model):
    """公司业务章管理"""
    
    DEPARTMENT_CHOICES = [
        ('international', '外贸部'),
        ('domestic', '内贸部'),
        ('both', '通用'),
    ]
    
    brand_name = models.CharField('品牌名称', max_length=100)
    seal_image = models.ImageField('业务章图片', upload_to='seals/')
    department = models.CharField('所属部门', max_length=20, choices=DEPARTMENT_CHOICES, default='both')
    is_active = models.BooleanField('是否启用', default=True)
    sort_order = models.IntegerField('排序', default=0)
    description = models.CharField('说明', max_length=200, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'company_seals'
        ordering = ['sort_order', '-created_at']
        verbose_name = '业务章'
        verbose_name_plural = '业务章'
    
    def __str__(self):
        return self.brand_name

# ==================== 三期：订单管理 ====================

class Order(models.Model):
    """订单表（内外贸通用）"""
    
    BUSINESS_TYPE_CHOICES = [
        ('international', '外贸'),
        ('domestic', '内贸'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('shipped', '已发货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    order_no = models.CharField('订单号', max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    business_type = models.CharField('业务类型', max_length=20, choices=BUSINESS_TYPE_CHOICES, default='international')
    order_date = models.DateField('订单日期')
    status = models.CharField('订单状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # 产品明细（JSON存储）
    items = models.JSONField('产品明细', default=list)
    # 格式：[{"product_name": "羊毛面料", "specification": "W001", "quantity": 500, "unit": "米", "unit_price": 22, "amount": 11000}]
    
    # 金额
    subtotal = models.DecimalField('小计', max_digits=12, decimal_places=2, default=0)
    
    # 费用明细（JSON存储）
    expenses = models.JSONField('费用明细', default=list)
    # 格式：[{"type": "运费", "amount": 1030, "note": "宁波→热那亚"}]
    
    total_cost = models.DecimalField('总成本', max_digits=12, decimal_places=2, default=0)
    profit = models.DecimalField('利润', max_digits=12, decimal_places=2, default=0)
    profit_margin = models.DecimalField('利润率', max_digits=5, decimal_places=2, default=0)
    
    # 销售人员
    sales_person = models.CharField('销售员', max_length=100, blank=True)
    
    # 备注
    notes = models.TextField('备注', blank=True)
    
    # 附件
    attachments = models.JSONField('附件', default=list, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    # 创建人（新增）
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_orders', verbose_name='创建人')

    class Meta:
        db_table = 'orders'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_no} - {self.customer.company_name}"

class UserEmailConfig(models.Model):
    """用户邮箱配置"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_configs')
    email = models.CharField('邮箱地址', max_length=200)
    smtp_host = models.CharField('SMTP服务器', max_length=200, default='smtp.exmail.qq.com')
    smtp_port = models.IntegerField('SMTP端口', default=587)
    smtp_password = models.CharField('邮箱密码', max_length=200)
    from_name = models.CharField('发件人名称', max_length=100)
    signature = models.TextField('邮件签名', blank=True)
    is_default = models.BooleanField('是否默认', default=False)
    daily_limit = models.IntegerField('每日上限', default=200)
    sent_today = models.IntegerField('今日已发送', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    last_reset_date = models.DateField('上次重置日期', auto_now_add=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'user_email_configs'
        verbose_name = '用户邮箱配置'
        verbose_name_plural = '用户邮箱配置'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.email}"

class OperationLog(models.Model):
    """操作日志"""
    
    ACTION_CHOICES = [
        ('create', '创建'),
        ('edit', '编辑'),
        ('delete', '删除'),
        ('batch_delete', '批量删除'),
        ('import', '导入'),
        ('export', '导出'),
        ('send_email', '发送邮件'),
        ('batch_send', '批量发送'),
        ('login', '登录'),
        ('logout', '退出'),
    ]
    
    MODULE_CHOICES = [
        ('customer', '客户管理'),
        ('order', '订单管理'),
        ('template', '邮件模板'),
        ('email', '邮件发送'),
        ('document', '公司文档'),
        ('search', '搜索任务'),
        ('user', '用户管理'),
        ('system', '系统'),
    ]
    
    user = models.CharField('操作用户', max_length=100)
    action = models.CharField('操作类型', max_length=20, choices=ACTION_CHOICES)
    module = models.CharField('操作模块', max_length=20, choices=MODULE_CHOICES)
    target = models.CharField('操作对象', max_length=200, blank=True)
    details = models.TextField('详情', blank=True)
    ip_address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)
    
    class Meta:
        db_table = 'operation_logs'
        ordering = ['-created_at']
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
    
    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

import random

def get_random_color():
    """随机生成颜色"""
    colors = ['#FF5722', '#4CAF50', '#2196F3', '#FFC107', '#9C27B0', '#E91E63', '#00BCD4', '#795548', '#F44336', '#3F51B5', '#009688', '#FF9800']
    return random.choice(colors)

class CustomerTag(models.Model):
    """客户标签"""
    name = models.CharField('标签名称', max_length=50, unique=True)
    color = models.CharField('标签颜色', max_length=20, default=get_random_color)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    class Meta:
        db_table = 'customer_tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CustomerTagRelation(models.Model):
    """客户-标签关联表"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tag_relations')
    tag = models.ForeignKey(CustomerTag, on_delete=models.CASCADE, related_name='customer_relations')
    created_at = models.DateTimeField('添加时间', auto_now_add=True)
    
    class Meta:
        db_table = 'customer_tag_relations'
        unique_together = ['customer', 'tag']

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('general_manager', '总经理'),
        ('manager', '部门主管'),
        ('sales', '业务员'),
        ('documentary', '跟单员'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('international', '外贸部'),
        ('domestic', '内贸部'),
        ('documentary', '跟单部'),
        ('management', '总经办'),
    ]
    
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='sales')
    department = models.CharField('部门', max_length=20, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    real_name = models.CharField('真实姓名', max_length=50, blank=True, null=True)
    phone = models.CharField('手机号', max_length=20, blank=True, null=True)
    
    # 修复 groups 和 user_permissions 的反向访问器冲突
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customers_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customers_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )
    
    class Meta:
        db_table = 'customers_user'  # 避免与 auth_user 冲突
        verbose_name = '用户'
        verbose_name_plural = '用户'

class CompanySetting(models.Model):
    """公司信息设置"""
    company_name = models.CharField('公司名称', max_length=200, default='Raffinato CRM')
    logo = models.ImageField('公司Logo', upload_to='company/', blank=True, null=True)
    address = models.CharField('公司地址', max_length=500, blank=True, null=True)
    phone = models.CharField('联系电话', max_length=50, blank=True, null=True)
    email = models.CharField('公司邮箱', max_length=100, blank=True, null=True)
    website = models.URLField('公司网站', blank=True, null=True)
    
    # 邮件签名
    email_signature = models.TextField('邮件签名', blank=True, null=True, help_text='发送邮件时自动添加的签名')
    
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'company_settings'
        verbose_name = '公司设置'
        verbose_name_plural = '公司设置'
    
    def __str__(self):
        return self.company_name

class BusinessRule(models.Model):
    """业务规则设置"""
    
    # 客户等级降级规则
    vip_downgrade_days = models.IntegerField('VIP降级天数', default=30, help_text='VIP客户超过多少天未联系降级为高级')
    advanced_downgrade_days = models.IntegerField('高级降级天数', default=60, help_text='高级客户超过多少天未联系降级为中级')
    intermediate_downgrade_days = models.IntegerField('中级降级天数', default=90, help_text='中级客户超过多少天未联系降级为潜在')
    dormant_days = models.IntegerField('沉睡标记天数', default=180, help_text='潜在客户超过多少天未联系标记为沉睡')
    
    # 跟进提醒规则
    followup_reminder_days = models.IntegerField('跟进提醒天数', default=30, help_text='距离上次联系多少天后提醒跟进')
    
    # 邮件规则
    daily_email_limit = models.IntegerField('每日邮件上限', default=200, help_text='每人每天最多发送邮件数')
    
    # 新客户默认设置
    default_customer_level = models.CharField('新客户默认等级', max_length=20, default='potential',
        choices=[('potential', '潜在客户'), ('intermediate', '中级客户'), ('advanced', '高级客户'), ('vip', 'VIP客户')])
    
    # 更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'business_rules'
        verbose_name = '业务规则'
        verbose_name_plural = '业务规则'
    
    def __str__(self):
        return f"业务规则 (更新于 {self.updated_at.strftime('%Y-%m-%d %H:%M')})"
    
    @classmethod
    def get_settings(cls):
        """获取设置（单例模式）"""
        settings, created = cls.objects.get_or_create(id=1)
        return settings

class BackupRecord(models.Model):
    """备份记录"""
    filename = models.CharField('备份文件名', max_length=200)
    file_size = models.IntegerField('文件大小(KB)', default=0)
    backup_type = models.CharField('备份类型', max_length=20, choices=[
        ('manual', '手动备份'),
        ('auto', '自动备份'),
    ], default='manual')
    created_at = models.DateTimeField('备份时间', auto_now_add=True)
    
    class Meta:
        db_table = 'backup_records'
        ordering = ['-created_at']
        verbose_name = '备份记录'
        verbose_name_plural = '备份记录'
    
    def __str__(self):
        return f"{self.filename} - {self.created_at}"

class CommunicationLog(models.Model):
    """沟通记录"""
    
    CHANNEL_CHOICES = [
        ('email', '邮件'),
        ('phone', '电话'),
        ('wechat', '微信'),
        ('whatsapp', 'WhatsApp'),
        ('visit', '线下拜访'),
        ('other', '其他'),
    ]
    
    DIRECTION_CHOICES = [
        ('outgoing', '发出'),
        ('incoming', '收到'),
    ]
    
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='communications')
    
    # 沟通基本信息
    channel = models.CharField('沟通渠道', max_length=20, choices=CHANNEL_CHOICES)
    direction = models.CharField('方向', max_length=10, choices=DIRECTION_CHOICES)
    subject = models.CharField('主题', max_length=200, blank=True)
    content = models.TextField('沟通内容')
    
    # 邮件相关
    email_id = models.CharField('邮件ID', max_length=100, blank=True, help_text='关联的发送记录')
    
    # 电话相关
    call_duration = models.IntegerField('通话时长(秒)', null=True, blank=True)
    
    # 附件
    attachment = models.FileField('附件', upload_to='communication/%Y/%m/', blank=True, null=True)
    
    # 跟进
    followup_needed = models.BooleanField('需要跟进', default=False)
    followup_date = models.DateField('下次跟进日期', null=True, blank=True)
    followup_note = models.CharField('跟进备注', max_length=200, blank=True)
    
    # 记录人
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='communications')
    created_at = models.DateTimeField('记录时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'communication_logs'
        ordering = ['-created_at']
        verbose_name = '沟通记录'
        verbose_name_plural = '沟通记录'
    
    def __str__(self):
        return f"{self.customer.company_name} - {self.get_channel_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_call_duration_display(self):
        if self.call_duration:
            minutes = self.call_duration // 60
            seconds = self.call_duration % 60
            if minutes > 0:
                return f"{minutes}分{seconds}秒"
            return f"{seconds}秒"
        return "-"

# ========== 自动化邮件序列 ==========

class EmailSequence(models.Model):
    """邮件序列（自动化流程）"""
    TRIGGER_CHOICES = [
        ('customer_created', '客户创建后'),
        ('customer_tagged', '客户打标签后'),
        ('email_opened', '邮件被打开后'),
        ('link_clicked', '链接被点击后'),
        ('no_response_days', '无回复X天后'),
        ('order_created', '创建订单后'),
        ('order_completed', '订单完成后'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '启用中'),
        ('paused', '已暂停'),
        ('stopped', '已停止'),
    ]
    
    name = models.CharField('序列名称', max_length=200)
    description = models.TextField('描述', blank=True)
    trigger_type = models.CharField('触发条件', max_length=50, choices=TRIGGER_CHOICES)
    trigger_days = models.IntegerField('触发延迟（天）', default=0, help_text='条件满足后延迟几天发送')
    trigger_tag = models.CharField('触发标签', max_length=100, blank=True, help_text='仅当客户有此标签时触发')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # 统计
    total_customers = models.IntegerField('影响客户数', default=0)
    total_sent = models.IntegerField('已发送邮件数', default=0)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'email_sequences'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class EmailSequenceStep(models.Model):
    """邮件序列步骤（每一步是一封邮件）"""
    sequence = models.ForeignKey(EmailSequence, on_delete=models.CASCADE, related_name='steps')
    step_order = models.IntegerField('步骤顺序', default=0)
    wait_days = models.IntegerField('等待天数', default=0, help_text='上一步发送后等待几天')
    
    # 邮件内容
    subject = models.CharField('邮件主题', max_length=500)
    template = models.TextField('邮件内容', help_text='支持变量：{{ company_name }}、{{ contact_person }}、{{ customer_name }}')
    
    # 可选设置
    send_time = models.TimeField('指定发送时间', blank=True, null=True, help_text='例如 09:00，留空则立即发送')
    only_weekdays = models.BooleanField('仅工作日发送', default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'email_sequence_steps'
        ordering = ['sequence', 'step_order']
    
    def __str__(self):
        return f"{self.sequence.name} - 步骤{self.step_order}: {self.subject[:50]}"


class EmailSequenceQueue(models.Model):
    """邮件序列队列（待发送的邮件）"""
    STATUS_CHOICES = [
        ('pending', '等待发送'),
        ('sent', '已发送'),
        ('failed', '发送失败'),
        ('cancelled', '已取消'),
    ]
    
    sequence = models.ForeignKey(EmailSequence, on_delete=models.CASCADE)
    step = models.ForeignKey(EmailSequenceStep, on_delete=models.CASCADE)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    
    scheduled_time = models.DateTimeField('计划发送时间')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 发送记录
    sent_at = models.DateTimeField('实际发送时间', blank=True, null=True)
    error_message = models.TextField('错误信息', blank=True)
    
    # 追踪
    email_log_id = models.IntegerField('关联邮件日志ID', blank=True, null=True)
    
    # ========== 新增：重试机制字段 ==========
    retry_count = models.IntegerField('已重试次数', default=0)
    last_retry_at = models.DateTimeField('上次重试时间', blank=True, null=True)
    max_retries = models.IntegerField('最大重试次数', default=3)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'email_sequence_queue'
        ordering = ['scheduled_time']
    
    def __str__(self):
        return f"{self.customer.company_name} - {self.sequence.name} - 步骤{self.step.step_order}"


class CustomerSequenceState(models.Model):
    """客户在序列中的状态"""
    STATUS_CHOICES = [
        ('active', '进行中'),
        ('completed', '已完成'),
        ('exited', '已退出'),
        ('paused', '已暂停'),
    ]
    
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='sequence_states')
    sequence = models.ForeignKey(EmailSequence, on_delete=models.CASCADE)
    current_step = models.IntegerField('当前步骤', default=0)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    entered_at = models.DateTimeField('进入序列时间', auto_now_add=True)
    completed_at = models.DateTimeField('完成时间', blank=True, null=True)
    
    class Meta:
        db_table = 'customer_sequence_states'
        unique_together = [['customer', 'sequence']]
    
    def __str__(self):
        return f"{self.customer.company_name} - {self.sequence.name}"

# ========== 团队协作与权限 ==========

class Department(models.Model):
    """部门"""
    name = models.CharField('部门名称', max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'departments'
    
    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """用户扩展信息"""
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('dept_leader', '部门主管'),
        ('sales', '销售人员'),
        ('readonly', '只读用户'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='sales')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属部门')
    phone = models.CharField('电话', max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class CustomerAssignment(models.Model):
    """客户分配记录"""
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='assignments')
    sales_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_history')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments_made')
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField('分配备注', blank=True)
    is_active = models.BooleanField('当前有效', default=True)
    
    class Meta:
        db_table = 'customer_assignments'
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.customer.company_name} -> {self.sales_user.username}"

class UnsubscribeBlacklist(models.Model):
    """退订黑名单"""
    email = models.EmailField('邮箱', unique=True, db_index=True)
    customer = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联客户')
    unsubscribe_reason = models.CharField('退订原因', max_length=200, blank=True)
    unsubscribed_at = models.DateTimeField('退订时间', auto_now_add=True)
    unsubscribed_from = models.CharField('退订来源', max_length=100, blank=True)  # 哪封邮件退订的
    ip_address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    
    class Meta:
        db_table = 'unsubscribe_blacklist'
        ordering = ['-unsubscribed_at']
        verbose_name = '退订黑名单'
        verbose_name_plural = '退订黑名单'
    
    def __str__(self):
        return self.email
