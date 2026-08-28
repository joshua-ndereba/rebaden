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
    InvestigationTimeline, PlaybookExecution, UserProfile, SystemSettings
)

from .forms import (
    LogUploadForm, UserProfileForm, PasswordChangeForm, InvestigationForm,
    InvestigationNoteForm, AlertActionForm, SavedSearchForm, ReportGenerationForm,
    DetectionRuleForm, AdvancedSearchForm, EvidenceUploadForm
)

from .investigation_ai import InvestigationAI

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
    """Enhanced SIEM dashboard with real data and interactive analysis."""
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    # Core metrics (all time to reflect uploaded logs)
    total_events_alltime = Event.objects.count()
    
    active_alerts = Alert.objects.exclude(status__in=['closed', 'resolved', 'false_positive']).count()
    critical_alerts = Alert.objects.filter(severity='critical').exclude(status__in=['closed', 'resolved', 'false_positive']).count()
    high_alerts = Alert.objects.filter(severity='high').exclude(status__in=['closed', 'resolved', 'false_positive']).count()
    open_investigations = Investigation.objects.exclude(status__in=['closed', 'resolved']).count()

    # Event analysis by category instead of event_type
    event_categories = Event.objects.values('category').annotate(count=Count('id')).order_by('-count')[:8]

    # Time-based analysis for charts (last 7 days of alerts)
    alert_trends = []
    for i in range(7):
        day_start = now - timedelta(days=i+1)
        day_end = now - timedelta(days=i)
        count = Alert.objects.filter(first_seen__gte=day_start, first_seen__lt=day_end).count()
        alert_trends.append({
            'day': day_start.strftime('%m/%d'),
            'count': count
        })
    alert_trends.reverse()

    # Top alerts with analysis
    top_alerts = Alert.objects.exclude(status__in=['closed', 'resolved', 'false_positive']).values(
        'name', 'severity'
    ).annotate(count=Count('id')).order_by('-count')[:8]

    # Recent critical/high security events
    recent_events = Event.objects.select_related('log_source', 'asset').prefetch_related('alert_set').filter(severity__in=['critical', 'high']).order_by('-time')[:15]
    if not recent_events.exists():
        # Fall back to any events if no critical/high
        recent_events = Event.objects.select_related('log_source', 'asset').prefetch_related('alert_set').order_by('-time')[:15]

    # AI insights and correlations
    ai_insights = InvestigationAI.generate_dashboard_insights(last_24h)

    # Alerts by severity for charting (all alerts to show full history)
    alerts_by_severity = Alert.objects.values('severity').annotate(
        count=Count('id')
    ).order_by('severity')

    # Organize into comprehensive metrics dictionary
    metrics = {
        'active_alerts': active_alerts,
        'recent_events': recent_events,
        'event_types': list(event_categories),
        'alert_trends': alert_trends,
        'alerts_by_severity': list(alerts_by_severity),
    }

    context = {
        'metrics': metrics,
        'total_events_alltime': total_events_alltime,
        'active_alerts': active_alerts,
        'critical_alerts': critical_alerts,
        'high_alerts': high_alerts,
        'open_investigations': open_investigations,
        'top_alerts': top_alerts,
        'recent_events': recent_events,
        'ai_insights': ai_insights,
        'event_types': list(event_categories),
        'alerts_by_severity': list(alerts_by_severity),
        
        # JSON serialized data for JavaScript charts
        'alerts_by_severity_json': json.dumps(list(alerts_by_severity)),
        'event_types_json': json.dumps(list(event_categories)),
        'alert_trends_json': json.dumps(alert_trends),
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
    """Log file import — supports multiple files per upload."""
    upload_success = False
    upload_stats = None

    if request.method == 'POST':
        # Handle reprocessing an existing log source
        if request.POST.get('action') == 'reprocess':
            source_id = request.POST.get('source_id')
            log_source = get_object_or_404(LogSource, pk=source_id)
            events = list(log_source.event_set.all())
            if not events:
                messages.warning(request, f'No events found for "{log_source.name}".')
            else:
                # Build lightweight event-data dicts for ThreatDetector
                event_data_list = [
                    {
                        'source_ip': e.source_ip,
                        'message': e.message,
                        'raw_log': e.raw_log,
                        'event_type': e.event_type,
                        'severity': e.severity,
                    }
                    for e in events
                ]
                threats = ThreatDetector.detect_threats(event_data_list)
                alerts_created = 0
                for threat in threats:
                    description = threat.get('description', 'Threat re-detected from existing events')
                    if 'source_ip' in threat:
                        description += f" | Source IP: {threat['source_ip']}"
                    Alert.objects.create(
                        name=f"{threat['type'].replace('_', ' ').title()} (re-scan)",
                        description=description,
                        severity=threat.get('severity', 'medium'),
                        status='new',
                    )
                    alerts_created += 1
                AuditLog.objects.create(
                    user=request.user,
                    action_type='create',
                    resource_type='log_reprocess',
                    description=f'Re-processed log source: {log_source.name} — {alerts_created} new alerts'
                )
                messages.success(
                    request,
                    f'Re-processed "{log_source.name}": {len(events)} events analysed, {alerts_created} new alerts created.'
                )
            return redirect('logs')

        log_files = request.FILES.getlist('log_file')
        log_type = request.POST.get('log_type', 'auto')
        source_name_base = request.POST.get('source_name', '').strip()

        if not log_files:
            messages.error(request, 'Please select at least one log file.')
        else:
            total_events = 0
            total_alerts = 0
            total_threats = 0
            file_names = []

            for log_file in log_files:
                source_name = source_name_base or log_file.name
                effective_log_type = None if log_type == 'auto' else log_type

                try:
                    file_content = log_file.read()
                    events = LogParser.parse_file(file_content, effective_log_type)
                    threats = ThreatDetector.detect_threats(events)

                    log_source, _ = LogSource.objects.get_or_create(
                        name=source_name,
                        defaults={
                            'source_type': effective_log_type or 'generic',
                            'host': 'uploaded',
                            'is_active': True,
                        }
                    )

                    events_created = 0
                    alerts_created = 0

                    for event_data in events:
                        Event.objects.create(
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

                    for threat in threats:
                        description = threat.get('description', 'Threat detected in uploaded logs')
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
                        if 'event' in threat:
                            related_event = Event.objects.filter(
                                raw_log=threat['event'].get('raw_log')
                            ).first()
                            if related_event:
                                alert.related_events.add(related_event)
                        alerts_created += 1

                    log_source.events_received += events_created
                    log_source.last_event_time = timezone.now()
                    log_source.save()

                    AuditLog.objects.create(
                        user=request.user,
                        action_type='create',
                        resource_type='log_upload',
                        description=f'Uploaded log file: {log_file.name} ({events_created} events, {alerts_created} alerts)'
                    )

                    total_events += events_created
                    total_alerts += alerts_created
                    total_threats += len(threats)
                    file_names.append(log_file.name)

                except Exception as e:
                    messages.error(request, f'Error processing {log_file.name}: {str(e)}')

            if file_names:
                upload_success = True
                files_label = ', '.join(file_names) if len(file_names) <= 3 else f'{len(file_names)} files'
                upload_stats = {
                    'file_name': files_label,
                    'events_created': total_events,
                    'alerts_created': total_alerts,
                    'threats_detected': total_threats,
                    'log_type': log_type,
                }
                messages.success(
                    request,
                    f'Imported {len(file_names)} file(s): {total_events} events, {total_alerts} alerts, {total_threats} threats detected.'
                )
    
    log_sources = LogSource.objects.all().order_by('-last_event_time')
    recent_logs = Event.objects.all().order_by('-time')[:50]
    
    context = {
        'log_sources': log_sources,
        'logs': recent_logs,
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
    new_count = Alert.objects.filter(status='new').count()
    
    paginator = Paginator(alerts_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status': status,
        'severity': severity,
        'new_count': new_count,
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
    """Asset inventory view — pure information, no log loading."""
    if request.method == 'POST':
        hostname = request.POST.get('hostname', '').strip()
        ip = request.POST.get('ip', '').strip()
        asset_type = request.POST.get('asset_type', 'server')
        os_name = request.POST.get('os', '').strip()
        owner = request.POST.get('owner', '').strip()
        department = request.POST.get('department', '').strip()
        criticality = request.POST.get('criticality', 'medium')
        location = request.POST.get('location', '').strip()

        if hostname and ip:
            try:
                Asset.objects.create(
                    hostname=hostname,
                    ip=ip,
                    asset_type=asset_type,
                    os=os_name,
                    owner=owner,
                    department=department,
                    criticality=criticality,
                    location=location,
                    is_active=True,
                )
                AuditLog.objects.create(
                    user=request.user,
                    action_type='create',
                    resource_type='asset',
                    description=f'Added asset: {hostname} ({ip})'
                )
                messages.success(request, f'Asset "{hostname}" added successfully.')
            except Exception as e:
                messages.error(request, f'Error adding asset: {str(e)}')
        else:
            messages.error(request, 'Hostname and IP address are required.')
        return redirect('assets')

    asset_type = request.GET.get('type', '')
    criticality = request.GET.get('criticality', '')

    assets_qs = Asset.objects.annotate(
        alert_count=Count('alert', distinct=True)
    ).all()

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
    """List investigations/cases with tab-based filtering."""
    tab = request.GET.get('tab', 'ongoing')  # 'ongoing', 'closed', 'all'
    priority = request.GET.get('priority', '')

    inv_qs = Investigation.objects.all()

    if tab == 'ongoing':
        inv_qs = inv_qs.filter(status__in=['new', 'open', 'in_progress', 'pending'])
    elif tab == 'closed':
        inv_qs = inv_qs.filter(status__in=['resolved', 'closed'])
    # tab == 'all' → no filter

    if priority:
        inv_qs = inv_qs.filter(priority=priority)

    inv_qs = inv_qs.order_by('-created')
    ongoing_count = Investigation.objects.filter(status__in=['new', 'open', 'in_progress', 'pending']).count()

    context = {
        'investigations': inv_qs,
        'tab': tab,
        'priority': priority,
        'ongoing_count': ongoing_count,
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
                    if not investigation.owner:
                        investigation.owner = request.user
                elif new_status == 'closed':
                    investigation.closed_at = timezone.now()
                    if not investigation.owner:
                        investigation.owner = request.user
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
    
    # Auto-save / update a Report record so it shows in the Reports page
    report_name = f"Investigation Report: {investigation.case_id}"
    report_description = ai_report.get('summary', '')
    
    notes = investigation.notes.all().order_by('created')
    if investigation.status in ('closed', 'resolved') and notes.exists():
        report_description += "\n\nInvestigator's Notes:\n"
        for note in notes:
            report_description += f'- [{note.created.strftime("%Y-%m-%d %H:%M")}] {note.author.username}: {note.content}\n'
            
    if ai_report.get('key_findings'):
        report_description += '\n\nKey Findings:\n' + '\n'.join(
            f'• {f}' for f in ai_report['key_findings']
        )
    if ai_report.get('recommendations'):
        report_description += '\n\nRecommendations:\n' + '\n'.join(
            f'• {r}' for r in ai_report['recommendations']
        )
    Report.objects.update_or_create(
        name=report_name,
        defaults={
            'report_type': 'incident_response',
            'description': report_description,
            'format': 'html',
            'generated_by': investigation.owner or request.user,
        }
    )
    
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
    """Threat hunting interface with live query builder."""
    # Save query
    if request.method == 'POST' and request.POST.get('action') == 'save_query':
        query_name = request.POST.get('query_name', '').strip()
        query_text = request.POST.get('query_text', '').strip()
        if query_name and query_text:
            SavedSearch.objects.create(
                name=query_name,
                query=query_text,
                owner=request.user,
                is_public=False,
            )
            messages.success(request, f'Query "{query_name}" saved.')
        return redirect('hunting')

    saved_queries = SavedSearch.objects.filter(
        Q(owner=request.user) | Q(is_public=True)
    ).order_by('-updated')

    # Execute query if provided
    results = []
    query = request.GET.get('query', '')
    sev_filter = request.GET.get('severity', '')
    time_range = request.GET.get('time_range', '24h')

    now = timezone.now()
    time_limits = {'1h': timedelta(hours=1), '24h': timedelta(hours=24), '7d': timedelta(days=7), '30d': timedelta(days=30)}
    since = now - time_limits.get(time_range, timedelta(hours=24))

    results_qs = Event.objects.filter(time__gte=since)
    if query:
        results_qs = results_qs.filter(
            Q(message__icontains=query) | Q(source__icontains=query) |
            Q(event_type__icontains=query) | Q(source_ip__icontains=query)
        )
    if sev_filter:
        results_qs = results_qs.filter(severity=sev_filter)

    results = results_qs.order_by('-time')[:200]

    # Stats
    results_count = results_qs.count()
    sev_breakdown = results_qs.values('severity').annotate(count=Count('id')).order_by('-count') if query else []

    # Geo points for the threat map (events with lat/lon or source IPs)
    geo_points = list(Event.objects.filter(
        time__gte=since,
        source_geo_lat__isnull=False,
        source_geo_lon__isnull=False
    ).values('source_geo_lat', 'source_geo_lon', 'source_ip', 'event_type')[:100])

    # Fall back to sample source IPs if no geo data
    if not geo_points and results:
        ip_counts = results_qs.exclude(source_ip__isnull=True).values('source_ip', 'event_type').annotate(
            n=Count('id')
        ).order_by('-n')[:20]
        for item in ip_counts:
            # Cannot do real geo lookup without external API; skip for now
            pass

    context = {
        'saved_queries': saved_queries,
        'query': query,
        'results': results,
        'results_count': results_count,
        'sev_breakdown': sev_breakdown,
        'sev_filter': sev_filter,
        'time_range': time_range,
        'geo_points_json': json.dumps(geo_points),
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
    """Reports listing — includes reports auto-generated from investigations."""
    reports_list = Report.objects.select_related('generated_by').all().order_by('-generated_at')
    
    context = {
        'reports': reports_list,
        'total_reports': reports_list.count(),
        'investigation_reports': reports_list.filter(report_type='incident_response').count(),
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
@login_required
def settings_view(request):
    """SIEM settings and configuration."""
    notification_channels = NotificationChannel.objects.all()
    notification_rules = NotificationRule.objects.all()
    log_sources = LogSource.objects.all()
    
    # Get or create user profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'notification_channels': notification_channels,
        'notification_rules': notification_rules,
        'log_sources': log_sources,
        'user_profile': user_profile,
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
# ADMIN PANEL
# ============================================================================

@login_required
def admin_panel(request):
    """Custom SIEM admin panel for managing analysts. Superuser only."""
    if not request.user.is_superuser:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access denied: Admin privileges required.")

    now = timezone.now()
    last_30d = now - timedelta(days=30)

    # Gather all users with relevant statistics
    users = User.objects.all().order_by('-date_joined')
    user_stats = []

    for user in users:
        profile = UserProfile.objects.filter(user=user).first()
        role = profile.role if profile else ('admin' if user.is_superuser else 'analyst')
        alerts_count = Alert.objects.filter(assigned_to=user).count()
        investigations_count = Investigation.objects.filter(owner=user).count()
        recent_actions = AuditLog.objects.filter(user=user).count()

        user_stats.append({
            'user': user,
            'profile': profile,
            'role': role,
            'alerts_assigned': alerts_count,
            'investigations_owned': investigations_count,
            'total_actions': recent_actions,
            'last_login': user.last_login,
        })

    # System-wide stats
    total_events = Event.objects.count()
    active_alerts = Alert.objects.filter(status__in=['new', 'open', 'investigating']).count()
    open_investigations = Investigation.objects.filter(status__in=['new', 'open', 'in_progress']).count()
    active_sources = LogSource.objects.filter(is_active=True).count()

    context = {
        'user_stats': user_stats,
        'total_events': total_events,
        'active_alerts': active_alerts,
        'open_investigations': open_investigations,
        'active_sources': active_sources,
        'total_analysts': users.count(),
    }
    return render(request, 'siem/admin_panel.html', context)


@login_required
def admin_user_detail(request, user_id):
    """Detailed analyst view for admin. Superuser only."""
    if not request.user.is_superuser:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access denied: Admin privileges required.")

    analyst = get_object_or_404(User, pk=user_id)

    # Handle role update
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_role':
            new_role = request.POST.get('role')
            profile, _ = UserProfile.objects.get_or_create(user=analyst)
            profile.role = new_role
            profile.save()
            messages.success(request, f"Role updated for {analyst.username}")
        elif action == 'toggle_active':
            analyst.is_active = not analyst.is_active
            analyst.save()
            status = "activated" if analyst.is_active else "deactivated"
            messages.success(request, f"Account {status} for {analyst.username}")
        return redirect('admin_user_detail', user_id=user_id)

    profile = UserProfile.objects.filter(user=analyst).first()
    alerts_assigned = Alert.objects.filter(assigned_to=analyst).order_by('-first_seen')[:20]
    investigations_owned = Investigation.objects.filter(owner=analyst).order_by('-created')[:20]
    audit_logs = AuditLog.objects.filter(user=analyst).order_by('-timestamp')[:30]

    # Stats
    total_alerts = Alert.objects.filter(assigned_to=analyst).count()
    resolved_alerts = Alert.objects.filter(assigned_to=analyst, status='resolved').count()
    total_investigations = Investigation.objects.filter(owner=analyst).count()
    closed_investigations = Investigation.objects.filter(owner=analyst, status__in=['resolved', 'closed']).count()

    role_choices = [
        ('analyst', 'Security Analyst'),
        ('investigator', 'Investigator'),
        ('admin', 'Administrator'),
        ('viewer', 'Viewer'),
    ]

    context = {
        'analyst': analyst,
        'profile': profile,
        'alerts_assigned': alerts_assigned,
        'investigations_owned': investigations_owned,
        'audit_logs': audit_logs,
        'total_alerts': total_alerts,
        'resolved_alerts': resolved_alerts,
        'total_investigations': total_investigations,
        'closed_investigations': closed_investigations,
        'role_choices': role_choices,
    }
    return render(request, 'siem/admin_user_detail.html', context)


# ============================================================================
# ADVANCED SEARCH
# ============================================================================

@login_required
def advanced_search(request):
    """Advanced search across all SIEM data with working filters."""
    form = AdvancedSearchForm(request.GET or None)
    results = {}
    search_performed = False

    if request.GET.get('query') or request.GET.get('source_ip') or request.GET.get('severity') or request.GET.get('category'):
        search_performed = True
        query = request.GET.get('query', '').strip()
        severity_list = request.GET.getlist('severity')
        category_list = request.GET.getlist('category')
        source_ip = request.GET.get('source_ip', '').strip()
        time_range = request.GET.get('time_range', '')

        now = timezone.now()
        time_limits = {
            '1h': timedelta(hours=1),
            '24h': timedelta(hours=24),
            '7d': timedelta(days=7),
            '30d': timedelta(days=30),
        }

        # ── Events ──
        event_qs = Event.objects.all()
        if query:
            event_qs = event_qs.filter(
                Q(message__icontains=query) |
                Q(source__icontains=query) |
                Q(username__icontains=query) |
                Q(event_type__icontains=query) |
                Q(source_ip__icontains=query)
            )
        if severity_list:
            event_qs = event_qs.filter(severity__in=severity_list)
        if category_list:
            event_qs = event_qs.filter(category__in=category_list)
        if source_ip:
            event_qs = event_qs.filter(source_ip=source_ip)
        if time_range and time_range in time_limits:
            event_qs = event_qs.filter(time__gte=now - time_limits[time_range])
        event_qs = event_qs.order_by('-time')

        # Paginate events
        paginator = Paginator(event_qs, 25)
        page_number = request.GET.get('page', 1)
        events_page = paginator.get_page(page_number)
        event_count = paginator.count

        # ── Alerts ──
        alert_qs = Alert.objects.all()
        if query:
            alert_qs = alert_qs.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )
        if severity_list:
            alert_qs = alert_qs.filter(severity__in=severity_list)
        if time_range and time_range in time_limits:
            alert_qs = alert_qs.filter(first_seen__gte=now - time_limits[time_range])
        alert_qs = alert_qs.order_by('-first_seen')[:50]
        alert_count = alert_qs.count()

        # ── Investigations ──
        inv_qs = Investigation.objects.all()
        if query:
            inv_qs = inv_qs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(case_id__icontains=query)
            )
        inv_qs = inv_qs.order_by('-created')[:50]
        inv_count = inv_qs.count()

        # ── IOCs ──
        ioc_qs = IOC.objects.all()
        if query:
            ioc_qs = ioc_qs.filter(
                Q(value__icontains=query) |
                Q(description__icontains=query)
            )
        ioc_qs = ioc_qs[:50]
        ioc_count = ioc_qs.count()

        # Log the search
        if query or source_ip:
            AuditLog.objects.create(
                user=request.user,
                action_type='search',
                resource_type='advanced_search',
                description=f'Search: "{query}" | severity={severity_list} | category={category_list} | ip={source_ip}'
            )

        results = {
            'events': events_page,
            'alerts': alert_qs,
            'investigations': inv_qs,
            'iocs': ioc_qs,
        }
        counts = {
            'events': event_count,
            'alerts': alert_count,
            'investigations': inv_count,
            'iocs': ioc_count,
        }
    else:
        events_page = None
        counts = {}

    # Active filters for display
    active_filters = {}
    if request.GET.get('query'):
        active_filters['Query'] = request.GET.get('query')
    if request.GET.getlist('severity'):
        active_filters['Severity'] = ', '.join(request.GET.getlist('severity'))
    if request.GET.getlist('category'):
        active_filters['Category'] = ', '.join(request.GET.getlist('category'))
    if request.GET.get('source_ip'):
        active_filters['Source IP'] = request.GET.get('source_ip')
    if request.GET.get('time_range'):
        active_filters['Time Range'] = request.GET.get('time_range')

    context = {
        'form': form,
        'results': results,
        'counts': counts,
        'search_performed': search_performed,
        'active_filters': active_filters,
        'events_page': events_page,
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


@login_required
def documentation_page(request):
    """Serve the central documentation and help hub."""
    return render(request, 'siem/documentation.html')