from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from customers.models import Customer, BusinessRule


class Command(BaseCommand):
    help = '自动降级超过规定时间未联系的客户'

    def handle(self, *args, **options):
        # 获取业务规则配置
        rules = BusinessRule.get_settings()
        
        today = timezone.now()
        downgrade_count = 0
        
        self.stdout.write('开始执行自动降级任务...')
        
        # VIP -> 高级 (使用配置的天数)
        vip_customers = Customer.objects.filter(
            is_deleted=False,
            level='vip',
            last_contact_time__lt=today - timedelta(days=rules.vip_downgrade_days)
        )
        for customer in vip_customers:
            customer.level = 'advanced'
            customer.save()
            downgrade_count += 1
            self.stdout.write(f'VIP客户 "{customer.company_name}" 降级为高级（超过{rules.vip_downgrade_days}天未联系）')
        
        # 高级 -> 中级 (使用配置的天数)
        advanced_customers = Customer.objects.filter(
            is_deleted=False,
            level='advanced',
            last_contact_time__lt=today - timedelta(days=rules.advanced_downgrade_days)
        )
        for customer in advanced_customers:
            customer.level = 'intermediate'
            customer.save()
            downgrade_count += 1
            self.stdout.write(f'高级客户 "{customer.company_name}" 降级为中级（超过{rules.advanced_downgrade_days}天未联系）')
        
        # 中级 -> 潜在 (使用配置的天数)
        intermediate_customers = Customer.objects.filter(
            is_deleted=False,
            level='intermediate',
            last_contact_time__lt=today - timedelta(days=rules.intermediate_downgrade_days)
        )
        for customer in intermediate_customers:
            customer.level = 'potential'
            customer.save()
            downgrade_count += 1
            self.stdout.write(f'中级客户 "{customer.company_name}" 降级为潜在（超过{rules.intermediate_downgrade_days}天未联系）')
        
        # 潜在 -> 沉睡标记 (使用配置的天数)
        dormant_customers = Customer.objects.filter(
            is_deleted=False,
            level='potential',
            last_contact_time__lt=today - timedelta(days=rules.dormant_days),
            is_dormant=False
        )
        for customer in dormant_customers:
            customer.is_dormant = True
            customer.save()
            self.stdout.write(f'潜在客户 "{customer.company_name}" 标记为沉睡（超过{rules.dormant_days}天未联系）')
        
        self.stdout.write(self.style.SUCCESS(f'自动降级任务完成！共降级 {downgrade_count} 个客户'))