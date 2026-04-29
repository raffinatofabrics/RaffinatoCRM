import time
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.conf import settings
from customers.models import EmailSequenceQueue, Customer, UserEmailConfig, CustomerSequenceState, UnsubscribeBlacklist
from send_logs.models import SendLog


class Command(BaseCommand):
    help = '处理邮件队列，发送到期的邮件'

    def add_arguments(self, parser):
        parser.add_argument('--once', action='store_true', help='只运行一次')
        parser.add_argument('--limit', type=int, default=50, help='每次处理的邮件数量')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("启动邮件队列处理器..."))

        while True:
            try:
                now = timezone.now()
                pending = EmailSequenceQueue.objects.filter(
                    status='pending',
                    scheduled_time__lte=now
                ).order_by('scheduled_time')[:options['limit']]

                if pending.exists():
                    self.stdout.write(f"找到 {pending.count()} 封待发送邮件")
                    for queue_item in pending:
                        self.send_queued_email(queue_item)
                        time.sleep(3)
                else:
                    self.stdout.write("没有待发送邮件")

                if options['once']:
                    break
                time.sleep(60)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("手动停止"))
                break
            except Exception as e:
                self.stderr.write(f"错误: {e}")
                time.sleep(60)

    def send_queued_email(self, queue_item):
        try:
            customer = queue_item.customer
            step = queue_item.step
            sequence = queue_item.sequence

            # 检查退订黑名单
            if UnsubscribeBlacklist.objects.filter(email=customer.email).exists():
                queue_item.status = 'cancelled'
                queue_item.error_message = '用户在退订黑名单中'
                queue_item.save()
                self.stdout.write(self.style.WARNING(f"🚫 跳过退订用户: {customer.email}"))
                return

            # 速率限制检查
            email_config = UserEmailConfig.objects.filter(is_default=True, is_active=True).first()
            if email_config and email_config.sent_today >= email_config.daily_limit:
                tomorrow = timezone.now() + timedelta(days=1)
                tomorrow = tomorrow.replace(hour=9, minute=0, second=0)
                queue_item.scheduled_time = tomorrow
                queue_item.save()
                self.stdout.write(self.style.WARNING(f"⏰ 今日已达上限，推迟到明天"))
                return

            # 检查是否已完成
            if CustomerSequenceState.objects.filter(customer=customer, sequence=sequence, status='completed').exists():
                queue_item.status = 'cancelled'
                queue_item.save()
                return

            # 变量替换
            variables = {
                'company_name': customer.company_name or '',
                'contact_person': customer.contact_person or '先生/女士',
                'country': customer.country or '',
                'city': customer.city or '',
                'province': customer.province or '',
                'phone': customer.phone or '',
            }

            subject = step.subject
            content = step.template or ''
            for key, value in variables.items():
                subject = subject.replace('{' + key + '}', str(value))
                subject = subject.replace('{{' + key + '}}', str(value))
                content = content.replace('{' + key + '}', str(value))
                content = content.replace('{{' + key + '}}', str(value))

            # 创建发送记录
            send_log = SendLog.objects.create(
                customer=customer,
                recipient=customer.email,
                subject=subject,
                content=content,
                status='pending',
                sent_at=timezone.now()
            )

            # 追踪像素
            tracking_img = f'<img src="/track/open/{send_log.id}/" width="1" height="1" style="display:none;">'

            # 退订链接
            unsubscribe_url = f"/unsubscribe/{send_log.id}/?email={customer.email}"
            unsubscribe_link = f'<br><br><hr><p style="font-size:12px;color:#999;">如果您不希望继续收到此类邮件，<a href="{unsubscribe_url}">点击这里退订</a></p>'

            final_content = content + tracking_img + unsubscribe_link

            # 发送
            from_email = email_config.email if email_config else settings.DEFAULT_FROM_EMAIL
            msg = EmailMultiAlternatives(
                subject=subject,
                body=final_content,
                from_email=from_email,
                to=[customer.email],
            )
            msg.attach_alternative(final_content, "text/html")
            msg.send()

            # 更新状态
            queue_item.status = 'sent'
            queue_item.sent_at = timezone.now()
            queue_item.email_log_id = send_log.id
            queue_item.retry_count = 0
            queue_item.save()

            send_log.status = 'sent'
            send_log.save()

            if email_config:
                email_config.sent_today += 1
                email_config.save()

            # 安排下一封
            next_step = sequence.steps.filter(step_order=step.step_order + 1).first()
            if next_step:
                CustomerSequenceState.objects.filter(customer=customer, sequence=sequence).update(current_step=step.step_order + 1)
                scheduled_time = timezone.now() + timedelta(days=next_step.wait_days)
                EmailSequenceQueue.objects.create(
                    sequence=sequence,
                    step=next_step,
                    customer=customer,
                    scheduled_time=scheduled_time,
                    status='pending'
                )
                self.stdout.write(f"📅 已安排下一封: {next_step.subject}")
            else:
                CustomerSequenceState.objects.filter(customer=customer, sequence=sequence).update(status='completed', completed_at=timezone.now())
                self.stdout.write(f"🏁 序列完成: {customer.email}")

            self.stdout.write(self.style.SUCCESS(f"✅ 已发送: {customer.email} - {subject}"))

        except Exception as e:
            self.stderr.write(f"❌ 发送失败: {e}")
            queue_item.retry_count += 1
            queue_item.last_retry_at = timezone.now()
            queue_item.error_message = str(e)

            if queue_item.retry_count < queue_item.max_retries:
                delays = [5, 30, 120]
                delay_minutes = delays[min(queue_item.retry_count - 1, len(delays) - 1)]
                queue_item.scheduled_time = timezone.now() + timedelta(minutes=delay_minutes)
                queue_item.status = 'pending'
                queue_item.save()
                self.stdout.write(self.style.WARNING(f"🔄 将在 {delay_minutes} 分钟后重试 ({queue_item.retry_count}/{queue_item.max_retries})"))
            else:
                queue_item.status = 'failed'
                queue_item.save()
                self.stdout.write(self.style.ERROR(f"💀 彻底失败: {customer.email}"))