from django.core.management.base import BaseCommand
from customers.models import UserEmailConfig, User

class Command(BaseCommand):
    help = '创建默认发件配置'
    
    def handle(self, *args, **options):
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR("❌ 没有用户，请先创建管理员账户"))
            self.stdout.write("运行: python manage.py createsuperuser")
            return
        
        self.stdout.write(f"找到用户: {user.username} (ID: {user.id})")
        
        existing = UserEmailConfig.objects.filter(user=user, is_default=True).first()
        if existing:
            self.stdout.write(self.style.WARNING(f"配置已存在: {existing.email}"))
            return
        
        config = UserEmailConfig(
            user=user,
            email='test@example.com',
            smtp_host='smtp.gmail.com',
            smtp_port=587,
            smtp_password='your-password',
            from_name='Raffinato CRM',
            signature='Raffinato Team',
            is_default=True,
            daily_limit=50,
            sent_today=0,
            is_active=True,
        )
        config.save()
        self.stdout.write(self.style.SUCCESS(f"✅ 已创建发件配置"))
        self.stdout.write(f"   邮箱: {config.email}")
        self.stdout.write(f"   每日限额: {config.daily_limit}")