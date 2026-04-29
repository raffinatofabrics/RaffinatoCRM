import re
import imaplib
import email
from email.header import decode_header
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from send_logs.models import SendLog
from customers.models import Customer, EmailSequenceQueue


class Command(BaseCommand):
    help = '处理邮件退信（通过IMAP读取退信邮箱）'
    
    def add_arguments(self, parser):
        parser.add_argument('--imap-server', type=str, help='IMAP服务器地址')
        parser.add_argument('--email', type=str, help='退信邮箱')
        parser.add_argument('--password', type=str, help='邮箱密码')
        parser.add_argument('--mark-read', action='store_true', help='处理后将邮件标记为已读')
    
    def handle(self, *args, **options):
        # 获取配置
        imap_server = options.get('imap_server') or getattr(settings, 'BOUNCE_IMAP_SERVER', None)
        email_address = options.get('email') or getattr(settings, 'BOUNCE_EMAIL', None)
        email_password = options.get('password') or getattr(settings, 'BOUNCE_EMAIL_PASSWORD', None)
        
        if not all([imap_server, email_address, email_password]):
            self.stdout.write(self.style.ERROR(
                "请配置 IMAP 服务器信息\n"
                "方式1: python manage.py process_bounces --imap-server imap.qq.com --email xxx@qq.com --password xxx\n"
                "方式2: 在 settings.py 中配置 BOUNCE_IMAP_SERVER, BOUNCE_EMAIL, BOUNCE_EMAIL_PASSWORD"
            ))
            return
        
        try:
            # 连接 IMAP
            self.stdout.write(f"正在连接 {imap_server}...")
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(email_address, email_password)
            mail.select('INBOX')
            
            # 搜索未读邮件
            result, data = mail.search(None, '(UNSEEN)')
            if result != 'OK':
                self.stdout.write("没有新邮件")
                mail.close()
                mail.logout()
                return
            
            email_ids = data[0].split()
            self.stdout.write(f"找到 {len(email_ids)} 封未读邮件")
            
            processed = 0
            for email_id in email_ids:
                result, msg_data = mail.fetch(email_id, '(RFC822)')
                if result != 'OK':
                    continue
                
                msg = email.message_from_bytes(msg_data[0][1])
                
                # 解析退信
                bounce_info = self.parse_bounce(msg)
                if bounce_info:
                    self.handle_bounce(bounce_info)
                    processed += 1
                
                # 标记为已读
                if options.get('mark_read'):
                    mail.store(email_id, '+FLAGS', '\\Seen')
            
            mail.close()
            mail.logout()
            
            self.stdout.write(self.style.SUCCESS(f"✅ 已处理 {processed} 封退信"))
            
        except Exception as e:
            self.stderr.write(f"错误: {e}")
            import traceback
            traceback.print_exc()
    
    def parse_bounce(self, msg):
        """解析退信邮件，提取原始收件人"""
        subject = self.decode_header_value(msg.get('Subject', ''))
        body = self.get_body(msg)
        
        self.stdout.write(f"解析邮件: {subject[:50]}...")
        
        # 退信类型识别模式
        hard_patterns = [
            r'no such user',
            r'user unknown',
            r'recipient rejected',
            r'mailbox unavailable',
            r'invalid address',
            r'does not exist',
            r'收件人不存在',
            r'邮箱不存在',
            r'地址无效',
            r'user not found',
            r'account disabled',
            r'domain not found',
            r'host not found',
            r'550.*User unknown',
            r'550.*No such user',
            r'550.*Invalid recipient',
            r'554.*rejected',
        ]
        
        soft_patterns = [
            r'mailbox full',
            r'quota exceeded',
            r'temporary failure',
            r'邮箱已满',
            r'超出空间限制',
            r'over quota',
            r'temporarily unavailable',
            r'too many connections',
            r'rate limit',
            r'greylisted',
            r'452.*requested action aborted',
            r'421.*service not available',
        ]
        
        # 提取收件人的模式
        extract_patterns = [
            r'Original-Recipient:\s*rfc822;\s*(\S+@\S+)',
            r'Final-Recipient:\s*rfc822;\s*(\S+@\S+)',
            r'for <(\S+@\S+)>',
            r'收件人：?\s*(\S+@\S+)',
            r'To:\s*(\S+@\S+)',
            r'X-Failed-Recipients:\s*(\S+@\S+)',
            r'Failed recipient:\s*(\S+@\S+)',
        ]
        
        # 判断退信类型
        bounce_type = None
        for pattern in hard_patterns:
            if re.search(pattern, subject, re.I) or re.search(pattern, body, re.I):
                bounce_type = 'hard'
                break
        
        if not bounce_type:
            for pattern in soft_patterns:
                if re.search(pattern, subject, re.I) or re.search(pattern, body, re.I):
                    bounce_type = 'soft'
                    break
        
        # 提取原始收件人
        recipient = None
        for pattern in extract_patterns:
            match = re.search(pattern, body, re.I)
            if match:
                recipient = match.group(1)
                break
        
        # 如果还没找到，从正文中提取第一个邮箱
        if not recipient and body:
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', body)
            if emails:
                # 排除退信邮箱本身
                for email_addr in emails:
                    if email_addr != getattr(settings, 'BOUNCE_EMAIL', ''):
                        recipient = email_addr
                        break
        
        if recipient and bounce_type:
            return {
                'recipient': recipient,
                'bounce_type': bounce_type,
                'reason': subject[:200] if subject else body[:200],
            }
        elif recipient:
            self.stdout.write(f"  无法判断退信类型，默认为硬退信: {recipient}")
            return {
                'recipient': recipient,
                'bounce_type': 'hard',
                'reason': subject[:200] if subject else body[:200],
            }
        
        return None
    
    def decode_header_value(self, value):
        """解码邮件头"""
        if not value:
            return ''
        try:
            decoded = decode_header(value)
            result = []
            for text, charset in decoded:
                if isinstance(text, bytes):
                    try:
                        text = text.decode(charset or 'utf-8', errors='ignore')
                    except:
                        text = text.decode('utf-8', errors='ignore')
                result.append(str(text))
            return ' '.join(result)
        except:
            return str(value)
    
    def get_body(self, msg):
        """获取邮件正文"""
        body = ''
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode('utf-8', errors='ignore')
                            break
                    elif content_type == 'text/html' and not body:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode('utf-8', errors='ignore')
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
        except:
            pass
        return body
    
    def handle_bounce(self, bounce_info):
        """处理退信结果"""
        recipient = bounce_info['recipient']
        bounce_type = bounce_info['bounce_type']
        reason = bounce_info['reason']
        
        self.stdout.write(f"\n处理退信: {recipient}")
        self.stdout.write(f"  类型: {bounce_type}")
        self.stdout.write(f"  原因: {reason[:100]}...")
        
        # 查找对应的发送记录
        send_log = SendLog.objects.filter(recipient=recipient).order_by('-sent_at').first()
        if send_log:
            send_log.is_bounced = True
            send_log.bounce_type = bounce_type
            send_log.bounce_reason = reason
            send_log.save()
            self.stdout.write(f"  已更新发送记录 ID: {send_log.id}")
        
        # 查找客户
        customer = Customer.objects.filter(email=recipient).first()
        
        if bounce_type == 'hard':
            if customer:
                customer.email_bounced = True
                customer.bounce_type = bounce_type
                customer.bounce_reason = reason
                customer.bounced_at = timezone.now()
                customer.email_invalid = True
                customer.save()
                
                self.stdout.write(self.style.WARNING(f"  ⚠️ 硬退信，已标记客户无效: {customer.company_name}"))
                
                # 取消该客户所有待发送的队列邮件
                cancelled = EmailSequenceQueue.objects.filter(
                    customer=customer,
                    status='pending'
                ).update(status='cancelled', error_message=f'硬退信: {reason}')
                
                self.stdout.write(f"  已取消 {cancelled} 封待发送邮件")
            else:
                self.stdout.write(f"  ⚠️ 未找到客户: {recipient}")
        else:
            self.stdout.write(f"  📧 软退信，已记录")