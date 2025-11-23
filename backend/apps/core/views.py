from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import json
import os
import csv
from django.conf import settings

from .models import (
    Event, Alert, Asset, LogSource, IOC, ThreatActor, ThreatFeed,
    DetectionRule, Investigation, InvestigationNote, Playbook,
    MitreTactic, MitreTechnique, ComplianceFramework, ComplianceCheck,
    Report, AnomalyDetection, UserBehaviorBaseline, SavedSearch,
    AuditLog, NotificationChannel, NotificationRule, Evidence,
    InvestigationTimeline, PlaybookExecution
)

from .forms import (
    LogUploadForm, UserProfileForm, PasswordChangeForm, InvestigationForm,
    InvestigationNoteForm, AlertActionForm, SavedSearchForm, ReportGenerationForm,
    DetectionRuleForm, AdvancedSearchForm, EvidenceUploadForm
)

from .log_parser import LogParser, ThreatDetector
from .report_generator import ReportGenerator


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        # Validation
        errors = []
        
        if not username:
            errors.append('Username is required.')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        elif User.objects.filter(username=username).exists():
            errors.append('Username already exists.')
        
        if not email:
            errors.append('Email is required.')
        elif User.objects.filter(email=email).exists():
            errors.append('Email already registered.')
        
        if not password:
            errors.append('Password is required.')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        elif password != password_confirm:
            errors.append('Passwords do not match.')
        
        if errors:
            context = {
                'errors': errors,
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
            return render(request, 'registration/register.html', context)
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Log the registration
            AuditLog.objects.create(
                user=user,
                action_type='create',
                resource_type='user',
                resource_id=str(user.id),
                description=f'New user registered: {username}'
            )
            
            # Automatically log the user in
            login(request, user)
            
            messages.success(request, f'Welcome to DERE SIEM, {user.first_name or user.username}!')
            return redirect('dashboard')
            
        except Exception as e:
            errors.append(f'An error occurred during registration: {str(e)}')
            context = {
                'errors': errors,
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
            return render(request, 'registration/register.html', context)
    
    return render(request, 'registration/register.html')


# ============================================================================
# CORE VIEWS
# ============================================================================

def home(request):
    return redirect('dashboard')
    
def index(request):
    """Redirect root to the dashboard."""
    return redirect('dashboard')

def api_home(request):
    """Simple JSON API root for the core app."""
    return JsonResponse({"message": "Welcome to the SIEM API!"})


# ============================================================================
# DASHBOARD
# ============================================================================

@login_required
def dashboard(request):
    """Enhanced SIEM dashboard with real data."""
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    
    # Get real metrics
    total_events = Event.objects.filter(time__gte=last_24h).count()
    critical_alerts = Alert.objects.filter(severity='critical', status__in=['new', 'open']).count()
    high_alerts = Alert.objects.filter(severity='high', status__in=['new', 'open']).count()
    open_investigations = Investigation.objects.filter(status__in=['new', 'open', 'in_progress']).count()
    
    # Top alerts
    top_alerts = Alert.objects.filter(status__in=['new', 'open']).values('name', 'severity').annotate(count=Count('id')).order_by('-count')[:5]
    
    # Recent critical events
    recent_events = Event.objects.all().order_by('-time')[:10]
    
    # Top source IPs
    top_sources_raw = Event.objects.filter(source_ip__isnull=False).values('source_ip').annotate(count=Count('id')).order_by('-count')[:5]
    top_sources = [{'ip': item['source_ip'], 'events': item['count']} for item in top_sources_raw]
    
    # MITRE ATT&CK coverage
    mitre_coverage = MitreTechnique.objects.count()
    
    # Threat intelligence stats
    active_iocs = IOC.objects.filter(is_active=True).count()
    threat_actors = ThreatActor.objects.count()
    
    # Anomalies
    unreviewed_anomalies = AnomalyDetection.objects.filter(is_reviewed=False).count()
    
    # Active alerts (new + open)
    active_alerts = Alert.objects.filter(status__in=['new', 'open']).count()
    
    # Events per minute
    events_per_minute = round(total_events / (24 * 60), 2) if total_events > 0 else 0
    
    # Organize into metrics dictionary for template
    metrics = {
        'events_per_minute': events_per_minute,
        'active_alerts': active_alerts,
        'top_sources': top_sources,
        'recent_events': recent_events,
    }
    
    context = {
        'metrics': metrics,
        'total_events_24h': total_events,
        'events_per_minute': events_per_minute,
        'critical_alerts': critical_alerts,
        'high_alerts': high_alerts,
        'open_investigations': open_investigations,
        'top_alerts': top_alerts,
        'recent_events': recent_events,
        'top_sources': top_sources,
        'mitre_coverage': mitre_coverage,
        'active_iocs': active_iocs,
        'threat_actors': threat_actors,
        'unreviewed_anomalies': unreviewed_anomalies,
    }
    
    return render(request, 'siem/dashboard.html', context)



# ============================================================================
# EVENTS & LOGS
# ============================================================================

@login_required
def events(request):
    """Enhanced events view with advanced filtering."""
    qs = Event.objects.all()
    
    # Filters
    q = request.GET.get('q', '')
    severity = request.GET.get('severity', '')
    category = request.GET.get('category', '')
    source_ip = request.GET.get('source_ip', '')
    username = request.GET.get('username', '')
    time_range = request.GET.get('time_range', '24h')
    
    if q:
        qs = qs.filter(Q(message__icontains=q) | Q(source__icontains=q))
    if severity:
        qs = qs.filter(severity=severity)
    if category:
        qs = qs.filter(category=category)
    if source_ip:
        qs = qs.filter(source_ip=source_ip)
    if username:
        qs = qs.filter(username__icontains=username)
    
    # Time range filter
    now = timezone.now()
    if time_range == '1h':
        qs = qs.filter(time__gte=now - timedelta(hours=1))
    elif time_range == '24h':
        qs = qs.filter(time__gte=now - timedelta(hours=24))
    elif time_range == '7d':
        qs = qs.filter(time__gte=now - timedelta(days=7))
    elif time_range == '30d':
        qs = qs.filter(time__gte=now - timedelta(days=30))
    
    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'q': q,
        'severity': severity,
        'category': category,
        'source_ip': source_ip,
        'username': username,
        'time_range': time_range,
        'severity_choices': Event.SEVERITY_CHOICES,
        'category_choices': Event.EVENT_CATEGORIES,
    }
    
    return render(request, 'siem/events.html', context)


@login_required
def logs_view(request):
    """Log ingestion and management with file upload."""
    upload_form = LogUploadForm()
    upload_success = False
    upload_stats = None
    
    if request.method == 'POST':
        upload_form = LogUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            log_file = request.FILES['log_file']
            log_type = upload_form.cleaned_data['log_type']
            source_name = upload_form.cleaned_data['source_name'] or log_file.name
            
            try:
                # Read file content
                file_content = log_file.read()
                
                # Parse log file
                if log_type == 'auto':
                    log_type = None  # Auto-detect
                
                events = LogParser.parse_file(file_content, log_type)
                
                # Detect threats
                threats = ThreatDetector.detect_threats(events)
                
                # Create or get log source
                log_source, created = LogSource.objects.get_or_create(
                    name=source_name,
                    defaults={
                        'source_type': log_type or 'generic',
                        'host': 'uploaded',
                        'is_active': True,
                    }
                )
                
                # Save events to database
                events_created = 0
                alerts_created = 0
                
                for event_data in events:
                    event = Event.objects.create(
                        time=event_data.get('timestamp', timezone.now()),
                        source=event_data.get('source', source_name),
                        log_source=log_source,
                        message=event_data.get('message', ''),
                        raw_log=event_data.get('raw_log', ''),
                        severity=event_data.get('severity', 'info'),
                        category=event_data.get('category', 'system'),
                        source_ip=event_data.get('source_ip'),
                        dest_ip=event_data.get('dest_ip'),
                        source_port=event_data.get('source_port'),
                        dest_port=event_data.get('dest_port'),
                        username=event_data.get('username', ''),
                        process_name=event_data.get('process_name', ''),
                        protocol=event_data.get('protocol', ''),
                        action=event_data.get('action', ''),
                        result=event_data.get('result', ''),
                    )
                    events_created += 1
                
                
                # Create alerts for detected threats
                for threat in threats:
                    # Use the description from threat detector if available
                    description = threat.get('description', f"Threat detected in uploaded logs")
                    
                    # Add additional context based on threat type
                    if 'source_ip' in threat:
                        description += f" | Source IP: {threat['source_ip']}"
                    if 'failed_attempts' in threat:
                        description += f" | Failed Attempts: {threat['failed_attempts']}"
                    if 'ports_scanned' in threat:
                        description += f" | Ports Scanned: {threat['ports_scanned']}"
                    if 'request_count' in threat:
                        description += f" | Request Count: {threat['request_count']}"
                    if 'tool' in threat:
                        description += f" | Tool: {threat['tool']}"
                    
                    alert = Alert.objects.create(
                        name=f"{threat['type'].replace('_', ' ').title()}",
                        description=description,
                        severity=threat.get('severity', 'medium'),
                        status='new',
                    )
                    
                    # Link related event if available
                    if 'event' in threat:
                        # Find the corresponding saved event
                        related_event = Event.objects.filter(
                            raw_log=threat['event'].get('raw_log')
                        ).first()
                        if related_event:
                            alert.related_events.add(related_event)
                    
                    alerts_created += 1
                
                # Update log source statistics
                log_source.events_received += events_created
                log_source.last_event_time = timezone.now()
                log_source.save()
                
                # Log the upload
                AuditLog.objects.create(
                    user=request.user,
                    action_type='create',
                    resource_type='log_upload',
                    description=f'Uploaded log file: {log_file.name} ({events_created} events, {alerts_created} alerts)'
                )
                
                upload_success = True
                upload_stats = {
                    'file_name': log_file.name,
                    'file_size': log_file.size,
                    'events_created': events_created,
                    'alerts_created': alerts_created,
                    'threats_detected': len(threats),
                    'log_type': log_type or 'auto-detected',
                }
                
                messages.success(
                    request,
                    f'Successfully uploaded {log_file.name}: {events_created} events processed, {alerts_created} alerts created'
                )
                
            except Exception as e:
                messages.error(request, f'Error processing log file: {str(e)}')
    
    log_sources = LogSource.objects.all().order_by('-last_event_time')
    recent_logs = Event.objects.all().order_by('-time')[:50]
    
    context = {
        'log_sources': log_sources,
        'logs': recent_logs,
        'upload_form': upload_form,
        'upload_success': upload_success,
        'upload_stats': upload_stats,
    }
    
    return render(request, 'siem/logs.html', context)


# ============================================================================
# ALERTS
# ============================================================================

@login_required
@require_http_methods(['GET', 'POST'])
def alerts(request):
    """Enhanced alerts view with assignment and actions."""
    if request.method == 'POST':
        alert_id = request.POST.get('alert_id')
        action = request.POST.get('action')
        alert = get_object_or_404(Alert, pk=alert_id)
        
        if action == 'ack':
            alert.status = 'investigating'
            alert.acknowledged_at = timezone.now()
            alert.assigned_to = request.user
            alert.save()
        elif action == 'resolve':
            alert.status = 'resolved'
            alert.resolved_at = timezone.now()
            alert.save()
        elif action == 'close':
            alert.status = 'closed'
            alert.save()
        elif action == 'false_positive':
            alert.status = 'false_positive'
            alert.save()
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action_type='update',
            resource_type='alert',
            resource_id=str(alert.id),
            description=f'Alert {action}: {alert.name}'
        )
        
        return redirect('alerts')
    
    # Filters
    status = request.GET.get('status', '')
    severity = request.GET.get('severity', '')
    
    alerts_qs = Alert.objects.all()
    
    if status:
        alerts_qs = alerts_qs.filter(status=status)
    if severity:
        alerts_qs = alerts_qs.filter(severity=severity)
    
    alerts_qs = alerts_qs.order_by('-first_seen')
    
    paginator = Paginator(alerts_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status': status,
        'severity': severity,
        'status_choices': Alert.STATUS_CHOICES,
        'severity_choices': [('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')],
    }
    
    return render(request, 'siem/alerts.html', context)



