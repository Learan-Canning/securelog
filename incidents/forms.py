"""
FORMS.PY - Django Forms for User Input and Validation

This file defines forms that handle user input, validation, and data processing.
Django forms provide automatic HTML generation, validation, and security features.

Key Concepts:
- ModelForm: Automatically generates form fields from model fields
- Form Validation: Ensures data integrity before saving to database
- Widget Customization: Controls how form fields appear in HTML
- CSRF Protection: Automatically included for security

Assessment Requirements Met:
- LO2.4: Forms with validation for creating and editing models
- LO1.1: User-friendly interfaces with clear labels and inputs
"""

# === DJANGO IMPORTS ===
from django import forms  # Django's form handling framework
from django.contrib.auth.models import User  # Django's built-in User model

# === LOCAL IMPORTS ===
from .models import IncidentReport, IncidentComment  # Our custom models


class IncidentReportForm(forms.ModelForm):
    """
    MAIN INCIDENT REPORT FORM - Core functionality for incident creation/editing
    
    This ModelForm automatically generates form fields based on the IncidentReport model.
    It handles validation, HTML generation, and data processing for incident reports.
    
    Features:
    - Automatic field generation from model
    - Custom widgets for better user experience
    - Field validation and required field enforcement
    - Bootstrap CSS classes for styling
    - Helpful placeholder text and labels
    
    Security: Django automatically includes CSRF protection
    """
    
    class Meta:
        model = IncidentReport
        fields = [
            'title', 'incident_type', 'description', 'location',
            'date_occurred', 'severity', 'people_involved', 'witnesses',
            'injuries_occurred', 'injury_details',
            'property_damage', 'damage_details',
            'immediate_action_taken', 'attachment'
        ]
        
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe what happened in detail...'
            }),
            'date_occurred': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'injury_details': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe any injuries...'
            }),
            'damage_details': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe any property damage...'
            }),
            'immediate_action_taken': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'What immediate actions were taken?'
            }),
            'people_involved': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Names of people involved...'
            }),
            'witnesses': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Names of witnesses...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add CSS classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # Make certain fields required
        self.fields['title'].required = True
        self.fields['incident_type'].required = True
        self.fields['description'].required = True
        self.fields['location'].required = True
        self.fields['date_occurred'].required = True
        
        # Add help text
        self.fields['severity'].help_text = "How severe was this incident?"
        self.fields['attachment'].help_text = "Upload photos or documents (optional)"


class IncidentCommentForm(forms.ModelForm):
    """Form for adding comments to incident reports"""
    
    class Meta:
        model = IncidentComment
        fields = ['comment']
        
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Add a comment...',
                'class': 'form-control'
            })
        }


class IncidentFilterForm(forms.Form):
    """Form for filtering incident reports"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search incidents...',
            'class': 'form-control'
        })
    )
    
    severity = forms.ChoiceField(
        required=False,
        choices=[('', 'All Severities')] + IncidentReport.SEVERITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + IncidentReport.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class UserRegistrationForm(forms.ModelForm):
    """Registration form for new users"""
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user