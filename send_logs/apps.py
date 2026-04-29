from django.apps import AppConfig

class SendLogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'send_logs'
    verbose_name = '邮件发送记录'