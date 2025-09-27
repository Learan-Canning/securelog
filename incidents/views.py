"""
VIEWS.PY - Django Views for Incident Reporting System

This file contains all the view logic for handling HTTP requests and responses.
Django views are Python functions or classes that receive HTTP requests and return responses.

Key Concepts:
- Class-Based Views (CBVs): Reusable view classes for common patterns
- Function-Based Views (FBVs): Custom functions for specific logic
- Mixins: Add functionality to CBVs (like LoginRequiredMixin for authentication)
- Generic Views: Django's built-in views for CRUD operations

Assessment Requirements Met:
- LO2.2: CRUD functionality implementation
- LO3.1: Role-based access control
- LO3.3: Access control and permissions
"""

# === DJANGO CORE IMPORTS ===
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages  # Flash messages for user feedback
from django.views.generic import (  # Generic class-based views for common patterns
    ListView,      # For displaying lists of objects
    DetailView,    # For displaying single object details
    CreateView,    # For creating new objects
    UpdateView,    # For editing existing objects
    DeleteView,    # For deleting objects
    TemplateView   # For simple template rendering
)
from django.urls import reverse_lazy  # URL reversing for class-based views
from django.http import JsonResponse  # For AJAX responses
from django.db.models import Q, Count  # Database query utilities

# === LOCAL APP IMPORTS ===
from .models import IncidentReport, IncidentType, IncidentComment
from .forms import IncidentReportForm, IncidentCommentForm  # Our custom forms


class HomePageView(TemplateView):
    """
    HOMEPAGE VIEW - Public landing page (no login required)
    
    This is your blank canvas for practicing HTML/CSS!
    Users see this first, then login to access the dashboard.
    """
    template_name = 'index.html'


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    DASHBOARD VIEW - Main landing page for logged-in users
    
    This view displays key metrics and recent incidents for quick overview.
    Uses Django's TemplateView for simple template rendering with context data.
    
    Features:
    - Statistics cards (total, urgent, personal, pending incidents)
    - Recent incidents list
    - Quick action buttons
    
    Security: LoginRequiredMixin ensures only authenticated users can access
    """
    template_name = 'incidents/dashboard.html'  # HTML template to render
    
    def get_context_data(self, **kwargs):
        """
        Add custom data to template context
        
        Django automatically calls this method to gather data for the template.
        We add statistics and recent incidents that the template can display.
        
        Returns:
            dict: Context dictionary with statistics and incident data
        """
        # Call parent method to get base context (includes request, user, etc.)
        context = super().get_context_data(**kwargs)
        
        # === DASHBOARD STATISTICS ===
        # Count total incidents in database
        context['total_incidents'] = IncidentReport.objects.count()
        
        # Count high-priority incidents that need immediate attention
        context['urgent_incidents'] = IncidentReport.objects.filter(
            severity__in=['high', 'critical']  # Django ORM filter for multiple values
        ).count()
        
        # Count incidents reported by current logged-in user
        context['my_incidents'] = IncidentReport.objects.filter(
            reported_by=self.request.user  # self.request.user is current user
        ).count()
        
        # Count incidents awaiting management review
        context['pending_incidents'] = IncidentReport.objects.filter(
            status__in=['submitted', 'under_review']
        ).count()
        
        # === RECENT INCIDENTS LIST ===
        # Get 5 most recent incidents for dashboard preview
        # [:5] is Python slice notation for first 5 items
        context['recent_incidents'] = IncidentReport.objects.all()[:5]
        
        return context  # Return all context data to template


class IncidentListView(LoginRequiredMixin, ListView):
    """List all incident reports with filtering and search"""
    model = IncidentReport
    template_name = 'incidents/incident_list.html'
    context_object_name = 'incidents'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = IncidentReport.objects.all()
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        
        # Filter by severity
        severity = self.request.GET.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-date_occurred')


class IncidentDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a single incident report"""
    model = IncidentReport
    template_name = 'incidents/incident_detail.html'
    context_object_name = 'incident'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['comment_form'] = IncidentCommentForm()
        return context


class IncidentCreateView(LoginRequiredMixin, CreateView):
    """Create a new incident report"""
    model = IncidentReport
    form_class = IncidentReportForm
    template_name = 'incidents/incident_create.html'
    
    def form_valid(self, form):
        form.instance.reported_by = self.request.user
        messages.success(self.request, 'Incident report created successfully!')
        return super().form_valid(form)


class IncidentUpdateView(LoginRequiredMixin, UpdateView):
    """Edit an existing incident report"""
    model = IncidentReport
    form_class = IncidentReportForm
    template_name = 'incidents/incident_edit.html'
    
    def get_queryset(self):
        # Users can only edit their own reports (unless they're staff)
        if self.request.user.is_staff:
            return IncidentReport.objects.all()
        return IncidentReport.objects.filter(reported_by=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Incident report updated successfully!')
        return super().form_valid(form)


class IncidentDeleteView(LoginRequiredMixin, DeleteView):
    """Delete an incident report"""
    model = IncidentReport
    template_name = 'incidents/incident_delete.html'
    success_url = reverse_lazy('incidents:list')
    
    def get_queryset(self):
        # Users can only delete their own reports (unless they're staff)
        if self.request.user.is_staff:
            return IncidentReport.objects.all()
        return IncidentReport.objects.filter(reported_by=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Incident report deleted successfully!')
        return super().delete(request, *args, **kwargs)


class MyReportsView(LoginRequiredMixin, ListView):
    """View user's own incident reports"""
    model = IncidentReport
    template_name = 'incidents/my_reports.html'
    context_object_name = 'incidents'
    
    def get_queryset(self):
        return IncidentReport.objects.filter(
            reported_by=self.request.user
        ).order_by('-date_occurred')


# AJAX Views for dynamic functionality
@login_required
def update_status(request, pk):
    """AJAX view to update incident status"""
    if request.method == 'POST':
        incident = get_object_or_404(IncidentReport, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(IncidentReport.STATUS_CHOICES):
            old_status = incident.status
            incident.status = new_status
            incident.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Status updated from {old_status} to {new_status}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def add_comment(request, pk):
    """AJAX view to add comment to incident"""
    if request.method == 'POST':
        incident = get_object_or_404(IncidentReport, pk=pk)
        form = IncidentCommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.incident = incident
            comment.author = request.user
            comment.save()
            
            return JsonResponse({
                'success': True,
                'comment': comment.comment,
                'author': comment.author.username,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid form'})
