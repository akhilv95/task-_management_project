Task Management Application
A comprehensive Django-based task management system with JWT authentication, role-based access control, and a custom admin panel for tracking task completion reports and worked hours.
Features
Role-Based Access Control

SuperAdmin: Full system access - manage all users, admins, and tasks
Admin: Manage assigned users and their tasks, view completion reports
User: View assigned tasks, update status, submit completion reports

API Features

JWT authentication for secure API access
RESTful endpoints for task management
Task completion tracking with mandatory reports
Worked hours logging and validation
Role-based API permissions

Admin Panel Features

Custom dashboard with role-specific statistics
User and admin management (SuperAdmin only)
Task creation and assignment
Completion reports viewing with worked hours
Responsive Bootstrap-based UI

Tech Stack

Backend: Django 4.2.7, Django REST Framework
Authentication: JWT tokens via djangorestframework-simplejwt
Database: SQLite (development), PostgreSQL (production ready)
Frontend: Bootstrap 5.1.3, Font Awesome icons
API Testing: Built-in Django admin, REST Client support

Login with:

Username: superadmin
Password: admin123
