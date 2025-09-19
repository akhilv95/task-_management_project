from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, Task

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            data['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password')
        return data

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assigned_to', 'assigned_to_name',
            'assigned_by', 'assigned_by_name', 'due_date', 'status', 'status_display',
            'completion_report', 'worked_hours', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'assigned_by', 'created_at', 'updated_at', 'completed_at']

class TaskUpdateSerializer(serializers.ModelSerializer):
    completion_report = serializers.CharField(required=False, allow_blank=False)
    worked_hours = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False,
        min_value=0.01
    )

    class Meta:
        model = Task
        fields = ['status', 'completion_report', 'worked_hours']

    def validate(self, data):
        status = data.get('status')
        completion_report = data.get('completion_report')
        worked_hours = data.get('worked_hours')

        if status == 'completed':
            if not completion_report:
                raise serializers.ValidationError({
                    'completion_report': 'Completion report is required when marking task as completed.'
                })
            if not worked_hours:
                raise serializers.ValidationError({
                    'worked_hours': 'Worked hours is required when marking task as completed.'
                })
        return data

    def update(self, instance, validated_data):
        if validated_data.get('status') == 'completed':
            validated_data['completed_at'] = timezone.now()
        return super().update(instance, validated_data)

class TaskReportSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'assigned_to_name', 'assigned_by_name',
            'completion_report', 'worked_hours', 'completed_at', 'due_date'
        ]
