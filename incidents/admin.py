from django.contrib import admin
from .models import IncidentType, IncidentReport, IncidentComment, IncidentStatusHistory


@admin.register(IncidentType)
class IncidentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_code', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'incident_type', 'severity', 'status', 
        'reported_by', 'date_occurred', 'created_at'
    )
    list_filter = (
        'severity', 'status', 'incident_type', 
        'injuries_occurred', 'property_damage', 'created_at'
    )
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at', 'date_reported')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'incident_type', 'description')
        }),
        ('When and Where', {
            'fields': ('date_occurred', 'date_reported', 'location')
        }),
        ('Classification', {
            'fields': ('severity', 'status')
        }),
        ('People Involved', {
            'fields': ('reported_by', 'people_involved', 'witnesses', 'assigned_to')
        }),
        ('Incident Details', {
            'fields': (
                'injuries_occurred', 'injury_details',
                'property_damage', 'damage_details',
                'immediate_action_taken'
            )
        }),
        ('Follow-up', {
            'fields': (
                'follow_up_required', 'follow_up_details',
                'resolution_notes'
            )
        }),
        ('Attachments', {
            'fields': ('attachment',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(IncidentComment)
class IncidentCommentAdmin(admin.ModelAdmin):
    list_display = ('incident', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('comment', 'incident__title')


@admin.register(IncidentStatusHistory)
class IncidentStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('incident', 'old_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('old_status', 'new_status', 'changed_at')
    search_fields = ('incident__title', 'change_reason')
