from django.urls import path, include
from . import views

# API URL patterns
api_urlpatterns = [
    path('auth/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('tasks/', views.UserTaskListView.as_view(), name='user_tasks'),
    path('tasks/<int:pk>/', views.TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/report/', views.TaskReportView.as_view(), name='task_report'),
]

# Admin Panel URL patterns
admin_urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.admin_logout_view, name='admin_logout'),
    path('users/', views.manage_users, name='manage_users'),
    path('tasks/', views.manage_tasks, name='manage_tasks'),
    path('reports/', views.task_reports, name='task_reports'),
    
    # AJAX endpoints
    path('ajax/create-user/', views.create_user, name='create_user'),
    path('ajax/create-task/', views.create_task, name='create_task'),
]

# Main URL patterns
urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('admin-panel/', include(admin_urlpatterns)),
]