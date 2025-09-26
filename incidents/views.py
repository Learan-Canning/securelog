from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q, Count
from .models import IncidentReport, IncidentType, IncidentComment
from .forms import IncidentReportForm, IncidentCommentForm


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard showing incident statistics and recent reports"""
    template_name = 'incidents/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get statistics for dashboard
        context['total_incidents'] = IncidentReport.objects.count()
        context['urgent_incidents'] = IncidentReport.objects.filter(
            severity__in=['high', 'critical']
        ).count()
        context['my_incidents'] = IncidentReport.objects.filter(
            reported_by=self.request.user
        ).count()
        context['pending_incidents'] = IncidentReport.objects.filter(
            status__in=['submitted', 'under_review']
        ).count()
        
        # Recent incidents
        context['recent_incidents'] = IncidentReport.objects.all()[:5]
        
        return context


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
