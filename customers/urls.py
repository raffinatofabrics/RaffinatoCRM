from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    # ========== 首页 - 业务数据大屏（需要登录才能访问） ==========
    path('', login_required(views.stats_dashboard), name='stats_dashboard'),
    
    # ========== 客户管理 ==========
    path('customers/', views.customer_list, name='customer_list'),
    path('import/', views.import_customers, name='import_customers'),
    path('export/', views.export_customers, name='export_customers'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('batch-send-email/', views.batch_send_email, name='batch_send_email'),
    path('batch-verify-emails/', views.batch_verify_emails, name='batch_verify_emails'),
    path('batch-update-scores/', views.batch_update_scores, name='batch_update_scores'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    
    # 搜索任务
    path('search-tasks/', views.search_task_list, name='search_task_list'),
    path('search-tasks/create/', views.search_task_create, name='search_task_create'),
    path('search-tasks/<int:task_id>/', views.search_task_detail, name='search_task_detail'),
    path('search-tasks/<int:task_id>/delete/', views.search_task_delete, name='search_task_delete'),
    path('search-tasks/<int:task_id>/run/', views.search_task_run, name='search_task_run'),
    path('search-tasks/batch-delete/', views.batch_delete_search_tasks, name='batch_delete_search_tasks'),
    
    # 搜索结果
    path('search-results/<int:result_id>/import/', views.search_result_import, name='search_result_import'),
    path('search-results/<int:result_id>/ignore/', views.search_result_ignore, name='search_result_ignore'),
    
    # 客户沟通记录
    path('communication/<int:customer_id>/list/', views.communication_list, name='communication_list'),
    path('communication/<int:customer_id>/create/', views.communication_create, name='communication_create'),
    path('communication/<int:log_id>/edit/', views.communication_edit, name='communication_edit'),
    path('communication/<int:log_id>/delete/', views.communication_delete, name='communication_delete'),
    path('communication/<int:log_id>/detail/', views.communication_detail, name='communication_detail'),

    # 客户操作
    path('<int:customer_id>/update-level/', views.update_customer_level, name='update_customer_level'),
    path('<int:customer_id>/send-email/', views.send_email_to_customer, name='send_email_to_customer'),
    path('<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('<int:customer_id>/edit/', views.customer_edit, name='customer_edit'),
    path('<int:customer_id>/add-communication/', views.add_communication, name='add_communication'),
    path('<int:customer_id>/verify-email/', views.verify_email, name='verify_email'),
    path('<int:customer_id>/update-score/', views.update_customer_score, name='update_customer_score'),
    
    # 公司文档
    path('documents/', views.document_list, name='document_list'),
    path('documents/upload/', views.document_upload, name='document_upload'),
    path('documents/<int:doc_id>/delete/', views.document_delete, name='document_delete'),
    path('documents/<int:doc_id>/download/', views.document_download, name='document_download'),
    
    # 订单管理
    # 订单管理 - 注意顺序：具体的放前面，模糊的放后面
    path('orders/<int:order_id>/export/<str:doc_type>/', views.order_export_pdf, name='order_export_pdf'),
    path('orders/<int:order_id>/print/', views.order_print, name='order_print'),
    path('orders/<int:order_id>/edit/', views.order_edit, name='order_edit'),
    path('orders/<int:order_id>/delete/', views.order_delete, name='order_delete'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),  # 这个放最后
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/batch-delete/', views.batch_delete_orders, name='batch_delete_orders'),
    path('orders/batch-update-status/', views.batch_update_order_status, name='batch_update_order_status'),   # 批量调整订单状态
    path('<int:order_id>/update-cost/', views.update_order_cost, name='update_order_cost'),  # 这个也需要统一

   # 客户操作
    path('<int:customer_id>/delete/', views.customer_delete, name='customer_delete'),
    path('batch-delete/', views.batch_delete_customers, name='batch_delete_customers'),

   #订单汇总
    path('order-summary/', views.order_summary, name='order_summary'),
    path('api/customer-search/', views.api_customer_search, name='api_customer_search'),
    path('api/product-search/', views.api_product_search, name='api_product_search'),
    
    #邮件发送
    path('<int:customer_id>/get-template-content/', views.get_template_content, name='get_template_content'),
    path('get-template-content/', views.get_template_content_universal, name='get_template_content_universal'),
    
    #多邮箱配置
    path('email-configs/', views.email_config_list, name='email_config_list'),
    path('email-configs/create/', views.email_config_create, name='email_config_create'),
    path('email-configs/<int:config_id>/edit/', views.email_config_edit, name='email_config_edit'),
    path('email-configs/<int:config_id>/delete/', views.email_config_delete, name='email_config_delete'),
    path('email-configs/<int:config_id>/test/', views.email_config_test, name='email_config_test'),
    path('api/user-email-configs/', views.api_user_email_configs, name='api_user_email_configs'),

    #操作日志管理
    path('operation-logs/', views.operation_log_list, name='operation_log_list'),
    path('operation-logs/clear/', views.clear_operation_logs, name='clear_operation_logs'),

    #业务章管理
    path('seals/', views.seal_list, name='seal_list'),
    path('seal/upload/', views.seal_upload, name='seal_upload'),
    path('seal/delete/<int:seal_id>/', views.seal_delete, name='seal_delete'),
    path('seal/reorder/', views.seal_reorder, name='seal_reorder'),

    #客户标签管理
    path('api/tags/', views.tag_list_api, name='tag_list_api'),
    path('api/customer/<int:customer_id>/tags/', views.get_customer_tags, name='get_customer_tags'),
    path('api/customer/<int:customer_id>/add-tag/', views.add_customer_tag, name='add_customer_tag'),
    path('api/customer/<int:customer_id>/remove-tag/<int:tag_id>/', views.remove_customer_tag, name='remove_customer_tag'),
    path('api/batch-add-tags/', views.batch_add_tags, name='batch_add_tags'),

    #手动添加客户
    path('add/', views.add_customer_manual, name='add_customer_manual'),

    #统计大屏
    path('stats-dashboard/', views.stats_dashboard, name='stats_dashboard'),

    #用户管理
    path('users/', views.user_list, name='user_list'),
    path('user/create/', views.user_create, name='user_create'),
    path('user/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('user/<int:user_id>/delete/', views.user_delete, name='user_delete'),

    #公司设置
    path('settings/company/', views.company_settings, name='company_settings'),

    # 管理员邮箱配置管理
    path('admin/email-configs/', views.admin_email_config_list, name='admin_email_config_list'),
    path('admin/email-configs/create/', views.admin_email_config_create, name='admin_email_config_create'),
    path('admin/email-configs/<int:config_id>/edit/', views.admin_email_config_edit, name='admin_email_config_edit'),
    path('admin/email-configs/<int:config_id>/delete/', views.admin_email_config_delete, name='admin_email_config_delete'),
    path('admin/email-configs/<int:config_id>/test/', views.admin_email_config_test, name='admin_email_config_test'),

    #客户沉睡设置
    path('settings/business-rules/', views.business_rules_settings, name='business_rules_settings'),

    #数据备份设置
    path('backup/', views.backup_list, name='backup_list'),
    path('backup/create/', views.backup_create, name='backup_create'),
    path('backup/<int:backup_id>/download/', views.backup_download, name='backup_download'),
    path('backup/<int:backup_id>/delete/', views.backup_delete, name='backup_delete'),
    path('backup/restore/', views.backup_restore, name='backup_restore'),
    
    #AI搜索功能 
    path('ai/generate-email/<int:customer_id>/', views.generate_ai_email, name='generate_ai_email'),

    #搜索后批量导入功能 
    path('search-tasks/<int:task_id>/batch-import/', views.batch_import_results, name='batch_import_results'),
    path('search-tasks/<int:task_id>/export/', views.export_search_results, name='export_search_results'),

       # 邮件追踪
    path('track/open/<int:log_id>/', views.track_open, name='track_open'),
    path('track/click/<int:log_id>/<str:link_id>/', views.track_click, name='track_click'),
    path('track/stats/<int:log_id>/', views.track_stats, name='track_stats'),

    # 退订管理（新添加）
    path('unsubscribe/<int:log_id>/', views.unsubscribe, name='unsubscribe'),
    path('unsubscribe/api/', views.unsubscribe_api, name='unsubscribe_api'),

    # 自动化邮件序列
    path('email-sequences/', views.email_sequence_list, name='email_sequence_list'),
    path('email-sequences/create/', views.email_sequence_create, name='email_sequence_create'),
    path('email-sequences/<int:pk>/', views.email_sequence_detail, name='email_sequence_detail'),
    path('email-sequences/<int:pk>/edit/', views.email_sequence_edit, name='email_sequence_edit'),
    path('email-sequences/<int:pk>/delete/', views.email_sequence_delete, name='email_sequence_delete'),
    path('email-sequences/<int:pk>/toggle/', views.email_sequence_toggle, name='email_sequence_toggle'),
    path('email-sequences/<int:pk>/add-step/', views.email_sequence_add_step, name='email_sequence_add_step'),
    path('email-sequence-steps/<int:step_id>/edit/', views.email_sequence_edit_step, name='email_sequence_edit_step'),
    path('email-sequence-steps/<int:step_id>/delete/', views.email_sequence_delete_step, name='email_sequence_delete_step'),
    path('email-queue/', views.email_sequence_queue, name='email_sequence_queue'),
    path('email-queue/<int:queue_id>/cancel/', views.email_sequence_cancel, name='email_sequence_cancel'),

    #客户分配
    path('api/sales-list/', views.api_sales_list, name='api_sales_list'),
    path('api/assign-customer/', views.api_assign_customer, name='api_assign_customer'),

    # 邮件统计报表
    path('email-stats/', views.email_stats_dashboard, name='email_stats_dashboard'),
    path('email-stats/detail/', views.email_stats_detail, name='email_stats_detail'),
    path('email-stats/api/', views.email_stats_api, name='email_stats_api'),
]