@login_required
def alert_detail(request, alert_id):
    """Detailed alert view with AI-powered analysis."""
    alert = get_object_or_404(Alert, pk=alert_id)
    
    # Handle investigation creation
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_investigation':
            # Import here to avoid circular imports
            from .investigation_ai import InvestigationAI
            import uuid
            
            # Generate case ID
            case_id = f"INV-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Get AI analysis for priority
            ai_analysis = InvestigationAI.analyze_alert(alert)
            priority_info = ai_analysis['investigation_priority']
            
            # Map priority level to investigation priority
            priority_map = {
                'P1 - Critical': 'critical',
                'P2 - High': 'high',
                'P3 - Medium': 'medium',
                'P4 - Low': 'low'
            }
            priority = priority_map.get(priority_info['level'], 'medium')
            
            # Create investigation
            investigation = Investigation.objects.create(
                case_id=case_id,
                title=f"Investigation: {alert.name}",
                description=f"Auto-created investigation for alert: {alert.name}\n\n{alert.description}",
                priority=priority,
                severity=alert.severity,
                status='open',
                owner=request.user
            )
            
            # Link alert to investigation
            investigation.alerts.add(alert)
            
            # Link affected assets
            for asset in alert.affected_assets.all():
                investigation.affected_assets.add(asset)
            
            # Link MITRE techniques
            for technique in alert.mitre_techniques.all():
                investigation.mitre_techniques.add(technique)
            
            # Create initial timeline entry
            from .models import InvestigationTimeline
            InvestigationTimeline.objects.create(
                investigation=investigation,
                event_type='investigation_created',
                description=f'Investigation created from alert: {alert.name}',
                user=request.user
            )
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action_type='create',
                resource_type='investigation',
                resource_id=case_id,
                description=f'Created investigation {case_id} from alert {alert.id}'
            )
            
            messages.success(request, f'Investigation {case_id} created successfully!')
            return redirect('investigation_detail', case_id=case_id)
        
        elif action == 'assign_to_me':
            alert.assigned_to = request.user
            alert.status = 'investigating'
            alert.save()
            messages.success(request, 'Alert assigned to you')
            return redirect('alert_detail', alert_id=alert_id)
    
    # Get AI analysis
    from .investigation_ai import InvestigationAI
    ai_analysis = InvestigationAI.analyze_alert(alert)
    
    context = {
        'alert': alert,
        'related_events': alert.related_events.all()[:50],
        'mitre_techniques': alert.mitre_techniques.all(),
        'affected_assets': alert.affected_assets.all(),
        'ai_analysis': ai_analysis,
    }
    
    return render(request, 'siem/alert_detail.html', context)



