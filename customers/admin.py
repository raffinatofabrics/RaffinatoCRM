from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import Customer, Order, Department, UserProfile, CustomerAssignment, CustomerTag, EmailSequence, EmailSequenceStep

User = get_user_model()

# 内联显示 UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户扩展信息'
    fk_name = 'user'

# 自定义 User Admin
class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role', 'get_department')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    def get_role(self, obj):
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.get_role_display()
        return '-'
    get_role.short_description = '角色'
    
    def get_department(self, obj):
        if hasattr(obj, 'profile') and obj.profile and obj.profile.department:
            return obj.profile.department.name
        return '-'
    get_department.short_description = '部门'
    
    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {'fields': ()}),
    )

# 注册自定义 User 模型
try:
    admin.site.unregister(User)
except:
    pass
admin.site.register(User, CustomUserAdmin)

# 注册其他模型
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department']
    list_filter = ['role', 'department']
    search_fields = ['user__username', 'user__email']

@admin.register(CustomerAssignment)
class CustomerAssignmentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'sales_user', 'assigned_by', 'assigned_at', 'is_active']
    list_filter = ['is_active']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'contact_person', 'email', 'level', 'assigned_sales']
    list_filter = ['level', 'business_type']
    search_fields = ['company_name', 'email', 'contact_person']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'customer', 'business_type', 'status', 'order_date']
    list_filter = ['business_type', 'status']

@admin.register(CustomerTag)
class CustomerTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']

@admin.register(EmailSequence)
class EmailSequenceAdmin(admin.ModelAdmin):
    list_display = ['name', 'trigger_type', 'status', 'created_at']

@admin.register(EmailSequenceStep)
class EmailSequenceStepAdmin(admin.ModelAdmin):
    list_display = ['sequence', 'step_order', 'subject', 'wait_days']