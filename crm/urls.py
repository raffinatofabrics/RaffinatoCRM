from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from customers.views import MobileFriendlyLoginView  # 👈 添加这行

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('customers.urls')),
    path('customers/', include('customers.urls')),
    path('templates/', include('templates.urls')),
    path('send-logs/', include('send_logs.urls')),
    path('login/', MobileFriendlyLoginView.as_view(template_name='registration/login.html'), name='login'),  # 👈 改这行
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
]

if not settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)