# ============================================================================
# ASSETS
# ============================================================================

@login_required
def assets(request):
    """Asset inventory view."""
    asset_type = request.GET.get('type', '')
    criticality = request.GET.get('criticality', '')
    
    assets_qs = Asset.objects.all()
    
    if asset_type:
        assets_qs = assets_qs.filter(asset_type=asset_type)
    if criticality:
        assets_qs = assets_qs.filter(criticality=criticality)
    
    context = {
        'assets': assets_qs,
        'asset_type': asset_type,
        'criticality': criticality,
        'asset_types': Asset.ASSET_TYPES,
        'criticality_levels': Asset.CRITICALITY_LEVELS,
    }
    
    return render(request, 'siem/assets.html', context)


# ============================================================================
# THREAT INTELLIGENCE
# ============================================================================

@login_required
def threat_intel(request):
    """Threat intelligence dashboard."""
    iocs = IOC.objects.filter(is_active=True).order_by('-created')[:50]
    threat_actors = ThreatActor.objects.all()
    threat_feeds = ThreatFeed.objects.all()
    
    # IOC statistics
    ioc_stats = {
        'total': IOC.objects.filter(is_active=True).count(),
        'critical': IOC.objects.filter(is_active=True, severity='critical').count(),
        'high': IOC.objects.filter(is_active=True, severity='high').count(),
        'by_type': IOC.objects.filter(is_active=True).values('ioc_type').annotate(count=Count('id')),
    }
    
    context = {
        'iocs': iocs,
        'threat_actors': threat_actors,
        'threat_feeds': threat_feeds,
        'ioc_stats': ioc_stats,
    }
    
    return render(request, 'siem/threat_intel.html', context)


