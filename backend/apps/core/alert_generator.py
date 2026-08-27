"""
Alert Generation Engine
Monitors events and generates alerts based on detection rules and patterns
"""

from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
import json
from .models import Event, Alert, DetectionRule, IOC, Asset, MITREMapping, MitreTechnique


class AlertGenerator:
    """
    Generates alerts from events based on detection rules,
    threat intelligence, and statistical anomalies
    """

    @staticmethod
    def process_event(event):
        """
        Process a single event and generate alerts if conditions are met
        """
        alerts_created = []
        
        # Rule-based detection
        rule_alerts = AlertGenerator.check_detection_rules(event)
        alerts_created.extend(rule_alerts)
        
        # IOC matching
        ioc_alerts = AlertGenerator.check_ioc_matches(event)
        alerts_created.extend(ioc_alerts)
        
        # Pattern-based detection
        pattern_alerts = AlertGenerator.check_suspicious_patterns(event)
        alerts_created.extend(pattern_alerts)
        
        # MITRE ATT&CK mapping
        AlertGenerator.map_mitre_techniques(event)
        
        return alerts_created

    @staticmethod
    def check_detection_rules(event):
        """
        Check event against active detection rules
        """
        alerts = []
        active_rules = DetectionRule.objects.filter(is_enabled=True)
        
        for rule in active_rules:
            try:
                # Simple pattern matching for rule logic
                rule_content = rule.rule_logic.lower()
                message = event.message.lower()
                
                # Check if keywords from rule match event
                if AlertGenerator.rule_matches(rule, event):
                    # Create alert
                    alert, created = Alert.objects.get_or_create(
                        detection_rule=rule,
                        first_seen=event.time,
                        defaults={
                            'name': f'Alert: {rule.name}',
                            'description': f'Triggered by detection rule: {rule.name}',
                            'severity': rule.severity,
                            'status': 'new',
                            'source_ip': event.source_ip,
                            'dest_ip': event.dest_ip,
                        }
                    )
                    
                    # Add event to alert
                    if created:
                        alert.related_events.add(event)
                        alert.event_count = 1
                        alert.last_seen = event.time
                        if event.asset:
                            alert.affected_assets.add(event.asset)
                        alert.save()
                    else:
                        alert.related_events.add(event)
                        alert.event_count += 1
                        alert.last_seen = event.time
                        if event.asset:
                            alert.affected_assets.add(event.asset)
                        alert.save()
                    
                    # Update rule hit count
                    rule.hit_count += 1
                    rule.last_hit = timezone.now()
                    rule.save()
                    
                    if created:
                        alerts.append(alert)
            
            except Exception as e:
                print(f"Error checking rule {rule.id}: {e}")
                continue
        
        return alerts

    @staticmethod
    def rule_matches(rule, event):
        """
        Check if an event matches a detection rule
        Simple keyword matching - can be extended for complex logic
        """
        try:
            rule_content = rule.rule_logic.lower()
            message = event.message.lower()
            source = event.source.lower() if event.source else ""
            
            # Parse rule content for keywords
            keywords = rule_content.split()
            
            # Check for keyword matches
            matches = sum(1 for keyword in keywords if keyword in message or keyword in source)
            
            # Match if at least 30% of keywords found
            threshold = max(1, len(keywords) // 3)
            return matches >= threshold
        
        except Exception as e:
            print(f"Error matching rule: {e}")
            return False

    @staticmethod
    def check_ioc_matches(event):
        """
        Check if event contains any known IOCs (Indicators of Compromise)
        """
        alerts = []
        
        try:
            # Check source IP
            if event.source_ip:
                ioc_match = IOC.objects.filter(
                    ioc_type='ip',
                    value=event.source_ip,
                    is_active=True
                ).first()
                
                if ioc_match:
                    alert, created = Alert.objects.get_or_create(
                        name=f'IOC Match: {ioc_match.threat_type or "Unknown Threat"}',
                        first_seen=event.time,
                        defaults={
                            'description': f'Event source IP matches known IOC: {ioc_match.value}',
                            'severity': ioc_match.severity,
                            'status': 'new',
                            'source_ip': event.source_ip,
                            'dest_ip': event.dest_ip,
                        }
                    )
                    
                    if created:
                        alert.related_events.add(event)
                        alert.event_count = 1
                        if event.asset:
                            alert.affected_assets.add(event.asset)
                        alert.save()
                        alerts.append(alert)
            
            # Check username
            if event.username:
                ioc_match = IOC.objects.filter(
                    ioc_type='user',
                    value=event.username,
                    is_active=True
                ).first()
                
                if ioc_match:
                    alert, created = Alert.objects.get_or_create(
                        name=f'IOC Match: Suspicious User',
                        first_seen=event.time,
                        defaults={
                            'description': f'Event contains known malicious user: {ioc_match.value}',
                            'severity': ioc_match.severity,
                            'status': 'new',
                            'source_ip': event.source_ip,
                            'dest_ip': event.dest_ip,
                        }
                    )
                    
                    if created:
                        alert.related_events.add(event)
                        alert.event_count = 1
                        if event.asset:
                            alert.affected_assets.add(event.asset)
                        alert.save()
                        alerts.append(alert)
        
        except Exception as e:
            print(f"Error checking IOCs: {e}")
        
        return alerts

    @staticmethod
    def check_suspicious_patterns(event):
        """
        Check for suspicious patterns and behavioral anomalies
        """
        alerts = []
        
        try:
            # Check for brute force patterns
            if event.action and event.action.lower() == 'failed':
                # Check for multiple failed attempts from same IP
                if event.source_ip:
                    failed_count = Event.objects.filter(
                        source_ip=event.source_ip,
                        action='failed',
                        time__gte=timezone.now() - timedelta(minutes=5)
                    ).count()
                    
                    if failed_count >= 5:
                        alert, created = Alert.objects.get_or_create(
                            name='Brute Force Attack Detected',
                            first_seen=event.time,
                            defaults={
                                'description': f'Multiple failed login attempts from {event.source_ip}',
                                'severity': 'high',
                                'status': 'new',
                                'source_ip': event.source_ip,
                                'dest_ip': event.dest_ip,
                            }
                        )
                        
                        if created:
                            alert.related_events.add(event)
                            alert.event_count = failed_count
                            if event.asset:
                                alert.affected_assets.add(event.asset)
                            alert.save()
                            alerts.append(alert)
            
            # Check for port scanning patterns
            if event.event_type and 'port_scan' in event.event_type.lower():
                alert, created = Alert.objects.get_or_create(
                    name='Port Scan Detected',
                    first_seen=event.time,
                    defaults={
                        'description': f'Port scan activity detected from {event.source_ip}',
                        'severity': 'medium',
                        'status': 'new',
                        'source_ip': event.source_ip,
                        'dest_ip': event.dest_ip,
                    }
                )
                
                if created:
                    alert.related_events.add(event)
                    alert.event_count = 1
                    if event.asset:
                        alert.affected_assets.add(event.asset)
                    alert.save()
                    alerts.append(alert)
            
            # Check for data exfiltration patterns
            if event.event_type and 'exfil' in event.event_type.lower():
                alert, created = Alert.objects.get_or_create(
                    name='Potential Data Exfiltration',
                    first_seen=event.time,
                    defaults={
                        'description': f'Suspicious data transfer detected on {event.asset.hostname if event.asset else "unknown asset"}',
                        'severity': 'critical',
                        'status': 'new',
                        'source_ip': event.source_ip,
                        'dest_ip': event.dest_ip,
                    }
                )
                
                if created:
                    alert.related_events.add(event)
                    alert.event_count = 1
                    if event.asset:
                        alert.affected_assets.add(event.asset)
                    alert.save()
                    alerts.append(alert)
            
            # Check for privilege escalation
            if event.event_type and 'privilege' in event.event_type.lower():
                alert, created = Alert.objects.get_or_create(
                    name='Privilege Escalation Attempt',
                    first_seen=event.time,
                    defaults={
                        'description': f'Unauthorized privilege escalation detected for user {event.username or "unknown"}',
                        'severity': 'critical',
                        'status': 'new',
                        'source_ip': event.source_ip,
                        'dest_ip': event.dest_ip,
                    }
                )
                
                if created:
                    alert.related_events.add(event)
                    alert.event_count = 1
                    if event.asset:
                        alert.affected_assets.add(event.asset)
                    alert.save()
                    alerts.append(alert)
        
        except Exception as e:
            print(f"Error checking suspicious patterns: {e}")
        
        return alerts

    @staticmethod
    def map_mitre_techniques(event):
        """
        Map events to MITRE ATT&CK techniques
        """
        try:
            # Simple mapping based on event type and severity
            if not event.event_type:
                return
            
            event_type_lower = event.event_type.lower()
            
            # Define event type to MITRE technique mappings
            mappings = {
                'brute_force': 'T1110',
                'credential_access': 'T1110',
                'discovery': 'T1087',
                'execution': 'T1053',
                'persistence': 'T1547',
                'privilege_escalation': 'T1548',
                'defense_evasion': 'T1562',
                'credential_dumping': 'T1003',
                'lateral_movement': 'T1570',
                'collection': 'T1123',
                'exfiltration': 'T1041',
                'command_control': 'T1071',
                'impact': 'T1531',
            }
            
            for event_keyword, technique_id in mappings.items():
                if event_keyword in event_type_lower:
                    try:
                        technique = MitreTechnique.objects.get(technique_id=technique_id)
                        MITREMapping.objects.get_or_create(
                            technique=technique,
                            event=event,
                            defaults={'confidence': 0.7}
                        )
                    except MitreTechnique.DoesNotExist:
                        pass
        
        except Exception as e:
            print(f"Error mapping MITRE techniques: {e}")

    @staticmethod
    def bulk_process_events(events):
        """
        Process multiple events in batch
        """
        all_alerts = []
        
        for event in events:
            alerts = AlertGenerator.process_event(event)
            all_alerts.extend(alerts)
        
        return all_alerts

    @staticmethod
    def correlate_alerts(hours=24):
        """
        Correlate related alerts from the same source/asset
        """
        time_threshold = timezone.now() - timedelta(hours=hours)
        
        # Group alerts by asset and severity
        alert_groups = Alert.objects.filter(
            created__gte=time_threshold,
            status__in=['new', 'investigating']
        ).values('asset', 'severity').annotate(count=Count('id'))
        
        correlations = []
        
        for group in alert_groups:
            if group['count'] > 3:
                correlations.append({
                    'asset_id': group['asset'],
                    'severity': group['severity'],
                    'alert_count': group['count'],
                    'timeframe': f'Last {hours} hours',
                })
        
        return correlations

    @staticmethod
    def get_alert_summary(days=7):
        """
        Get alert statistics and summary
        """
        time_threshold = timezone.now() - timedelta(days=days)
        
        alerts = Alert.objects.filter(created__gte=time_threshold)
        
        summary = {
            'total_alerts': alerts.count(),
            'by_severity': dict(
                alerts.values('severity').annotate(count=Count('id')).values_list('severity', 'count')
            ),
            'by_status': dict(
                alerts.values('status').annotate(count=Count('id')).values_list('status', 'count')
            ),
            'by_asset': list(
                alerts.values('asset__hostname').annotate(count=Count('id')).order_by('-count')[:10]
            ),
            'avg_resolution_time': None,  # Could be calculated if resolved_at is available
        }
        
        return summary
