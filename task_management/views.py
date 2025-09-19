from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User, Task
from .serializers import (
    LoginSerializer, UserSerializer, TaskSerializer, 
    TaskUpdateSerializer, TaskReportSerializer
)

# Custom permission classes
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'superadmin']:
            return True
        return obj.assigned_to == request.user

class IsAdminOrSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['admin', 'superadmin']

# API Views
class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserTaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)

class TaskUpdateView(generics.UpdateAPIView):
    serializer_class = TaskUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.role == 'user':
            return Task.objects.filter(assigned_to=self.request.user)
        else:
            return Task.objects.all()

class TaskReportView(generics.RetrieveAPIView):
    serializer_class = TaskReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]

    def get_object(self):
        task = get_object_or_404(Task, id=self.kwargs['pk'], status='completed')
        
        # Admin can only see reports from their assigned users
        if self.request.user.role == 'admin':
            if task.assigned_to.assigned_admin != self.request.user:
                raise PermissionError("You can only view reports from your assigned users")
        
        return task

# Admin Panel Views
@login_required
def admin_dashboard(request):
    if request.user.role not in ['admin', 'superadmin']:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('admin_login')
    
    context = {}
    
    if request.user.role == 'superadmin':
        context.update({
            'total_users': User.objects.filter(role='user').count(),
            'total_admins': User.objects.filter(role='admin').count(),
            'total_tasks': Task.objects.count(),
            'completed_tasks': Task.objects.filter(status='completed').count(),
        })
    else:  # admin
        managed_users = User.objects.filter(assigned_admin=request.user)
        context.update({
            'managed_users_count': managed_users.count(),
            'assigned_tasks': Task.objects.filter(assigned_by=request.user).count(),
            'completed_tasks': Task.objects.filter(
                assigned_by=request.user, 
                status='completed'
            ).count(),
        })
    
    return render(request, 'admin/dashboard.html', context)

@login_required
def manage_users(request):
    if request.user.role != 'superadmin':
        messages.error(request, 'Access denied. SuperAdmin privileges required.')
        return redirect('admin_dashboard')
    
    users = User.objects.filter(role='user').order_by('-created_at')
    admins = User.objects.filter(role='admin').order_by('-created_at')
    
    return render(request, 'admin/manage_users.html', {
        'users': users,
        'admins': admins
    })

@login_required
def manage_tasks(request):
    if request.user.role not in ['admin', 'superadmin']:
        messages.error(request, 'Access denied.')
        return redirect('admin_login')
    
    if request.user.role == 'superadmin':
        tasks = Task.objects.all().order_by('-created_at')
        users = User.objects.filter(role='user')
    else:  # admin
        tasks = Task.objects.filter(assigned_by=request.user).order_by('-created_at')
        users = User.objects.filter(assigned_admin=request.user)
    
    return render(request, 'admin/manage_tasks.html', {
        'tasks': tasks,
        'users': users
    })

@login_required
def task_reports(request):
    if request.user.role not in ['admin', 'superadmin']:
        messages.error(request, 'Access denied.')
        return redirect('admin_login')
    
    if request.user.role == 'superadmin':
        completed_tasks = Task.objects.filter(status='completed').order_by('-completed_at')
    else:  # admin
        completed_tasks = Task.objects.filter(
            assigned_by=request.user, 
            status='completed'
        ).order_by('-completed_at')
    
    return render(request, 'admin/task_reports.html', {
        'completed_tasks': completed_tasks
    })

# AJAX views for dynamic operations
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_user(request):
    if request.user.role != 'superadmin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role='user'
        )
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_task(request):
    if request.user.role not in ['admin', 'superadmin']:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        assigned_user = User.objects.get(id=data['assigned_to'])
        
        # Admin can only assign tasks to their managed users
        if request.user.role == 'admin' and assigned_user.assigned_admin != request.user:
            return JsonResponse({'error': 'You can only assign tasks to your managed users'}, status=403)
        
        task = Task.objects.create(
            title=data['title'],
            description=data['description'],
            assigned_to=assigned_user,
            assigned_by=request.user,
            due_date=data['due_date']
        )
        
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'assigned_to': task.assigned_to.username,
                'status': task.status
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user and user.role in ['admin', 'superadmin']:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient privileges.')
    
    return render(request, 'admin/login.html')

@login_required
def admin_logout_view(request):
    logout(request)
    return redirect('admin_login')