@login_required
def ioc_detail(request, ioc_id):
    """Detailed IOC view."""
    ioc = get_object_or_404(IOC, pk=ioc_id)
    
    # Find related events
    related_events = Event.objects.filter(
        Q(source_ip=ioc.value) | Q(message__icontains=ioc.value)
    ).order_by('-time')[:20]
    
    context = {
        'ioc': ioc,
        'related_events': related_events,
    }
    
    return render(request, 'siem/ioc_detail.html', context)


# ============================================================================
# INVESTIGATIONS & INCIDENT RESPONSE
# ============================================================================

@login_required
def investigations(request):
    """List investigations/cases."""
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    
    inv_qs = Investigation.objects.all()
    
    if status:
        inv_qs = inv_qs.filter(status=status)
    if priority:
        inv_qs = inv_qs.filter(priority=priority)
    
    inv_qs = inv_qs.order_by('-created')
    
    context = {
        'investigations': inv_qs,
        'status': status,
        'priority': priority,
        'status_choices': Investigation.STATUS_CHOICES,
        'priority_choices': Investigation.PRIORITY_CHOICES,
    }
    
    return render(request, 'siem/investigations.html', context)


@login_required
def investigation_detail(request, case_id):
    """Detailed investigation view with AI-powered insights, timeline and notes."""
    investigation = get_object_or_404(Investigation, case_id=case_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_note':
            # Add note
            note_content = request.POST.get('note_content')
            if note_content:
                InvestigationNote.objects.create(
                    investigation=investigation,
                    author=request.user,
                    content=note_content
                )
                messages.success(request, 'Note added successfully')
                return redirect('investigation_detail', case_id=case_id)
        
        elif action == 'update_status':
            # Update investigation status
            new_status = request.POST.get('status')
            if new_status:
                investigation.status = new_status
                if new_status == 'resolved':
                    investigation.resolved_at = timezone.now()
                elif new_status == 'closed':
                    investigation.closed_at = timezone.now()
                investigation.save()
                
                # Add timeline entry
                InvestigationTimeline.objects.create(
                    investigation=investigation,
                    event_type='status_changed',
                    description=f'Status changed to: {new_status}',
                    user=request.user
                )
                
                messages.success(request, f'Investigation status updated to {new_status}')
                return redirect('investigation_detail', case_id=case_id)
    
    # Generate AI-powered investigation report
    from .investigation_ai import InvestigationAI
    ai_report = InvestigationAI.generate_investigation_report(investigation)
    
    # Get AI analysis for each alert
    alert_analyses = []
    for alert in investigation.alerts.all():
        analysis = InvestigationAI.analyze_alert(alert)
        alert_analyses.append({
            'alert': alert,
            'analysis': analysis
        })
    
    context = {
        'inv': investigation,
        'notes': investigation.notes.all().order_by('-created'),
        'timeline': investigation.timeline.all().order_by('-timestamp'),
        'alerts': investigation.alerts.all(),
        'affected_assets': investigation.affected_assets.all(),
        'related_iocs': investigation.related_iocs.all(),
        'mitre_techniques': investigation.mitre_techniques.all(),
        'evidence': investigation.evidence.all(),
        'ai_report': ai_report,
        'alert_analyses': alert_analyses,
    }
    
    return render(request, 'siem/investigation_detail.html', context)



@login_required
def playbooks(request):
    """List incident response playbooks."""
    playbooks_list = Playbook.objects.all()
    
    context = {
        'playbooks': playbooks_list,
    }
    
    return render(request, 'siem/playbooks.html', context)


@login_required
def playbook_detail(request, playbook_id):
    """Detailed playbook view."""
    playbook = get_object_or_404(Playbook, pk=playbook_id)
    
    # Parse steps from JSON
    try:
        steps = json.loads(playbook.steps)
    except:
        steps = []
    
    context = {
        'playbook': playbook,
        'steps': steps,
        'mitre_techniques': playbook.mitre_techniques.all(),
    }
    
    return render(request, 'siem/playbook_detail.html', context)


# ============================================================================
# DETECTION & CORRELATION
# ============================================================================

@login_required
def detection_rules(request):
    """List detection rules."""
    rule_type = request.GET.get('type', '')
    is_enabled = request.GET.get('enabled', '')
    
    rules_qs = DetectionRule.objects.all()
    
    if rule_type:
        rules_qs = rules_qs.filter(rule_type=rule_type)
    if is_enabled:
        rules_qs = rules_qs.filter(is_enabled=(is_enabled == 'true'))
    
    context = {
        'rules': rules_qs,
        'rule_type': rule_type,
        'is_enabled': is_enabled,
        'rule_types': DetectionRule.RULE_TYPES,
    }
    
    return render(request, 'siem/detection_rules.html', context)


@login_required
def rule_detail(request, rule_id):
    """Detailed detection rule view."""
    rule = get_object_or_404(DetectionRule, pk=rule_id)
    
    # Get recent alerts triggered by this rule
    recent_alerts = Alert.objects.filter(detection_rule=rule).order_by('-first_seen')[:10]
    
    context = {
        'rule': rule,
        'recent_alerts': recent_alerts,
        'mitre_techniques': rule.mitre_techniques.all(),
    }
    
    return render(request, 'siem/rule_detail.html', context)


# ============================================================================
# MITRE ATT&CK
# ============================================================================

@login_required
def mitre_attack(request):
    """MITRE ATT&CK framework view."""
    tactics = MitreTactic.objects.all()
    
    # Get techniques grouped by tactic
    tactics_with_techniques = []
    for tactic in tactics:
        techniques = tactic.techniques.all()
        tactics_with_techniques.append({
            'tactic': tactic,
            'techniques': techniques,
        })
    
    context = {
        'tactics_with_techniques': tactics_with_techniques,
    }
    
    return render(request, 'siem/mitre_attack.html', context)


@login_required
def mitre_technique_detail(request, technique_id):
    """Detailed MITRE technique view."""
    technique = get_object_or_404(MitreTechnique, technique_id=technique_id)
    
    # Find related alerts
    related_alerts = Alert.objects.filter(mitre_techniques=technique).order_by('-first_seen')[:10]
    
    # Find related detection rules
    related_rules = DetectionRule.objects.filter(mitre_techniques=technique)
    
    context = {
        'technique': technique,
        'related_alerts': related_alerts,
        'related_rules': related_rules,
    }
    
    return render(request, 'siem/mitre_technique_detail.html', context)


# ============================================================================
# HUNTING
# ============================================================================

@login_required
def hunting(request):
    """Threat hunting interface."""
    saved_queries = SavedSearch.objects.filter(
        Q(owner=request.user) | Q(is_public=True)
    ).order_by('-updated')
    
    # Execute query if provided
    results = []
    query = request.GET.get('query', '')
    
    if query:
        # Simple query execution (in production, use proper query parser)
        results = Event.objects.filter(
            Q(message__icontains=query) | Q(source__icontains=query)
        ).order_by('-time')[:100]
    
    context = {
        'saved_queries': saved_queries,
        'query': query,
        'results': results,
    }
    
    return render(request, 'siem/hunting.html', context)


# ============================================================================
# UEBA (User & Entity Behavior Analytics)
# ============================================================================

@login_required
def ueba(request):
    """UEBA dashboard."""
    anomalies = AnomalyDetection.objects.filter(is_reviewed=False).order_by('-detected_at')[:50]
    baselines = UserBehaviorBaseline.objects.all().order_by('-risk_score')[:20]
    
    # High-risk users
    high_risk_users = UserBehaviorBaseline.objects.filter(risk_score__gte=50).order_by('-risk_score')
    
    context = {
        'anomalies': anomalies,
        'baselines': baselines,
        'high_risk_users': high_risk_users,
    }
    
    return render(request, 'siem/ueba.html', context)


@login_required
def anomaly_detail(request, anomaly_id):
    """Detailed anomaly view."""
    anomaly = get_object_or_404(AnomalyDetection, pk=anomaly_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_reviewed':
            anomaly.is_reviewed = True
            anomaly.save()
        elif action == 'mark_false_positive':
            anomaly.is_false_positive = True
            anomaly.is_reviewed = True
            anomaly.save()
        return redirect('anomaly_detail', anomaly_id=anomaly_id)
    
    context = {
        'anomaly': anomaly,
        'related_events': anomaly.related_events.all()[:20],
    }
    
    return render(request, 'siem/anomaly_detail.html', context)


# ============================================================================
# COMPLIANCE
# ============================================================================

@login_required
def compliance(request):
    """Compliance dashboard."""
    frameworks = ComplianceFramework.objects.filter(is_active=True)
    
    # Get compliance status for each framework
    framework_status = []
    for framework in frameworks:
        checks = ComplianceCheck.objects.filter(framework=framework)
        total_checks = checks.count()
        passed = checks.filter(last_result='pass').count()
        failed = checks.filter(last_result='fail').count()
        
        framework_status.append({
            'framework': framework,
            'total_checks': total_checks,
            'passed': passed,
            'failed': failed,
            'compliance_rate': round((passed / total_checks * 100) if total_checks > 0 else 0, 1),
        })
    
    context = {
        'framework_status': framework_status,
    }
    
    return render(request, 'siem/compliance.html', context)


@login_required
def compliance_framework_detail(request, framework_id):
    """Detailed compliance framework view."""
    framework = get_object_or_404(ComplianceFramework, pk=framework_id)
    checks = ComplianceCheck.objects.filter(framework=framework)
    
    context = {
        'framework': framework,
        'checks': checks,
    }
    
    return render(request, 'siem/compliance_framework_detail.html', context)


# ============================================================================
# REPORTS
# ============================================================================

@login_required
def reports(request):
    """Reports listing and generation."""
    reports_list = Report.objects.all().order_by('-generated_at')
    
    context = {
        'reports': reports_list,
    }
    
    return render(request, 'siem/reports.html', context)


@login_required
def generate_report(request):
    """Generate a new report."""
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        report_format = request.POST.get('format', 'pdf')
        
        # Create report record
        report = Report.objects.create(
            name=f"{dict(Report.REPORT_TYPES).get(report_type, 'Custom')} Report",
            report_type=report_type,
            format=report_format,
            generated_by=request.user,
        )
        
        return redirect('reports')
    
    context = {
        'report_types': Report.REPORT_TYPES,
        'format_choices': Report.FORMAT_CHOICES,
    }
    
    return render(request, 'siem/generate_report.html', context)


# ============================================================================
# SETTINGS & CONFIGURATION
# ============================================================================

@login_required
def settings_view(request):
    """SIEM settings and configuration."""
    notification_channels = NotificationChannel.objects.all()
    notification_rules = NotificationRule.objects.all()
    log_sources = LogSource.objects.all()
    
    context = {
        'notification_channels': notification_channels,
        'notification_rules': notification_rules,
        'log_sources': log_sources,
    }
    
    return render(request, 'siem/settings.html', context)


# ============================================================================
# USER PROFILE & ACCOUNT MANAGEMENT
# ============================================================================

@login_required
def user_profile(request):
    """User profile management."""
    profile_form = UserProfileForm(instance=request.user)
    password_form = PasswordChangeForm()
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                
                # Log the action
                AuditLog.objects.create(
                    user=request.user,
                    action_type='update',
                    resource_type='user_profile',
                    resource_id=str(request.user.id),
                    description='Updated profile information'
                )
                
                messages.success(request, 'Profile updated successfully!')
                return redirect('user_profile')
        
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.POST)
            if password_form.is_valid():
                current_password = password_form.cleaned_data['current_password']
                new_password = password_form.cleaned_data['new_password']
                
                # Verify current password
                if request.user.check_password(current_password):
                    request.user.set_password(new_password)
                    request.user.save()
                    
                    # Update session to prevent logout
                    update_session_auth_hash(request, request.user)
                    
                    # Log the action
                    AuditLog.objects.create(
                        user=request.user,
                        action_type='update',
                        resource_type='user_password',
                        resource_id=str(request.user.id),
                        description='Changed password'
                    )
                    
                    messages.success(request, 'Password changed successfully!')
                    return redirect('user_profile')
                else:
                    messages.error(request, 'Current password is incorrect.')
    
    # Get user activity stats
    user_logins = AuditLog.objects.filter(
        user=request.user,
        action_type='login'
    ).count()
    
    user_actions = AuditLog.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:20]
    
    investigations_owned = Investigation.objects.filter(owner=request.user).count()
    alerts_assigned = Alert.objects.filter(assigned_to=request.user).count()
    
    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'user_logins': user_logins,
        'user_actions': user_actions,
        'investigations_owned': investigations_owned,
        'alerts_assigned': alerts_assigned,
    }
    
    return render(request, 'siem/user_profile.html', context)


