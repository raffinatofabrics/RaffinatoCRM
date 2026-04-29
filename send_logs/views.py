from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import SendLog

@login_required
def send_log_list(request):
    """发送记录列表"""
    logs = SendLog.objects.all().order_by('-sent_at')
    
    # 权限过滤：销售只能看到自己的发送记录
    if hasattr(request.user, 'profile'):
        role = request.user.profile.role
        if role == 'sales':
            # 销售只能看到自己客户的发送记录
            logs = logs.filter(customer__assigned_sales=request.user)
        elif role == 'dept_leader':
            dept = request.user.profile.department
            if dept:
                logs = logs.filter(customer__department=dept)
    
    return render(request, 'send_logs/list.html', {'logs': logs})