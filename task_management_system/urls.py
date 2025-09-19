from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def home_redirect(request):
    """Redirect home page to admin panel"""
    return redirect('admin_login')

urlpatterns = [
    path('admin/', admin.site.urls),  # Django admin
    path('', home_redirect, name='home'),  # Redirect root to login
    path('', include('task_management.urls')),  # Our app URLs
]