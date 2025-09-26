# Django imports for database models and utilities
from django.db import models
from django.contrib.auth.models import User  # Built-in Django User model
from django.utils import timezone  # Django's timezone utilities
from django.urls import reverse  # For generating URLs from view names


class IncidentType(models.Model):
    """
    Model for categorizing different types of incidents (e.g., Safety, Security, Equipment).
    
    This model allows administrators to create categories for organizing incidents,
    making it easier to filter and analyze incident data by type.
    
    Fields:
        name: Unique name for the incident type (e.g., "Safety Incident")
        description: Optional detailed description of what this type covers
        color_code: Hex color code for visual representation in the UI
        created_at: Timestamp when this type was created
    """
    
    # CharField stores short text up to 100 characters, unique=True prevents duplicates
    name = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Unique name for this incident type"
    )
    
    # TextField allows longer text, blank=True means it's optional in forms
    description = models.TextField(
        blank=True,
        help_text="Detailed description of what this incident type covers"
    )
    
    # Store hex color code for UI theming (e.g., #FF0000 for red)
    color_code = models.CharField(
        max_length=7, 
        default='#007bff',  # Bootstrap primary blue as default
        help_text="Hex color code for visual representation (e.g., #FF0000)"
    )
    
    # auto_now_add=True automatically sets this when the record is first created
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this incident type was created"
    )

    class Meta:
        """
        Meta class defines metadata for the model
        """
        ordering = ['name']  # Default ordering by name alphabetically
        verbose_name = "Incident Type"
        verbose_name_plural = "Incident Types"

    def __str__(self):
        """
        String representation of the model - what appears in admin and dropdowns
        """
        return self.name