# ============================================================================
# ENHANCED REPORT GENERATION
# ============================================================================

@login_required
def generate_report_view(request):
    """Enhanced report generation with multiple formats."""
    form = ReportGenerationForm()
    
    if request.method == 'POST':
        form = ReportGenerationForm(request.POST)
        if form.is_valid():
            report_type = form.cleaned_data['report_type']
            format_type = form.cleaned_data['format']
            start_date = form.cleaned_data.get('time_range_start')
            end_date = form.cleaned_data.get('time_range_end')
            
            # Generate report data based on type
            if report_type == 'security_summary':
                report_data = ReportGenerator.generate_security_summary(start_date, end_date)
            elif report_type == 'incident_response':
                report_data = ReportGenerator.generate_incident_response_report()
            elif report_type == 'threat_intelligence':
                report_data = ReportGenerator.generate_threat_intelligence_report()
            elif report_type == 'compliance':
                report_data = ReportGenerator.generate_compliance_report()
            elif report_type == 'user_activity':
                report_data = ReportGenerator.generate_user_activity_report()
            elif report_type == 'asset_inventory':
                report_data = ReportGenerator.generate_asset_inventory_report()
            else:
                report_data = {'report_type': 'Custom', 'data': 'No data available'}
            
            # Export in requested format
            if format_type == 'json':
                content = ReportGenerator.export_to_json(report_data)
                content_type = 'application/json'
                file_extension = 'json'
            elif format_type == 'csv':
                content = ReportGenerator.export_to_csv(report_data)
                content_type = 'text/csv'
                file_extension = 'csv'
            elif format_type == 'html':
                content = ReportGenerator.export_to_html(report_data)
                content_type = 'text/html'
                file_extension = 'html'
            else:
                # Default to JSON
                content = ReportGenerator.export_to_json(report_data)
                content_type = 'application/json'
                file_extension = 'json'
            
            # Create report record
            report = Report.objects.create(
                name=f"{dict(Report.REPORT_TYPES).get(report_type, 'Custom')} Report",
                report_type=report_type,
                format=format_type,
                generated_by=request.user,
                time_range_start=start_date,
                time_range_end=end_date,
            )
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action_type='create',
                resource_type='report',
                resource_id=str(report.id),
                description=f'Generated {report_type} report in {format_type} format'
            )
            
            # Return file download
            response = HttpResponse(content, content_type=content_type)
            filename = f"{report_type}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
    
    context = {
        'form': form,
    }
    
    return render(request, 'siem/generate_report.html', context)


