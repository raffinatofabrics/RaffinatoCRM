from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from customers.models import OperationLog

class Command(BaseCommand):
    help = '删除指定天数前的操作日志'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=60,
            help='保留天数（默认60天）',
        )

    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = OperationLog.objects.filter(created_at__lt=cutoff_date).delete()[0]
        self.stdout.write(self.style.SUCCESS(f'已删除 {deleted_count} 条 {days} 天前的日志'))