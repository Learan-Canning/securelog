from django.urls import path
from . import views

app_name = 'incidents'

urlpatterns = [
    # Main pages
    path('', views.IncidentListView.as_view(), name='list'),
    path('create/', views.IncidentCreateView.as_view(), name='create'),
    path('<int:pk>/', views.IncidentDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.IncidentUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.IncidentDeleteView.as_view(), name='delete'),
    
    # Dashboard and filtering
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('my-reports/', views.MyReportsView.as_view(), name='my_reports'),
    
    # AJAX endpoints for dynamic functionality
    path('ajax/update-status/<int:pk>/', views.update_status, name='update_status'),
    path('ajax/add-comment/<int:pk>/', views.add_comment, name='add_comment'),
]