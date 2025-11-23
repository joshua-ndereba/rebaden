from django.contrib import admin
from .models import (
    Asset, Event, Alert, LogSource, ThreatFeed, IOC, ThreatActor,
    MitreTactic, MitreTechnique, DetectionRule, Investigation,
    InvestigationNote, InvestigationTimeline, Evidence, Playbook,
    PlaybookExecution, UserBehaviorBaseline, AnomalyDetection,
    ComplianceFramework, ComplianceCheck, Report, NotificationChannel,
    NotificationRule, AuditLog, SavedSearch
)


# ============================================================================
# ASSET MANAGEMENT
# ============================================================================

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'ip', 'asset_type', 'criticality', 'owner', 'is_active', 'last_seen')
    list_filter = ('asset_type', 'criticality', 'is_active', 'department')
    search_fields = ('hostname', 'ip', 'owner', 'mac_address')
    readonly_fields = ('created', 'updated', 'last_seen')
    fieldsets = (
        ('Basic Information', {
            'fields': ('hostname', 'ip', 'mac_address', 'asset_type')
        }),
        ('System Details', {
            'fields': ('os', 'os_version', 'location')
        }),
        ('Ownership', {
            'fields': ('owner', 'department', 'criticality')
        }),
        ('Security', {
            'fields': ('risk_score', 'is_active', 'tags')
        }),
        ('Metadata', {
            'fields': ('metadata', 'created', 'updated', 'last_seen'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# EVENT & LOG MANAGEMENT
# ============================================================================

@admin.register(LogSource)
class LogSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'host', 'is_active', 'events_received', 'last_event_time')
    list_filter = ('source_type', 'is_active')
    search_fields = ('name', 'host')
    readonly_fields = ('events_received', 'last_event_time', 'created')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('time', 'source', 'severity', 'category', 'source_ip', 'username')
    list_filter = ('severity', 'category', 'source_geo_country')
    search_fields = ('source', 'message', 'source_ip', 'username')
    readonly_fields = ('created',)
    date_hierarchy = 'time'


# ============================================================================
# THREAT INTELLIGENCE
# ============================================================================

@admin.register(ThreatFeed)
class ThreatFeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'feed_type', 'is_active', 'ioc_count', 'last_update')
    list_filter = ('feed_type', 'is_active')
    search_fields = ('name', 'url')
    readonly_fields = ('ioc_count', 'last_update', 'created')


@admin.register(IOC)
class IOCAdmin(admin.ModelAdmin):
    list_display = ('ioc_type', 'value', 'threat_type', 'severity', 'confidence', 'is_active', 'first_seen')
    list_filter = ('ioc_type', 'severity', 'confidence', 'is_active', 'threat_type')
    search_fields = ('value', 'description', 'threat_actor', 'campaign')
    readonly_fields = ('first_seen', 'last_seen', 'created', 'updated')
    date_hierarchy = 'first_seen'


@admin.register(ThreatActor)
class ThreatActorAdmin(admin.ModelAdmin):
    list_display = ('name', 'sophistication', 'country', 'first_seen', 'last_activity')
    list_filter = ('sophistication', 'country')
    search_fields = ('name', 'aliases', 'description')
    readonly_fields = ('created',)


# ============================================================================
# MITRE ATT&CK
# ============================================================================

@admin.register(MitreTactic)
class MitreTacticAdmin(admin.ModelAdmin):
    list_display = ('tactic_id', 'name')
    search_fields = ('tactic_id', 'name', 'description')


@admin.register(MitreTechnique)
class MitreTechniqueAdmin(admin.ModelAdmin):
    list_display = ('technique_id', 'name', 'tactic', 'is_subtechnique')
    list_filter = ('tactic', 'is_subtechnique')
    search_fields = ('technique_id', 'name', 'description')
    raw_id_fields = ('parent_technique',)


# ============================================================================
# DETECTION & CORRELATION
# ============================================================================

@admin.register(DetectionRule)
class DetectionRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'rule_type', 'severity', 'is_enabled', 'times_triggered', 'last_triggered')
    list_filter = ('rule_type', 'severity', 'is_enabled', 'false_positive_rate')
    search_fields = ('name', 'description', 'rule_logic')
    readonly_fields = ('times_triggered', 'last_triggered', 'created', 'updated')
    filter_horizontal = ('mitre_techniques',)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('name', 'severity', 'status', 'assigned_to', 'first_seen', 'event_count')
    list_filter = ('severity', 'status', 'first_seen')
    search_fields = ('name', 'description', 'source_ip')
    readonly_fields = ('first_seen', 'last_seen', 'acknowledged_at', 'resolved_at')
    filter_horizontal = ('related_events', 'affected_assets', 'mitre_techniques')
    date_hierarchy = 'first_seen'


# ============================================================================
# INCIDENT RESPONSE
# ============================================================================

@admin.register(Investigation)
class InvestigationAdmin(admin.ModelAdmin):
    list_display = ('case_id', 'title', 'status', 'priority', 'severity', 'owner', 'created')
    list_filter = ('status', 'priority', 'severity', 'assigned_team')
    search_fields = ('case_id', 'title', 'description')
    readonly_fields = ('created', 'updated', 'started_at', 'resolved_at', 'closed_at')
    filter_horizontal = ('alerts', 'related_iocs', 'affected_assets', 'mitre_techniques')
    date_hierarchy = 'created'


@admin.register(InvestigationNote)
class InvestigationNoteAdmin(admin.ModelAdmin):
    list_display = ('investigation', 'author', 'is_important', 'created')
    list_filter = ('is_important', 'created')
    search_fields = ('content',)
    readonly_fields = ('created', 'updated')


@admin.register(InvestigationTimeline)
class InvestigationTimelineAdmin(admin.ModelAdmin):
    list_display = ('investigation', 'timestamp', 'event_type', 'user')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('description',)
    readonly_fields = ('timestamp',)


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'evidence_type', 'investigation', 'collected_by', 'collected_at', 'file_size')
    list_filter = ('evidence_type', 'collected_at')
    search_fields = ('name', 'description', 'file_hash')
    readonly_fields = ('collected_at',)


