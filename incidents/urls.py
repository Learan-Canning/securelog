"""
URLS.PY - URL Configuration for Incidents App

This file defines URL patterns that map web addresses to view functions.
Django uses these patterns to determine which view should handle each request.

Key Concepts:
- URL Patterns: Map URLs to views (e.g., /create/ → IncidentCreateView)
- Named URLs: Allow reverse lookup in templates (e.g., {% url 'incidents:create' %})
- URL Parameters: <int:pk> captures integer primary keys from URLs
- App Namespacing: 'incidents' namespace prevents URL name conflicts

Assessment Requirements Met:
- LO2.2: CRUD operations accessible via RESTful URLs
- LO1.1: Clear navigation structure for user experience
"""

from django.urls import path  # Django URL pattern matching
from . import views  # Import our view classes and functions

# App namespace - allows {% url 'incidents:create' %} in templates
app_name = 'incidents'

urlpatterns = [
    # === MAIN CRUD PAGES ===
    # Homepage - Dashboard (better for staff application)
    path('', views.DashboardView.as_view(), name='home'),
    
    # All incidents list
    path('list/', views.IncidentListView.as_view(), name='list'),
    
    # Create new incident (CREATE operation)
    path('create/', views.IncidentCreateView.as_view(), name='create'),
    
    # View single incident details (READ operation)
    # <int:pk> captures the incident ID from URL (e.g., /5/ captures pk=5)
    path('<int:pk>/', views.IncidentDetailView.as_view(), name='detail'),
    
    # Edit existing incident (UPDATE operation)
    path('<int:pk>/edit/', views.IncidentUpdateView.as_view(), name='edit'),
    
    # Delete incident (DELETE operation)
    path('<int:pk>/delete/', views.IncidentDeleteView.as_view(), name='delete'),
    
    # === DASHBOARD AND USER-SPECIFIC PAGES ===
    # Main dashboard with statistics and recent incidents
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # User's personal incidents only
    path('my-reports/', views.MyReportsView.as_view(), name='my_reports'),
    
    # === AJAX ENDPOINTS ===
    # These URLs handle dynamic JavaScript requests without page reload
    
    # Update incident status via AJAX (for quick status changes)
    path('ajax/update-status/<int:pk>/', views.update_status, name='update_status'),
    
    # Add comment to incident via AJAX (for real-time commenting)
    path('ajax/add-comment/<int:pk>/', views.add_comment, name='add_comment'),
]