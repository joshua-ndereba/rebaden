"""
AI-Powered Investigation Assistant
Provides automated analysis and recommendations for security investigations
"""

import json
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from .models import Event, Alert, IOC, MitreTechnique, Investigation


class InvestigationAI:
    """AI assistant for security investigations"""
    
    @staticmethod
    def analyze_alert(alert):
        """Analyze an alert and provide investigation recommendations"""
        analysis = {
            'severity_assessment': InvestigationAI._assess_severity(alert),
            'related_events': InvestigationAI._find_related_events(alert),
            'ioc_matches': InvestigationAI._check_ioc_matches(alert),
            'mitre_mapping': InvestigationAI._map_to_mitre(alert),
            'recommended_actions': InvestigationAI._recommend_actions(alert),
            'investigation_priority': InvestigationAI._calculate_priority(alert),
            'timeline_analysis': InvestigationAI._analyze_timeline(alert),
            'threat_context': InvestigationAI._get_threat_context(alert),
        }
        return analysis
    
    @staticmethod
    def _assess_severity(alert):
        """Assess the true severity of an alert"""
        severity_score = 0
        factors = []
        
        # Base severity
        severity_map = {'low': 1, 'medium': 3, 'high': 7, 'critical': 10}
        severity_score += severity_map.get(alert.severity, 3)
        factors.append(f"Base severity: {alert.severity}")
        
        # Check for multiple related events
        event_count = alert.related_events.count()
        if event_count > 10:
            severity_score += 3
            factors.append(f"High event volume: {event_count} related events")
        elif event_count > 5:
            severity_score += 2
            factors.append(f"Moderate event volume: {event_count} related events")
        
        # Check for critical asset involvement
        critical_assets = alert.affected_assets.filter(criticality='critical').count()
        if critical_assets > 0:
            severity_score += 4
            factors.append(f"Critical assets affected: {critical_assets}")
        
        # Determine final assessment
        if severity_score >= 15:
            assessment = "CRITICAL - Immediate action required"
        elif severity_score >= 10:
            assessment = "HIGH - Urgent investigation needed"
        elif severity_score >= 6:
            assessment = "MEDIUM - Investigation recommended"
        else:
            assessment = "LOW - Monitor and review"
        
        return {
            'score': severity_score,
            'assessment': assessment,
            'factors': factors
        }
    
    @staticmethod
    def _find_related_events(alert):
        """Find events related to this alert"""
        related = []
        
        # Get events already linked to the alert
        linked_events = alert.related_events.all()[:10]
        
        # If alert has source IPs, find other events from same IPs
        source_ips = set()
        for event in linked_events:
            if event.source_ip:
                source_ips.add(event.source_ip)
        
        if source_ips:
            # Find other suspicious events from same IPs
            time_window = timezone.now() - timedelta(hours=24)
            similar_events = Event.objects.filter(
                source_ip__in=source_ips,
                time__gte=time_window,
                severity__in=['high', 'critical']
            ).exclude(
                id__in=[e.id for e in linked_events]
            )[:10]
            
            for event in similar_events:
                related.append({
                    'event': event,
                    'reason': f'Same source IP: {event.source_ip}',
                    'relevance': 'high'
                })
        
        return related
    
    @staticmethod
    def _check_ioc_matches(alert):
        """Check for IOC matches in alert events"""
        matches = []
        
        # Get active IOCs
        active_iocs = IOC.objects.filter(is_active=True)
        
        # Check events for IOC matches
        for event in alert.related_events.all():
            message = event.message.lower()
            raw_log = event.raw_log.lower()
            
            for ioc in active_iocs:
                ioc_value = ioc.value.lower()
                
                if ioc_value in message or ioc_value in raw_log:
                    matches.append({
                        'ioc': ioc,
                        'type': ioc.ioc_type,
                        'value': ioc.value,
                        'severity': ioc.severity,
                        'description': ioc.description,
                        'event_id': event.id
                    })
        
        return matches
    
    @staticmethod
    def _map_to_mitre(alert):
        """Map alert to MITRE ATT&CK techniques"""
        mappings = []
        
        # Check if alert already has MITRE techniques
        existing_techniques = alert.mitre_techniques.all()
        if existing_techniques:
            for technique in existing_techniques:
                mappings.append({
                    'technique_id': technique.technique_id,
                    'name': technique.name,
                    'tactic': technique.tactic.name if technique.tactic else 'Unknown',
                    'confidence': 'high'
                })
        
        # Attempt to infer MITRE techniques from alert name/description
        alert_text = (alert.name + ' ' + alert.description).lower()
        
        # Simple keyword-based mapping
        technique_keywords = {
            'T1110': ['brute force', 'password spray', 'credential stuffing'],
            'T1190': ['exploit', 'vulnerability', 'sql injection', 'xss'],
            'T1059': ['command injection', 'powershell', 'cmd.exe', 'bash'],
            'T1071': ['command and control', 'c2', 'callback'],
            'T1087': ['account discovery', 'enumeration'],
            'T1046': ['network service scanning', 'port scan'],
            'T1566': ['phishing', 'malicious email'],
            'T1486': ['ransomware', 'encryption'],
            'T1003': ['credential dumping', 'mimikatz'],
            'T1021': ['remote services', 'psexec', 'rdp'],
        }
        
        for technique_id, keywords in technique_keywords.items():
            for keyword in keywords:
                if keyword in alert_text:
                    try:
                        technique = MitreTechnique.objects.get(technique_id=technique_id)
                        if technique not in existing_techniques:
                            mappings.append({
                                'technique_id': technique.technique_id,
                                'name': technique.name,
                                'tactic': technique.tactic.name if technique.tactic else 'Unknown',
                                'confidence': 'medium'
                            })
                    except MitreTechnique.DoesNotExist:
                        pass
                    break
        
        return mappings
    
    @staticmethod
    def _recommend_actions(alert):
        """Recommend investigation and response actions"""
        actions = []
        
        # Severity-based actions
        if alert.severity in ['critical', 'high']:
            actions.append({
                'priority': 1,
                'action': 'Isolate affected systems',
                'description': 'Immediately isolate affected assets to prevent lateral movement',
                'category': 'containment'
            })
            actions.append({
                'priority': 2,
                'action': 'Collect forensic evidence',
                'description': 'Capture memory dumps, disk images, and network traffic',
                'category': 'investigation'
            })
        
        # Alert type-based actions
        alert_name = alert.name.lower()
        
        if 'brute force' in alert_name or 'password' in alert_name:
            actions.append({
                'priority': 3,
                'action': 'Reset compromised credentials',
                'description': 'Force password reset for affected accounts',
                'category': 'remediation'
            })
            actions.append({
                'priority': 4,
                'action': 'Enable MFA',
                'description': 'Implement multi-factor authentication for affected accounts',
                'category': 'prevention'
            })
        
        if 'sql injection' in alert_name or 'xss' in alert_name:
            actions.append({
                'priority': 3,
                'action': 'Patch vulnerable application',
                'description': 'Apply security patches or implement input validation',
                'category': 'remediation'
            })
            actions.append({
                'priority': 4,
                'action': 'Review application logs',
                'description': 'Check for data exfiltration or unauthorized access',
                'category': 'investigation'
            })
        
        if 'malware' in alert_name or 'trojan' in alert_name:
            actions.append({
                'priority': 3,
                'action': 'Run antivirus scan',
                'description': 'Perform full system scan with updated signatures',
                'category': 'remediation'
            })
            actions.append({
                'priority': 4,
                'action': 'Check for persistence mechanisms',
                'description': 'Examine startup items, scheduled tasks, and registry keys',
                'category': 'investigation'
            })
        
        if 'port scan' in alert_name or 'reconnaissance' in alert_name:
            actions.append({
                'priority': 3,
                'action': 'Block source IP',
                'description': 'Add source IP to firewall blocklist',
                'category': 'containment'
            })
            actions.append({
                'priority': 4,
                'action': 'Review firewall rules',
                'description': 'Ensure only necessary ports are exposed',
                'category': 'prevention'
            })
        
        # Generic actions
        actions.append({
            'priority': 5,
            'action': 'Document findings',
            'description': 'Create detailed investigation notes and timeline',
            'category': 'documentation'
        })
        
        actions.append({
            'priority': 6,
            'action': 'Notify stakeholders',
            'description': 'Inform security team and management of incident',
            'category': 'communication'
        })
        
        return sorted(actions, key=lambda x: x['priority'])
    
    @staticmethod
    def _calculate_priority(alert):
        """Calculate investigation priority"""
        score = 0
        
        # Severity weight
        severity_weights = {'low': 1, 'medium': 3, 'high': 7, 'critical': 10}
        score += severity_weights.get(alert.severity, 3)
        
        # Age factor (newer alerts get higher priority)
        age_hours = (timezone.now() - alert.first_seen).total_seconds() / 3600
        if age_hours < 1:
            score += 5
        elif age_hours < 6:
            score += 3
        elif age_hours < 24:
            score += 1
        
        # Event volume
        event_count = alert.related_events.count()
        if event_count > 50:
            score += 4
        elif event_count > 20:
            score += 2
        elif event_count > 10:
            score += 1
        
        # Determine priority level
        if score >= 15:
            return {'level': 'P1 - Critical', 'score': score, 'sla': '15 minutes'}
        elif score >= 10:
            return {'level': 'P2 - High', 'score': score, 'sla': '1 hour'}
        elif score >= 6:
            return {'level': 'P3 - Medium', 'score': score, 'sla': '4 hours'}
        else:
            return {'level': 'P4 - Low', 'score': score, 'sla': '24 hours'}
    
    @staticmethod
    def _analyze_timeline(alert):
        """Analyze event timeline"""
        events = alert.related_events.order_by('time')
        
        if not events:
            return {'summary': 'No events in timeline', 'events': []}
        
        timeline = []
        for event in events[:20]:  # Limit to 20 events
            timeline.append({
                'time': event.time,
                'source': event.source,
                'source_ip': event.source_ip,
                'message': event.message[:100],  # Truncate long messages
                'severity': event.severity
            })
        
        # Calculate timeline span
        first_event = events.first()
        last_event = events.last()
        duration = (last_event.time - first_event.time).total_seconds()
        
        summary = f"Timeline spans {duration/60:.1f} minutes with {events.count()} events"
        
        return {
            'summary': summary,
            'first_event': first_event.time,
            'last_event': last_event.time,
            'duration_minutes': duration / 60,
            'event_count': events.count(),
            'events': timeline
        }
    
    @staticmethod
    def _get_threat_context(alert):
        """Get threat intelligence context"""
        context = {
            'threat_actors': [],
            'campaigns': [],
            'recommendations': []
        }
        
        # Check for known threat actor patterns
        alert_text = (alert.name + ' ' + alert.description).lower()
        
        if 'ransomware' in alert_text:
            context['threat_actors'].append('Ransomware operators')
            context['campaigns'].append('Ransomware campaign')
            context['recommendations'].append('Implement offline backups')
            context['recommendations'].append('Disable macro execution')
        
        if 'apt' in alert_text or 'advanced persistent' in alert_text:
            context['threat_actors'].append('APT group')
            context['campaigns'].append('Targeted attack')
            context['recommendations'].append('Conduct full network sweep')
            context['recommendations'].append('Review access logs for lateral movement')
        
        if 'phishing' in alert_text:
            context['threat_actors'].append('Phishing group')
            context['campaigns'].append('Credential harvesting')
            context['recommendations'].append('User security awareness training')
            context['recommendations'].append('Implement email filtering')
        
        return context
    
    @staticmethod
    def generate_investigation_report(investigation):
        """Generate an AI-assisted investigation report"""
        report = {
            'case_id': investigation.case_id,
            'title': investigation.title,
            'status': investigation.status,
            'priority': investigation.priority,
            'summary': '',
            'key_findings': [],
            'timeline': [],
            'recommendations': [],
            'next_steps': []
        }
        
        # Analyze all alerts in the investigation
        for alert in investigation.alerts.all():
            analysis = InvestigationAI.analyze_alert(alert)
            
            # Add key findings
            if analysis['ioc_matches']:
                report['key_findings'].append(f"IOC matches found: {len(analysis['ioc_matches'])} indicators")
            
            if analysis['mitre_mapping']:
                techniques = ', '.join([m['technique_id'] for m in analysis['mitre_mapping'][:3]])
                report['key_findings'].append(f"MITRE techniques: {techniques}")
            
            # Add recommendations
            for action in analysis['recommended_actions'][:5]:
                if action not in report['recommendations']:
                    report['recommendations'].append(action['action'])
        
        # Generate summary
        alert_count = investigation.alerts.count()
        asset_count = investigation.affected_assets.count()
        report['summary'] = f"Investigation involves {alert_count} alerts affecting {asset_count} assets. "
        report['summary'] += f"Priority: {investigation.priority}. Status: {investigation.status}."
        
        return report

    @staticmethod
    def generate_dashboard_insights(time_window):
        """Generate AI-powered insights for dashboard display"""
        from .models import Event, Alert, IOC

        insights = {
            'threat_summary': '',
            'risk_assessment': 'low',
            'key_findings': [],
            'recommendations': [],
            'correlations': []
        }

        # Analyze recent events for patterns
        recent_events = Event.objects.filter(time__gte=time_window)
        event_count = recent_events.count()

        if event_count == 0:
            insights['threat_summary'] = "No security events detected in the last 24 hours."
            return insights

        # Analyze attack patterns
        attack_types = recent_events.values('event_type').annotate(
            count=Count('id')
        ).order_by('-count')

        # Check for brute force patterns
        brute_force_events = recent_events.filter(event_type='brute_force').count()
        if brute_force_events > 10:
            insights['key_findings'].append(f"Brute force attack detected: {brute_force_events} attempts")
            insights['risk_assessment'] = 'high'
            insights['recommendations'].append("Implement account lockout policies")

        # Check for SQL injection patterns
        sql_injection = recent_events.filter(event_type='sql_injection').count()
        if sql_injection > 0:
            insights['key_findings'].append(f"SQL injection attempts: {sql_injection}")
            insights['risk_assessment'] = max(insights['risk_assessment'], 'medium')
            insights['recommendations'].append("Review input validation and WAF rules")

        # Check for port scanning
        port_scans = recent_events.filter(event_type='port_scan').count()
        if port_scans > 20:
            insights['key_findings'].append(f"Port scanning activity: {port_scans} attempts")
            insights['recommendations'].append("Review firewall rules and network segmentation")

        # Analyze source IP patterns
        top_attackers = recent_events.values('source_ip').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        if len(top_attackers) > 0:
            top_attacker = top_attackers[0]
            if top_attacker['count'] > 50:
                insights['key_findings'].append(f"High activity from {top_attacker['source_ip']}: {top_attacker['count']} events")
                insights['correlations'].append(f"Investigate source IP {top_attacker['source_ip']} for coordinated attacks")

        # Generate threat summary
        if insights['risk_assessment'] == 'high':
            insights['threat_summary'] = f"High threat activity detected. {event_count} security events in the last 24 hours."
        elif insights['risk_assessment'] == 'medium':
            insights['threat_summary'] = f"Moderate threat activity. {event_count} security events require attention."
        else:
            insights['threat_summary'] = f"Normal activity with {event_count} security events logged."

        # Add general recommendations if none specific
        if not insights['recommendations']:
            insights['recommendations'].append("Continue monitoring for emerging threats")
            insights['recommendations'].append("Review recent alerts for false positives")

        return insights