# ============================================================================
# ADVANCED SEARCH
# ============================================================================

@login_required
def advanced_search(request):
    """Advanced search across all SIEM data."""
    form = AdvancedSearchForm(request.GET or None)
    results = []
    search_performed = False
    
    if form.is_valid() and request.GET:
        search_performed = True
        query = form.cleaned_data.get('query', '')
        
        # Search across multiple models
        if query:
            # Search events
            event_results = Event.objects.filter(
                Q(message__icontains=query) |
                Q(source__icontains=query) |
                Q(username__icontains=query)
            )[:50]
            
            # Search alerts
            alert_results = Alert.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )[:50]
            
            # Search investigations
            investigation_results = Investigation.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(case_id__icontains=query)
            )[:50]
            
            # Search IOCs
            ioc_results = IOC.objects.filter(
                Q(value__icontains=query) |
                Q(description__icontains=query)
            )[:50]
            
            results = {
                'events': event_results,
                'alerts': alert_results,
                'investigations': investigation_results,
                'iocs': ioc_results,
            }
    
    context = {
        'form': form,
        'results': results,
        'search_performed': search_performed,
    }
    
    return render(request, 'siem/advanced_search.html', context)


# ============================================================================
# INVESTIGATION CREATION & MANAGEMENT
# ============================================================================

