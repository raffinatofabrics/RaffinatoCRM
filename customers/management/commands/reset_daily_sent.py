from django.core.management.base import BaseCommand
from customers.models import UserEmailConfig
from django.utils import timezone

class Command(BaseCommand):
    help = '重置每日发送计数'
    
    def handle(self, *args, **options):
        # 重置所有发件配置的 sent_today
        count = UserEmailConfig.objects.update(sent_today=0, last_reset_date=timezone.now())
        self.stdout.write(self.style.SUCCESS(f"✅ 已重置 {count} 个发件配置的每日计数"))