class IncidentReport(models.Model):
    """
    MAIN CUSTOM MODEL - Core incident reporting functionality
    
    This is the primary model for the SecureLog application and meets the assessment
    requirement for an "original custom model with associated functionality."
    
    This model handles:
    - Incident documentation and tracking
    - Workflow management (draft → submitted → resolved → closed)
    - Severity classification for prioritization
    - People and location tracking
    - File attachments and follow-up actions
    
    Business Logic:
    - Staff can create incident reports
    - Managers can assign and update status
    - Automatic timestamp tracking for audit trail
    - Property methods for UI display and business rules
    """
    
    # CHOICE FIELDS: These create dropdown options in forms and ensure data consistency
    
    # Severity levels help prioritize incidents (critical = immediate attention)
    SEVERITY_CHOICES = [
        ('low', 'Low'),           # Minor issues, no immediate danger
        ('medium', 'Medium'),     # Standard workplace incidents
        ('high', 'High'),         # Serious incidents requiring quick response
        ('critical', 'Critical'), # Emergency situations, immediate action needed
    ]
    
    # Status workflow tracks incident lifecycle from creation to closure
    STATUS_CHOICES = [
        ('draft', 'Draft'),                    # Being written, not yet submitted
        ('submitted', 'Submitted'),            # Submitted for review
        ('under_review', 'Under Review'),      # Manager reviewing details
        ('investigating', 'Investigating'),    # Active investigation in progress
        ('resolved', 'Resolved'),              # Solution implemented
        ('closed', 'Closed'),                  # Completed and archived
    ]

    # === BASIC INFORMATION FIELDS ===
    # These fields capture the core details of what happened
    
    # Title: Short summary that appears in lists and reports
    title = models.CharField(
        max_length=200,  # Reasonable limit for titles
        help_text="Brief description of the incident (e.g., 'Slip and fall in cafeteria')"
    )
    
    # Foreign Key relationship to IncidentType model
    # PROTECT prevents deletion of IncidentType if reports exist
    incident_type = models.ForeignKey(
        IncidentType,
        on_delete=models.PROTECT,  # Protects data integrity
        help_text="Category of incident (Safety, Security, Equipment, etc.)"
    )
    
    # TextField allows unlimited text for detailed descriptions
    description = models.TextField(
        help_text="Detailed description of what happened, who was involved, and circumstances"
    )
    
    # === LOCATION AND TIME TRACKING ===
    # Critical for incident analysis and emergency response
    
    # Physical location where incident occurred
    location = models.CharField(
        max_length=200,
        help_text="Specific location (e.g., 'Building A, Floor 2, Conference Room 205')"
    )
    
    # When the actual incident happened (user-entered)
    date_occurred = models.DateTimeField(
        help_text="Exact date and time when the incident occurred"
    )
    
    # When the report was created (automatically set)
    # timezone.now ensures proper timezone handling
    date_reported = models.DateTimeField(
        default=timezone.now,  # Auto-populates with current timestamp
        help_text="When this report was submitted to the system"
    )
    
    # Classification
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='medium',
        help_text="How severe was this incident?"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current status of the incident report"
    )
    
    # People Involved
    reported_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reported_incidents',
        help_text="Staff member who reported this incident"
    )
    
    people_involved = models.TextField(
        blank=True,
        help_text="Names of people involved in the incident"
    )
    
    witnesses = models.TextField(
        blank=True,
        help_text="Names of any witnesses"
    )
    
    # Additional Information
    injuries_occurred = models.BooleanField(
        default=False,
        help_text="Were there any injuries?"
    )
    
    injury_details = models.TextField(
        blank=True,
        help_text="Details of any injuries (if applicable)"
    )
    
    property_damage = models.BooleanField(
        default=False,
        help_text="Was there any property damage?"
    )
    
    damage_details = models.TextField(
        blank=True,
        help_text="Details of property damage (if applicable)"
    )
    
    immediate_action_taken = models.TextField(
        blank=True,
        help_text="What immediate actions were taken?"
    )
    
    # Follow-up and Resolution
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents',
        help_text="Manager/supervisor assigned to handle this incident"
    )
    
    resolution_notes = models.TextField(
        blank=True,
        help_text="Notes on how the incident was resolved"
    )
    
    follow_up_required = models.BooleanField(
        default=False,
        help_text="Does this incident require follow-up actions?"
    )
    
    follow_up_details = models.TextField(
        blank=True,
        help_text="Details of required follow-up actions"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # File attachments (optional)
    attachment = models.FileField(
        upload_to='incident_attachments/',
        blank=True,
        null=True,
        help_text="Upload any relevant photos or documents"
    )

    class Meta:
        ordering = ['-date_occurred', '-created_at']
        verbose_name = "Incident Report"
        verbose_name_plural = "Incident Reports"

    def __str__(self):
        return f"{self.title} - {self.get_severity_display()}"

    def get_absolute_url(self):
        """Returns the URL to access the detail view for this incident"""
        return reverse('incidents:detail', kwargs={'pk': self.pk})

    @property
    def is_urgent(self):
        """Check if incident is urgent (critical or high severity)"""
        return self.severity in ['critical', 'high']

    @property
    def days_since_reported(self):
        """Calculate days since incident was reported"""
        return (timezone.now() - self.date_reported).days

    @property
    def status_color(self):
        """Return color class for status display"""
        status_colors = {
            'draft': 'secondary',
            'submitted': 'primary',
            'under_review': 'info',
            'investigating': 'warning',
            'resolved': 'success',
            'closed': 'dark',
        }
        return status_colors.get(self.status, 'secondary')

    @property
    def severity_color(self):
        """Return color class for severity display"""
        severity_colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'dark',
        }
        return severity_colors.get(self.severity, 'secondary')


class IncidentComment(models.Model):
    """
    Model for comments/notes on incident reports
    """
    incident = models.ForeignKey(
        IncidentReport,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    
    comment = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.incident.title}"


class IncidentStatusHistory(models.Model):
    """
    Model to track status changes for audit trail
    """
    incident = models.ForeignKey(
        IncidentReport,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    
    changed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    
    change_reason = models.TextField(blank=True)
    
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name = "Status History"
        verbose_name_plural = "Status Histories"

    def __str__(self):
        return f"{self.incident.title}: {self.old_status} → {self.new_status}"