@login_required
def create_investigation(request):
    """Create a new investigation."""
    form = InvestigationForm()
    
    if request.method == 'POST':
        form = InvestigationForm(request.POST)
        if form.is_valid():
            investigation = form.save(commit=False)
            
            # Generate case ID
            import random
            import string
            case_id = f"INV-{timezone.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}"
            investigation.case_id = case_id
            investigation.owner = request.user
            investigation.status = 'new'
            investigation.save()
            
            # Create timeline entry
            InvestigationTimeline.objects.create(
                investigation=investigation,
                event_type='created',
                description=f'Investigation created by {request.user.username}',
                user=request.user
            )
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action_type='create',
                resource_type='investigation',
                resource_id=case_id,
                description=f'Created investigation: {investigation.title}'
            )
            
            messages.success(request, f'Investigation {case_id} created successfully!')
            return redirect('investigation_detail', case_id=case_id)
    
    context = {
        'form': form,
    }
    
    return render(request, 'siem/create_investigation.html', context)


# ============================================================================
# EXPORT FUNCTIONALITY
# ============================================================================

@login_required
def export_events(request):
    """Export events to CSV."""
    # Get filter parameters
    severity = request.GET.get('severity', '')
    category = request.GET.get('category', '')
    time_range = request.GET.get('time_range', '24h')
    
    # Build query
    qs = Event.objects.all()
    
    if severity:
        qs = qs.filter(severity=severity)
    if category:
        qs = qs.filter(category=category)
    
    # Time range filter
    now = timezone.now()
    if time_range == '1h':
        qs = qs.filter(time__gte=now - timedelta(hours=1))
    elif time_range == '24h':
        qs = qs.filter(time__gte=now - timedelta(hours=24))
    elif time_range == '7d':
        qs = qs.filter(time__gte=now - timedelta(days=7))
    
    # Create CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="events_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Time', 'Source', 'Severity', 'Category', 'Message', 'Source IP', 'Username'])
    
    for event in qs[:1000]:  # Limit to 1000 events
        writer.writerow([
            event.time,
            event.source,
            event.severity,
            event.category,
            event.message,
            event.source_ip or '',
            event.username or '',
        ])
    
    # Log the export
    AuditLog.objects.create(
        user=request.user,
        action_type='export',
        resource_type='events',
        description=f'Exported {qs.count()} events to CSV'
    )
    
    return response


