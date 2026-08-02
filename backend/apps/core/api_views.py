"""
API Views for SIEM Data Ingestion and Management
Handles real data intake, CRUD operations, and asset/log management
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from datetime import timedelta
import json
import os

from .models import (
    Asset, LogSource, Event, Alert, IOC, DetectionRule,
    Investigation, Playbook, Report, Anomaly, UserProfile,
    SystemSettings, MitreTechnique, ComplianceFramework
)
from .serializers import (
    AssetSerializer, AssetDetailSerializer, LogSourceSerializer,
    EventSerializer, EventDetailSerializer, AlertSerializer,
    AlertDetailSerializer, AlertActionSerializer, IOCSerializer,
    DetectionRuleSerializer, InvestigationSerializer,
    InvestigationDetailSerializer, PlaybookSerializer,
    ReportSerializer, AnomalySerializer, UserProfileSerializer,
    SystemSettingsSerializer, MITRETechniqueSerializer
)
from .log_parser import LogParser


# ============================================================================
# ASSET MANAGEMENT API
# ============================================================================

class AssetViewSet(viewsets.ModelViewSet):
    """
    API for managing assets
    
    list: Get all assets
    create: Add a new asset
    retrieve: Get asset details
    update: Update asset information
    partial_update: Partially update asset
    destroy: Delete an asset
    
    Actions:
    - search: Search assets by hostname, IP, or tag
    - by_criticality: Filter by criticality level
    - with_events: Get assets with recent events
    """
    queryset = Asset.objects.all().order_by('-criticality', 'hostname')
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['asset_type', 'criticality', 'is_active']
    search_fields = ['hostname', 'ip', 'owner', 'department', 'tags']
    ordering_fields = ['hostname', 'ip', 'risk_score', 'last_seen']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AssetDetailSerializer
        return AssetSerializer

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create assets from list"""
        assets_data = request.data.get('assets', [])
        created = []
        
        for asset_data in assets_data:
            try:
                asset, _ = Asset.objects.get_or_create(
                    hostname=asset_data['hostname'],
                    ip=asset_data['ip'],
                    defaults=asset_data
                )
                created.append(AssetSerializer(asset).data)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(created, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def by_criticality(self, request):
        """Filter assets by criticality level"""
        criticality = request.query_params.get('level')
        if criticality:
            assets = self.queryset.filter(criticality=criticality)
            serializer = self.get_serializer(assets, many=True)
            return Response(serializer.data)
        return Response([], status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def with_events(self, request):
        """Get assets that have recent events"""
        days = int(request.query_params.get('days', 7))
        time_threshold = timezone.now() - timedelta(days=days)
        
        assets = self.queryset.filter(
            event__time__gte=time_threshold
        ).distinct().annotate(
            recent_events=Count('event', filter=Q(event__time__gte=time_threshold))
        )
        
        serializer = self.get_serializer(assets, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def activity(self, request, pk=None):
        """Get activity history for an asset"""
        asset = self.get_object()
        days = int(request.query_params.get('days', 30))
        time_threshold = timezone.now() - timedelta(days=days)
        
        events = asset.event_set.filter(time__gte=time_threshold).order_by('-time')[:100]
        alerts = asset.alert_set.filter(created__gte=time_threshold).order_by('-created')[:50]
        
        return Response({
            'asset': AssetDetailSerializer(asset).data,
            'recent_events': EventSerializer(events, many=True).data,
            'recent_alerts': AlertSerializer(alerts, many=True).data,
        })


# ============================================================================
# LOG SOURCE MANAGEMENT API
# ============================================================================

class LogSourceViewSet(viewsets.ModelViewSet):
    """
    API for managing log sources
    
    list: Get all log sources
    create: Add a new log source
    retrieve: Get log source details
    update: Update log source
    destroy: Delete a log source
    
    Actions:
    - stats: Get statistics for a log source
    - test_connection: Test connectivity to log source
    """
    queryset = LogSource.objects.all().order_by('-is_active', 'name')
    serializer_class = LogSourceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['source_type', 'is_active']
    search_fields = ['name', 'host']

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for a log source"""
        log_source = self.get_object()
        days = int(request.query_params.get('days', 7))
        time_threshold = timezone.now() - timedelta(days=days)
        
        events = log_source.event_set.filter(time__gte=time_threshold)
        
        severity_breakdown = events.values('severity').annotate(
            count=Count('id')
        ).order_by('-count')
        
        hourly_stats = []
        for i in range(24):
            hour_start = timezone.now().replace(hour=i, minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)
            count = events.filter(time__gte=hour_start, time__lt=hour_end).count()
            hourly_stats.append({'hour': i, 'count': count})
        
        return Response({
            'log_source': LogSourceSerializer(log_source).data,
            'total_events': events.count(),
            'severity_breakdown': list(severity_breakdown),
            'hourly_stats': hourly_stats,
        })

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test connection to log source"""
        log_source = self.get_object()
        
        try:
            # Simple connection test - in production, implement proper health checks
            if log_source.is_active and log_source.host:
                return Response({
                    'status': 'connected',
                    'message': f'Connected to {log_source.host}:{log_source.port}'
                })
            else:
                return Response({
                    'status': 'disconnected',
                    'message': 'Log source is not active'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# LOG FILE UPLOAD & PROCESSING API
# ============================================================================

class LogUploadViewSet(viewsets.ViewSet):
    """
    API for uploading and processing log files
    
    Actions:
    - upload: Upload a log file for processing
    - process: Process uploaded log file
    - history: Get upload history
    - stats: Get processing statistics
    """
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload a log file"""
        uploaded_file = request.FILES.get('file')
        log_type = request.data.get('log_type', 'auto')
        source_name = request.data.get('source_name', 'uploaded_logs')
        
        if not uploaded_file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save file temporarily
        file_path = f'/tmp/{uploaded_file.name}'
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        try:
            # Get or create log source
            log_source, _ = LogSource.objects.get_or_create(
                name=source_name,
                defaults={
                    'source_type': log_type,
                    'host': 'uploaded',
                    'is_active': True,
                }
            )
            
            # Parse log file
            events_data = LogParser.parse_file(file_path, log_type)
            
            # Create events
            events_created = []
            for event_data in events_data:
                event_data['log_source'] = log_source
                event = Event.objects.create(**event_data)
                events_created.append(event)
            
            # Update log source stats
            log_source.events_received += len(events_created)
            log_source.last_event_time = timezone.now()
            log_source.save()
            
            # Clean up temp file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return Response({
                'status': 'success',
                'message': f'Processed {len(events_created)} events',
                'log_source_id': log_source.id,
                'events_created': len(events_created),
                'file': uploaded_file.name,
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get log upload history"""
        log_sources = LogSource.objects.filter(host='uploaded').order_by('-created')
        
        history = []
        for source in log_sources:
            history.append({
                'id': source.id,
                'name': source.name,
                'events_received': source.events_received,
                'last_event_time': source.last_event_time,
                'created': source.created,
            })
        
        return Response(history)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get upload statistics"""
        total_uploads = LogSource.objects.filter(host='uploaded').count()
        total_events = Event.objects.filter(log_source__host='uploaded').count()
        
        by_type = Event.objects.filter(
            log_source__host='uploaded'
        ).values('log_source__source_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        by_severity = Event.objects.filter(
            log_source__host='uploaded'
        ).values('severity').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_uploads': total_uploads,
            'total_events': total_events,
            'by_type': list(by_type),
            'by_severity': list(by_severity),
        })


# ============================================================================
# EVENT API
# ============================================================================

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for events
    
    list: Get all events with filtering
    retrieve: Get event details
    
    Actions:
    - by_severity: Filter events by severity
    - by_asset: Get events for an asset
    - search: Full-text search on events
    - timeline: Get events over time
    """
    queryset = Event.objects.all().order_by('-time')
    permission_classes = [IsAuthenticated]
    filterset_fields = ['severity', 'category', 'event_type', 'source_ip']
    search_fields = ['source', 'message', 'username', 'source_ip', 'event_type']
    ordering_fields = ['-time', 'severity', 'source_ip']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EventDetailSerializer
        return EventSerializer

    @action(detail=False, methods=['get'])
    def by_severity(self, request):
        """Get events by severity level"""
        severity = request.query_params.get('level')
        if severity:
            events = self.queryset.filter(severity=severity)[:100]
            serializer = self.get_serializer(events, many=True)
            return Response(serializer.data)
        return Response([], status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def by_asset(self, request):
        """Get events for a specific asset"""
        asset_id = request.query_params.get('asset_id')
        if asset_id:
            events = self.queryset.filter(asset_id=asset_id)[:100]
            serializer = self.get_serializer(events, many=True)
            return Response(serializer.data)
        return Response([], status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def timeline(self, request):
        """Get events in timeline format"""
        days = int(request.query_params.get('days', 7))
        time_threshold = timezone.now() - timedelta(days=days)
        
        timeline = {}
        events = self.queryset.filter(time__gte=time_threshold)
        
        for event in events:
            day = event.time.strftime('%Y-%m-%d')
            if day not in timeline:
                timeline[day] = {'count': 0, 'severity_breakdown': {}}
            
            timeline[day]['count'] += 1
            severity = event.severity
            timeline[day]['severity_breakdown'][severity] = timeline[day]['severity_breakdown'].get(severity, 0) + 1
        
        return Response(timeline)


# ============================================================================
# ALERT API
# ============================================================================

class AlertViewSet(viewsets.ModelViewSet):
    """
    API for alert management
    
    list: Get all alerts
    create: Create a new alert
    retrieve: Get alert details
    update: Update alert
    destroy: Delete alert
    
    Actions:
    - by_status: Filter alerts by status
    - by_severity: Filter alerts by severity
    - open_alerts: Get all open alerts
    - take_action: Perform actions on alerts (resolve, assign, etc)
    """
    queryset = Alert.objects.all().order_by('-first_seen')
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'severity', 'assigned_to']
    search_fields = ['name', 'description']
    ordering_fields = ['-first_seen', 'severity']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AlertDetailSerializer
        elif self.action == 'take_action':
            return AlertActionSerializer
        return AlertSerializer

    @action(detail=False, methods=['get'])
    def open_alerts(self, request):
        """Get all open/new alerts"""
        alerts = self.queryset.filter(status__in=['new', 'investigating'])
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Filter alerts by status"""
        status_filter = request.query_params.get('status')
        if status_filter:
            alerts = self.queryset.filter(status=status_filter)[:50]
            serializer = self.get_serializer(alerts, many=True)
            return Response(serializer.data)
        return Response([], status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def take_action(self, request, pk=None):
        """Perform actions on an alert"""
        alert = self.get_object()
        serializer = AlertActionSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            notes = serializer.validated_data.get('notes', '')
            
            if action == 'resolve':
                alert.status = 'resolved'
                alert.resolved_at = timezone.now()
            elif action == 'escalate':
                alert.status = 'investigating'
            elif action == 'investigate':
                alert.status = 'investigating'
            elif action == 'close':
                alert.status = 'resolved'
                alert.resolved_at = timezone.now()
            elif action == 'reopen':
                alert.status = 'new'
            
            if notes:
                alert.metadata = (alert.metadata or '') + f'\n[{timezone.now()}] {notes}'
            
            alert.save()
            return Response(AlertSerializer(alert).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# INVESTIGATION API
# ============================================================================

class InvestigationViewSet(viewsets.ModelViewSet):
    """
    API for investigation management
    
    list: Get all investigations
    create: Create a new investigation
    retrieve: Get investigation details
    update: Update investigation
    destroy: Delete investigation
    
    Actions:
    - open: Get open investigations
    - by_priority: Filter by priority
    - assign: Assign investigation to investigator
    """
    queryset = Investigation.objects.all().order_by('-created')
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'priority', 'owner']
    search_fields = ['case_id', 'title', 'description', 'resolution', 'root_cause', 'lessons_learned']
    ordering_fields = ['-created', 'priority', 'status']

    def get_serializer_class(self):
        if self.action in ['retrieve', 'partial_update', 'update']:
            return InvestigationDetailSerializer
        return InvestigationSerializer

    @action(detail=False, methods=['get'])
    def open(self, request):
        """Get open/in-progress investigations"""
        investigations = self.queryset.filter(
            status__in=['open', 'in_progress']
        )
        serializer = self.get_serializer(investigations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign investigation to investigator"""
        investigation = self.get_object()
        investigator_id = request.data.get('investigator_id')
        
        if investigator_id:
            investigation.owner_id = investigator_id
            investigation.save()
            return Response(InvestigationDetailSerializer(investigation).data)
        
        return Response(
            {'error': 'investigator_id required'},
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================================
# PROFILE API
# ============================================================================

class UserProfileViewSet(viewsets.ViewSet):
    """
    API for user profile management
    
    Actions:
    - me: Get current user's profile
    - update_profile: Update user profile
    - settings: Get user settings
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return Response({
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            },
            'profile': UserProfileSerializer(profile).data,
        })

    @action(detail=False, methods=['post'])
    def update_profile(self, request):
        """Update current user's profile"""
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        
        user = request.user
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        user.save()
        
        profile.role = request.data.get('role', profile.role)
        profile.department = request.data.get('department', profile.department)
        profile.timezone = request.data.get('timezone', profile.timezone)
        profile.notifications_enabled = request.data.get('notifications_enabled', profile.notifications_enabled)
        profile.email_alerts = request.data.get('email_alerts', profile.email_alerts)
        profile.alert_severity_threshold = request.data.get(
            'alert_severity_threshold',
            profile.alert_severity_threshold
        )
        profile.save()
        
        return Response(UserProfileSerializer(profile).data)

    @action(detail=False, methods=['get'])
    def settings(self, request):
        """Get user settings"""
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return Response(UserProfileSerializer(profile).data)
