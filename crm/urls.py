from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('customers.urls')),
    path('customers/', include('customers.urls')),  # 这会使用 customers.urls 的第一个路由
    path('templates/', include('templates.urls')),
    path('send-logs/', include('send_logs.urls')),  
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
]