# ============================================================================
# API ENDPOINTS
# ============================================================================

@login_required
def api_events(request):
    """API endpoint for events data."""
    time_range = request.GET.get('range', '24h')
    
    now = timezone.now()
    if time_range == '1h':
        start_time = now - timedelta(hours=1)
    elif time_range == '24h':
        start_time = now - timedelta(hours=24)
    elif time_range == '7d':
        start_time = now - timedelta(days=7)
    else:
        start_time = now - timedelta(hours=24)
    
    events = Event.objects.filter(time__gte=start_time).values('time', 'severity', 'category')
    
    return JsonResponse(list(events), safe=False)


@login_required
def api_alerts_stats(request):
    """API endpoint for alert statistics."""
    stats = {
        'by_severity': list(Alert.objects.values('severity').annotate(count=Count('id'))),
        'by_status': list(Alert.objects.values('status').annotate(count=Count('id'))),
        'total': Alert.objects.count(),
    }
    
    return JsonResponse(stats)


@login_required
def api_threat_map(request):
    """API endpoint for threat map data."""
    # Get events with geolocation
    events = Event.objects.filter(
        source_geo_lat__isnull=False,
        source_geo_lon__isnull=False
    ).values('source_geo_lat', 'source_geo_lon', 'severity', 'source_ip')[:100]
    
    return JsonResponse(list(events), safe=False)