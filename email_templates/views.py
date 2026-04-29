from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import EmailTemplate

def template_list(request):
    """邮件模板列表"""
    templates = EmailTemplate.objects.filter(is_active=True)
    return render(request, 'email_templates/template_list.html', {'templates': templates})

def template_create(request):
    """创建邮件模板"""
    if request.method == 'POST':
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        
        EmailTemplate.objects.create(
            name=name,
            subject=subject,
            content=content,
            is_active=True
        )
        messages.success(request, f'模板 "{name}" 创建成功')
        return redirect('template_list')
    
    return render(request, 'email_templates/template_form.html')

def template_edit(request, template_id):
    """编辑邮件模板"""
    template = get_object_or_404(EmailTemplate, id=template_id)
    
    if request.method == 'POST':
        template.name = request.POST.get('name')
        template.subject = request.POST.get('subject')
        template.content = request.POST.get('content')
        template.save()
        messages.success(request, f'模板 "{template.name}" 更新成功')
        return redirect('template_list')
    
    return render(request, 'email_templates/template_form.html', {'template': template})

def template_delete(request, template_id):
    """删除邮件模板"""
    template = get_object_or_404(EmailTemplate, id=template_id)
    name = template.name
    template.is_active = False
    template.save()
    messages.success(request, f'模板 "{name}" 已删除')
    return redirect('template_list')

def api_templates(request):
    """获取模板列表API"""
    templates = EmailTemplate.objects.filter(is_active=True).values('id', 'name')
    return JsonResponse(list(templates), safe=False)

def api_preview(request, template_id):
    """预览邮件内容API"""
    from customers.models import Customer
    template = get_object_or_404(EmailTemplate, id=template_id)
    customer_id = request.GET.get('customer_id')
    
    variables = {
        'company_name': '示例公司',
        'contact_person': '张三',
        'country': '意大利',
        'my_name': 'Jp',
        'my_company': 'Raffinato',
    }
    
    if customer_id:
        customer = Customer.objects.get(id=customer_id)
        variables = {
            'company_name': customer.company_name,
            'contact_person': customer.contact_person or '先生/女士',
            'country': customer.country or '',
            'my_name': 'Jp',
            'my_company': 'Raffinato',
        }
    
    subject = template.subject.format(**variables)
    content = template.content.format(**variables)
    
    return JsonResponse({'subject': subject, 'content': content})