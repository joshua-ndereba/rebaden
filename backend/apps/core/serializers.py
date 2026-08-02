"""
DRF Serializers for SIEM Core Models
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Asset, LogSource, Event, Alert, IOC, ThreatFeed,
    DetectionRule, Investigation, Playbook, Report,
    UserProfile, SystemSettings, Anomaly, MitreTechnique,
    MITREMapping, ComplianceFramework, ComplianceCheck
)


# ============================================================================
# USER & PROFILE SERIALIZERS
# ============================================================================

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'role', 'department', 'phone', 'timezone',
            'notifications_enabled', 'email_alerts', 'sms_alerts',
            'alert_severity_threshold', 'created', 'updated'
        ]
        read_only_fields = ['id', 'created', 'updated']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    profile = UserProfileSerializer(source='userprofile', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_active', 'date_joined', 'profile'
        ]
        read_only_fields = ['id', 'date_joined']


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer for profile updates"""
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'password', 'confirm_password'
        ]
        read_only_fields = ['id', 'username']

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password and password != confirm_password:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        return data

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('confirm_password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


# ============================================================================
# ASSET SERIALIZERS
# ============================================================================

class AssetSerializer(serializers.ModelSerializer):
    """Serializer for Asset model"""
    class Meta:
        model = Asset
        fields = [
            'id', 'hostname', 'ip', 'mac_address', 'asset_type', 'os',
            'os_version', 'owner', 'department', 'location', 'criticality',
            'risk_score', 'last_seen', 'is_active', 'tags', 'metadata',
            'created', 'updated'
        ]
        read_only_fields = ['id', 'last_seen', 'created', 'updated']


class AssetDetailSerializer(AssetSerializer):
    """Detailed asset serializer with related events"""
    event_count = serializers.SerializerMethodField()

    class Meta(AssetSerializer.Meta):
        fields = AssetSerializer.Meta.fields + ['event_count']

    def get_event_count(self, obj):
        return obj.event_set.count()


# ============================================================================
# LOG SOURCE SERIALIZERS
# ============================================================================

class LogSourceSerializer(serializers.ModelSerializer):
    """Serializer for LogSource model"""
    class Meta:
        model = LogSource
        fields = [
            'id', 'name', 'source_type', 'host', 'port', 'protocol',
            'is_active', 'events_received', 'last_event_time',
            'parser_config', 'created'
        ]
        read_only_fields = ['id', 'events_received', 'last_event_time', 'created']


# ============================================================================
# EVENT SERIALIZERS
# ============================================================================

class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model"""
    source_name = serializers.CharField(source='log_source.name', read_only=True)
    asset_name = serializers.CharField(source='asset.hostname', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'time', 'source', 'source_name', 'message', 'raw_log',
            'severity', 'category', 'asset', 'asset_name', 'log_source',
            'source_ip', 'dest_ip', 'source_port', 'dest_port', 'username',
            'process_name', 'file_path', 'protocol', 'action', 'result',
            'source_geo_country', 'source_geo_city', 'source_geo_lat',
            'source_geo_lon', 'tags', 'custom_fields', 'event_type',
            'created'
        ]
        read_only_fields = ['id', 'created']


class EventDetailSerializer(EventSerializer):
    """Detailed event serializer"""
    log_source = LogSourceSerializer(read_only=True)
    asset = AssetSerializer(read_only=True)

    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields


# ============================================================================
# ALERT SERIALIZERS
# ============================================================================

class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model"""
    rule_name = serializers.CharField(source='detection_rule.name', read_only=True)
    affected_assets = AssetSerializer(many=True, read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'name', 'description', 'severity', 'status',
            'detection_rule', 'rule_name', 'affected_assets',
            'event_count', 'source_ip', 'dest_ip',
            'first_seen', 'last_seen', 'assigned_to',
            'resolved_at', 'tags', 'metadata'
        ]
        read_only_fields = ['id', 'event_count', 'first_seen', 'last_seen']


class AlertDetailSerializer(AlertSerializer):
    """Detailed alert serializer with related data"""
    detection_rule = serializers.SerializerMethodField()
    affected_assets = AssetSerializer(many=True, read_only=True)
    related_events = EventSerializer(many=True, read_only=True)

    class Meta(AlertSerializer.Meta):
        fields = AlertSerializer.Meta.fields + ['related_events']

    def get_detection_rule(self, obj):
        if obj.detection_rule:
            return {
                'id': obj.detection_rule.id,
                'name': obj.detection_rule.name,
                'rule_type': obj.detection_rule.rule_type,
                'severity': obj.detection_rule.severity
            }
        return None


class AlertActionSerializer(serializers.Serializer):
    """Serializer for alert actions (status change, assignment, etc)"""
    action = serializers.ChoiceField(choices=[
        ('resolve', 'Resolve'),
        ('escalate', 'Escalate'),
        ('investigate', 'Investigate'),
        ('close', 'Close'),
        ('reopen', 'Reopen')
    ])
    notes = serializers.CharField(required=False, allow_blank=True)
    assigned_to = serializers.IntegerField(required=False)


# ============================================================================
# IOC SERIALIZERS
# ============================================================================

class IOCSerializer(serializers.ModelSerializer):
    """Serializer for IOC model"""
    feed_name = serializers.CharField(source='source_feed.name', read_only=True)

    class Meta:
        model = IOC
        fields = [
            'id', 'ioc_type', 'value', 'description', 'threat_type',
            'confidence', 'severity', 'threat_actor', 'campaign',
            'source_feed', 'feed_name', 'first_seen', 'last_seen',
            'is_active', 'tags', 'metadata'
        ]
        read_only_fields = ['id', 'first_seen', 'last_seen']


# ============================================================================
# THREAT FEED SERIALIZERS
# ============================================================================

class ThreatFeedSerializer(serializers.ModelSerializer):
    """Serializer for ThreatFeed model"""
    class Meta:
        model = ThreatFeed
        fields = [
            'id', 'name', 'url', 'feed_type', 'is_active',
            'last_update', 'update_frequency', 'ioc_count', 'created'
        ]
        read_only_fields = ['id', 'ioc_count', 'last_update', 'created']


# ============================================================================
# DETECTION RULE SERIALIZERS
# ============================================================================

class DetectionRuleSerializer(serializers.ModelSerializer):
    """Serializer for DetectionRule model"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = DetectionRule
        fields = [
            'id', 'name', 'description', 'rule_type', 'rule_content',
            'is_active', 'severity', 'tags', 'created_by', 'created_by_name',
            'created', 'updated', 'times_triggered', 'last_triggered'
        ]
        read_only_fields = ['id', 'times_triggered', 'last_triggered', 'created', 'updated']


# ============================================================================
# INVESTIGATION SERIALIZERS
# ============================================================================

class InvestigationSerializer(serializers.ModelSerializer):
    """Serializer for Investigation model"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    alert_count = serializers.SerializerMethodField()

    class Meta:
        model = Investigation
        fields = [
            'id', 'case_id', 'title', 'description', 'status', 'priority',
            'severity', 'assigned_team', 'owner', 'owner_name',
            'alert_count', 'created', 'updated', 'started_at',
            'resolved_at', 'closed_at', 'resolution', 'root_cause',
            'lessons_learned', 'tags', 'metadata'
        ]
        read_only_fields = ['id', 'case_id', 'created', 'updated']

    def get_alert_count(self, obj):
        return obj.alerts.count()


class InvestigationDetailSerializer(InvestigationSerializer):
    """Detailed investigation serializer"""
    alerts = AlertSerializer(many=True, read_only=True)
    affected_assets = AssetSerializer(many=True, read_only=True)
    related_iocs = IOCSerializer(many=True, read_only=True)

    class Meta(InvestigationSerializer.Meta):
        fields = InvestigationSerializer.Meta.fields + ['alerts', 'affected_assets', 'related_iocs']


# ============================================================================
# PLAYBOOK SERIALIZERS
# ============================================================================

class PlaybookSerializer(serializers.ModelSerializer):
    """Serializer for Playbook model"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Playbook
        fields = [
            'id', 'name', 'description', 'playbook_type', 'content',
            'is_active', 'created_by', 'created_by_name', 'created', 'updated'
        ]
        read_only_fields = ['id', 'created', 'updated']


# ============================================================================
# REPORT SERIALIZERS
# ============================================================================

class ReportSerializer(serializers.ModelSerializer):
    """Serializer for Report model"""
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)

    class Meta:
        model = Report
        fields = [
            'id', 'title', 'report_type', 'content', 'file_path',
            'generated_by', 'generated_by_name', 'created',
            'date_from', 'date_to', 'severity_filter', 'category_filter'
        ]
        read_only_fields = ['id', 'file_path', 'created']


# ============================================================================
# ANOMALY SERIALIZERS
# ============================================================================

class AnomalySerializer(serializers.ModelSerializer):
    """Serializer for Anomaly model"""
    asset_name = serializers.CharField(source='asset.hostname', read_only=True)

    class Meta:
        model = Anomaly
        fields = [
            'id', 'asset', 'asset_name', 'anomaly_type', 'description',
            'confidence_score', 'severity', 'detected_at',
            'is_investigated', 'investigation_notes'
        ]
        read_only_fields = ['id', 'detected_at']


# ============================================================================
# MITRE SERIALIZERS
# ============================================================================

class MITRETechniqueSerializer(serializers.ModelSerializer):
    """Serializer for MITRETechnique model"""
    class Meta:
        model = MitreTechnique
        fields = [
            'id', 'technique_id', 'name', 'description', 'tactic',
            'platforms', 'data_sources', 'detection', 'mitigation',
            'is_subtechnique', 'created'
        ]
        read_only_fields = ['id', 'created']


class MITREMappingSerializer(serializers.ModelSerializer):
    """Serializer for MITREMapping model"""
    technique_id = serializers.CharField(source='technique.technique_id', read_only=True)
    technique_name = serializers.CharField(source='technique.name', read_only=True)

    class Meta:
        model = MITREMapping
        fields = [
            'id', 'technique', 'technique_id', 'technique_name',
            'event', 'alert', 'ioc', 'confidence', 'mapped_by', 'mapped_at'
        ]
        read_only_fields = ['id', 'mapped_at']


# ============================================================================
# COMPLIANCE SERIALIZERS
# ============================================================================

class ComplianceCheckSerializer(serializers.ModelSerializer):
    """Serializer for ComplianceCheck model"""
    framework_name = serializers.CharField(source='framework.name', read_only=True)
    checked_by_name = serializers.CharField(source='checked_by.get_full_name', read_only=True)

    class Meta:
        model = ComplianceCheck
        fields = [
            'id', 'framework', 'framework_name', 'control_id',
            'control_description', 'status', 'evidence',
            'checked_at', 'checked_by', 'checked_by_name'
        ]
        read_only_fields = ['id', 'checked_at']


class ComplianceFrameworkSerializer(serializers.ModelSerializer):
    """Serializer for ComplianceFramework model"""
    check_count = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceFramework
        fields = [
            'id', 'name', 'description', 'version', 'controls',
            'is_active', 'check_count', 'created', 'updated'
        ]
        read_only_fields = ['id', 'created', 'updated']

    def get_check_count(self, obj):
        return obj.compliancecheck_set.count()


# ============================================================================
# SETTINGS SERIALIZERS
# ============================================================================

class SystemSettingsSerializer(serializers.ModelSerializer):
    """Serializer for SystemSettings model"""
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)

    class Meta:
        model = SystemSettings
        fields = [
            'id', 'key', 'value', 'description', 'category',
            'is_public', 'updated_by', 'updated_by_name', 'updated'
        ]
        read_only_fields = ['id', 'updated']