@admin.register(Playbook)
class PlaybookAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_automated', 'is_active', 'times_executed', 'success_rate', 'author')
    list_filter = ('is_automated', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('times_executed', 'success_rate', 'created', 'updated')
    filter_horizontal = ('mitre_techniques',)


@admin.register(PlaybookExecution)
class PlaybookExecutionAdmin(admin.ModelAdmin):
    list_display = ('playbook', 'investigation', 'started_by', 'started_at', 'status')
    list_filter = ('status', 'started_at')
    search_fields = ('playbook__name',)
    readonly_fields = ('started_at', 'completed_at')


# ============================================================================
# UEBA
# ============================================================================

@admin.register(UserBehaviorBaseline)
class UserBehaviorBaselineAdmin(admin.ModelAdmin):
    list_display = ('username', 'peer_group', 'risk_score', 'last_calculated')
    list_filter = ('peer_group', 'risk_score')
    search_fields = ('username',)
    readonly_fields = ('last_calculated', 'created')


@admin.register(AnomalyDetection)
class AnomalyDetectionAdmin(admin.ModelAdmin):
    list_display = ('anomaly_type', 'entity_type', 'entity_id', 'severity', 'confidence_score', 'detected_at', 'is_reviewed')
    list_filter = ('anomaly_type', 'severity', 'is_reviewed', 'is_false_positive')
    search_fields = ('entity_id', 'description')
    readonly_fields = ('detected_at',)
    filter_horizontal = ('related_events',)


# ============================================================================
# COMPLIANCE
# ============================================================================

@admin.register(ComplianceFramework)
class ComplianceFrameworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'is_active', 'created')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    readonly_fields = ('created',)


@admin.register(ComplianceCheck)
class ComplianceCheckAdmin(admin.ModelAdmin):
    list_display = ('framework', 'requirement_id', 'name', 'is_automated', 'last_run', 'last_result')
    list_filter = ('framework', 'is_automated', 'last_result')
    search_fields = ('requirement_id', 'name', 'description')
    readonly_fields = ('last_run',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'format', 'generated_by', 'generated_at', 'is_scheduled')
    list_filter = ('report_type', 'format', 'is_scheduled', 'generated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('generated_at',)
    date_hierarchy = 'generated_at'


# ============================================================================
# NOTIFICATIONS
# ============================================================================

@admin.register(NotificationChannel)
class NotificationChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel_type', 'is_active', 'created')
    list_filter = ('channel_type', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('created',)


@admin.register(NotificationRule)
class NotificationRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'severity_threshold', 'is_enabled', 'max_notifications_per_hour')
    list_filter = ('severity_threshold', 'is_enabled')
    search_fields = ('name', 'description')
    filter_horizontal = ('channels',)
    readonly_fields = ('created', 'updated')


# ============================================================================
# AUDIT & SEARCHES
# ============================================================================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action_type', 'resource_type', 'resource_id', 'ip_address')
    list_filter = ('action_type', 'resource_type', 'timestamp')
    search_fields = ('user__username', 'description', 'resource_id')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'query_type', 'owner', 'is_public', 'is_scheduled', 'times_executed', 'last_executed')
    list_filter = ('query_type', 'is_public', 'is_scheduled')
    search_fields = ('name', 'description', 'query')
    readonly_fields = ('times_executed', 'last_executed', 'created', 'updated')