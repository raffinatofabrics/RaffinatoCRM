from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    """
    全局登录中间件：未登录用户访问任何页面（除了白名单）都自动跳转到登录页
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # 白名单路径：这些路径不需要登录
        exempt_paths = [
            '/login/',      # 登录页
            '/logout/',     # 退出页
            '/static/',     # 静态文件（CSS、JS、图片）
            '/media/',      # 媒体文件（用户上传）
            '/admin/',      # Django 后台（如果你需要）
        ]
        
        # 检查当前路径是否在白名单中
        is_exempt = False
        for path in exempt_paths:
            if request.path.startswith(path):
                is_exempt = True
                break
        
        # 如果用户未登录，且不在白名单路径
        if not request.user.is_authenticated and not is_exempt:
            # 跳转到登录页，登录后回到当前页面
            login_url = reverse('login')
            return redirect(f'{login_url}?next={request.path}')
        
        # 否则正常处理请求
        return self.get_response(request)