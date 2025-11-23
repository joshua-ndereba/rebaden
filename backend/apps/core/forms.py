"""
Forms for SIEM Application
"""

from django import forms
from django.contrib.auth.models import User
from .models import (
    Investigation, InvestigationNote, Alert, DetectionRule,
    SavedSearch, Report, Evidence, Playbook
)


class LogUploadForm(forms.Form):
    """Form for uploading log files"""
    log_file = forms.FileField(
        label='Log File',
        help_text='Upload log files (max 10MB). Supported formats: .log, .txt, .csv',
        widget=forms.FileInput(attrs={
            'accept': '.log,.txt,.csv',
            'class': 'input'
        })
    )
    log_type = forms.ChoiceField(
        label='Log Type',
        choices=[
            ('auto', 'Auto-detect'),
            ('syslog', 'Syslog'),
            ('apache', 'Apache'),
            ('nginx', 'Nginx'),
            ('windows_event', 'Windows Event Log'),
            ('firewall', 'Firewall'),
            ('auth', 'Authentication Log'),
            ('generic', 'Generic'),
        ],
        initial='auto',
        widget=forms.Select(attrs={'class': 'input'})
    )
    source_name = forms.CharField(
        label='Source Name',
        max_length=128,
        required=False,
        help_text='Optional: Name for this log source',
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'e.g., Web Server 01'})
    )


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
        }


class PasswordChangeForm(forms.Form):
    """Form for changing password"""
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input'}),
        label='Current Password'
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input'}),
        label='New Password',
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input'}),
        label='Confirm New Password'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('New passwords do not match')
        
        return cleaned_data


class InvestigationForm(forms.ModelForm):
    """Form for creating/editing investigations"""
    class Meta:
        model = Investigation
        fields = ['title', 'description', 'priority', 'severity', 'assigned_team']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'input', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'input'}),
            'severity': forms.Select(attrs={'class': 'input'}),
            'assigned_team': forms.TextInput(attrs={'class': 'input'}),
        }


class InvestigationNoteForm(forms.ModelForm):
    """Form for adding investigation notes"""
    class Meta:
        model = InvestigationNote
        fields = ['content', 'is_important']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'input', 'rows': 3, 'placeholder': 'Add your note here...'}),
            'is_important': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }


class AlertActionForm(forms.Form):
    """Form for alert actions"""
    action = forms.ChoiceField(
        choices=[
            ('acknowledge', 'Acknowledge'),
            ('investigate', 'Start Investigation'),
            ('resolve', 'Resolve'),
            ('false_positive', 'Mark as False Positive'),
            ('close', 'Close'),
        ],
        widget=forms.Select(attrs={'class': 'input'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'input', 'rows': 2, 'placeholder': 'Optional notes...'})
    )


class SavedSearchForm(forms.ModelForm):
    """Form for saving search queries"""
    class Meta:
        model = SavedSearch
        fields = ['name', 'description', 'query', 'query_type', 'is_public', 'tags']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'input', 'rows': 2}),
            'query': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
            'query_type': forms.Select(attrs={'class': 'input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'tags': forms.TextInput(attrs={'class': 'input', 'placeholder': 'comma, separated, tags'}),
        }


class ReportGenerationForm(forms.Form):
    """Form for generating reports"""
    report_type = forms.ChoiceField(
        label='Report Type',
        choices=Report.REPORT_TYPES,
        widget=forms.Select(attrs={'class': 'input'})
    )
    format = forms.ChoiceField(
        label='Format',
        choices=Report.FORMAT_CHOICES,
        initial='pdf',
        widget=forms.Select(attrs={'class': 'input'})
    )
    time_range_start = forms.DateTimeField(
        label='Start Date',
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'input', 'type': 'datetime-local'})
    )
    time_range_end = forms.DateTimeField(
        label='End Date',
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'input', 'type': 'datetime-local'})
    )
    include_charts = forms.BooleanField(
        label='Include Charts',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'})
    )


class DetectionRuleForm(forms.ModelForm):
    """Form for creating/editing detection rules"""
    class Meta:
        model = DetectionRule
        fields = ['name', 'description', 'rule_type', 'severity', 'rule_logic', 
                  'threshold_value', 'time_window', 'is_enabled', 'false_positive_rate', 'tags']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
            'rule_type': forms.Select(attrs={'class': 'input'}),
            'severity': forms.Select(attrs={'class': 'input'}),
            'rule_logic': forms.Textarea(attrs={'class': 'input', 'rows': 4, 'placeholder': 'Enter rule logic...'}),
            'threshold_value': forms.NumberInput(attrs={'class': 'input'}),
            'time_window': forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Seconds'}),
            'is_enabled': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'false_positive_rate': forms.Select(attrs={'class': 'input'}),
            'tags': forms.TextInput(attrs={'class': 'input'}),
        }


class AdvancedSearchForm(forms.Form):
    """Form for advanced event search"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Search events...'})
    )
    severity = forms.MultipleChoiceField(
        required=False,
        choices=[('info', 'Info'), ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
        widget=forms.CheckboxSelectMultiple()
    )
    category = forms.MultipleChoiceField(
        required=False,
        choices=[
            ('authentication', 'Authentication'),
            ('network', 'Network'),
            ('malware', 'Malware'),
            ('data_access', 'Data Access'),
            ('system', 'System'),
            ('application', 'Application'),
            ('threat', 'Threat'),
        ],
        widget=forms.CheckboxSelectMultiple()
    )
    source_ip = forms.GenericIPAddressField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': '192.168.1.1'})
    )
    time_range = forms.ChoiceField(
        required=False,
        choices=[
            ('1h', 'Last Hour'),
            ('24h', 'Last 24 Hours'),
            ('7d', 'Last 7 Days'),
            ('30d', 'Last 30 Days'),
            ('custom', 'Custom Range'),
        ],
        widget=forms.Select(attrs={'class': 'input'})
    )


class EvidenceUploadForm(forms.ModelForm):
    """Form for uploading evidence to investigations"""
    file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'input'})
    )
    
    class Meta:
        model = Evidence
        fields = ['evidence_type', 'name', 'description']
        widgets = {
            'evidence_type': forms.Select(attrs={'class': 'input'}),
            'name': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
        }
