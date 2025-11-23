"""
Report Generator for SIEM
Generates various security reports in different formats
"""

import json
import csv
from io import StringIO, BytesIO
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q
from .models import Event, Alert, Investigation, IOC, Asset, AnomalyDetection


class ReportGenerator:
    """Generate security reports"""
    
    @staticmethod
    def generate_security_summary(start_date=None, end_date=None):
        """Generate security summary report"""
        if not end_date:
            end_date = timezone.now()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        # Gather statistics
        total_events = Event.objects.filter(time__range=[start_date, end_date]).count()
        
        events_by_severity = Event.objects.filter(
            time__range=[start_date, end_date]
        ).values('severity').annotate(count=Count('id'))
        
        events_by_category = Event.objects.filter(
            time__range=[start_date, end_date]
        ).values('category').annotate(count=Count('id'))
        
        total_alerts = Alert.objects.filter(first_seen__range=[start_date, end_date]).count()
        critical_alerts = Alert.objects.filter(
            first_seen__range=[start_date, end_date],
            severity='critical'
        ).count()
        
        open_investigations = Investigation.objects.filter(
            created__range=[start_date, end_date],
            status__in=['new', 'open', 'in_progress']
        ).count()
        
        top_source_ips = Event.objects.filter(
            time__range=[start_date, end_date],
            source_ip__isnull=False
        ).values('source_ip').annotate(count=Count('id')).order_by('-count')[:10]
        
        top_targets = Event.objects.filter(
            time__range=[start_date, end_date],
            dest_ip__isnull=False
        ).values('dest_ip').annotate(count=Count('id')).order_by('-count')[:10]
        
        return {
            'report_type': 'Security Summary',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
            },
            'summary': {
                'total_events': total_events,
                'total_alerts': total_alerts,
                'critical_alerts': critical_alerts,
                'open_investigations': open_investigations,
            },
            'events_by_severity': list(events_by_severity),
            'events_by_category': list(events_by_category),
            'top_source_ips': list(top_source_ips),
            'top_targets': list(top_targets),
            'generated_at': timezone.now().isoformat(),
        }
    
    @staticmethod
    def generate_incident_response_report(investigation_id=None):
        """Generate incident response report"""
        if investigation_id:
            investigations = Investigation.objects.filter(id=investigation_id)
        else:
            # Last 30 days
            start_date = timezone.now() - timedelta(days=30)
            investigations = Investigation.objects.filter(created__gte=start_date)
        
        report_data = []
        for inv in investigations:
            report_data.append({
                'case_id': inv.case_id,
                'title': inv.title,
                'status': inv.status,
                'priority': inv.priority,
                'severity': inv.severity,
                'created': inv.created.isoformat(),
                'resolved_at': inv.resolved_at.isoformat() if inv.resolved_at else None,
                'alerts_count': inv.alerts.count(),
                'affected_assets_count': inv.affected_assets.count(),
                'notes_count': inv.notes.count(),
                'resolution': inv.resolution,
            })
        
        return {
            'report_type': 'Incident Response',
            'investigations': report_data,
            'total_investigations': len(report_data),
            'generated_at': timezone.now().isoformat(),
        }
    
    @staticmethod
    def generate_threat_intelligence_report(days=7):
        """Generate threat intelligence report"""
        start_date = timezone.now() - timedelta(days=days)
        
        # IOC statistics
        new_iocs = IOC.objects.filter(created__gte=start_date).count()
        active_iocs = IOC.objects.filter(is_active=True).count()
        
        iocs_by_type = IOC.objects.filter(
            is_active=True
        ).values('ioc_type').annotate(count=Count('id'))
        
        iocs_by_severity = IOC.objects.filter(
            is_active=True
        ).values('severity').annotate(count=Count('id'))
        
        # Recent high-severity IOCs
        high_severity_iocs = IOC.objects.filter(
            severity__in=['high', 'critical'],
            is_active=True
        ).order_by('-created')[:20].values(
            'ioc_type', 'value', 'threat_type', 'severity', 'created'
        )
        
        return {
            'report_type': 'Threat Intelligence',
            'period_days': days,
            'summary': {
                'new_iocs': new_iocs,
                'active_iocs': active_iocs,
            },
            'iocs_by_type': list(iocs_by_type),
            'iocs_by_severity': list(iocs_by_severity),
            'high_severity_iocs': list(high_severity_iocs),
            'generated_at': timezone.now().isoformat(),
        }
    
    @staticmethod
    def generate_compliance_report():
        """Generate compliance report"""
        from .models import ComplianceFramework, ComplianceCheck
        
        frameworks = ComplianceFramework.objects.filter(is_active=True)
        report_data = []
        
        for framework in frameworks:
            checks = ComplianceCheck.objects.filter(framework=framework)
            total_checks = checks.count()
            passed = checks.filter(last_result='pass').count()
            failed = checks.filter(last_result='fail').count()
            warnings = checks.filter(last_result='warning').count()
            
            compliance_rate = (passed / total_checks * 100) if total_checks > 0 else 0
            
            report_data.append({
                'framework': framework.name,
                'version': framework.version,
                'total_checks': total_checks,
                'passed': passed,
                'failed': failed,
                'warnings': warnings,
                'compliance_rate': round(compliance_rate, 2),
            })
        
        return {
            'report_type': 'Compliance',
            'frameworks': report_data,
            'generated_at': timezone.now().isoformat(),
        }
    
    @staticmethod
    def generate_user_activity_report(days=7):
        """Generate user activity report"""
        from .models import AuditLog
        
        start_date = timezone.now() - timedelta(days=days)
        
        # Activity by user
        activity_by_user = AuditLog.objects.filter(
            timestamp__gte=start_date
        ).values('user__username').annotate(count=Count('id')).order_by('-count')[:20]
        
        # Activity by action type
        activity_by_action = AuditLog.objects.filter(
            timestamp__gte=start_date
        ).values('action_type').annotate(count=Count('id'))
        
        # Recent critical actions
        critical_actions = AuditLog.objects.filter(
            timestamp__gte=start_date,
            action_type__in=['delete', 'update']
        ).order_by('-timestamp')[:50].values(
            'timestamp', 'user__username', 'action_type', 'resource_type', 'description'
        )
        
        return {
            'report_type': 'User Activity',
            'period_days': days,
            'activity_by_user': list(activity_by_user),
            'activity_by_action': list(activity_by_action),
            'critical_actions': list(critical_actions),
            'generated_at': timezone.now().isoformat(),
        }
    
    @staticmethod
    def generate_asset_inventory_report():
        """Generate asset inventory report"""
        total_assets = Asset.objects.count()
        active_assets = Asset.objects.filter(is_active=True).count()
        
        assets_by_type = Asset.objects.values('asset_type').annotate(count=Count('id'))
        assets_by_criticality = Asset.objects.values('criticality').annotate(count=Count('id'))
        
        high_risk_assets = Asset.objects.filter(
            risk_score__gte=50
        ).order_by('-risk_score')[:20].values(
            'hostname', 'ip', 'asset_type', 'criticality', 'risk_score', 'owner'
        )
        
        return {
            'report_type': 'Asset Inventory',
            'summary': {
                'total_assets': total_assets,
                'active_assets': active_assets,
            },
            'assets_by_type': list(assets_by_type),
            'assets_by_criticality': list(assets_by_criticality),
            'high_risk_assets': list(high_risk_assets),
            'generated_at': timezone.now().isoformat(),
        }
    
    @staticmethod
    def export_to_json(data):
        """Export report data to JSON"""
        return json.dumps(data, indent=2, default=str)
    
    @staticmethod
    def export_to_csv(data):
        """Export report data to CSV"""
        output = StringIO()
        
        # Write summary
        writer = csv.writer(output)
        writer.writerow(['Report Type', data.get('report_type', 'Unknown')])
        writer.writerow(['Generated At', data.get('generated_at', '')])
        writer.writerow([])
        
        # Write summary statistics
        if 'summary' in data:
            writer.writerow(['Summary Statistics'])
            for key, value in data['summary'].items():
                writer.writerow([key.replace('_', ' ').title(), value])
            writer.writerow([])
        
        # Write detailed data based on report type
        for key, value in data.items():
            if isinstance(value, list) and value:
                writer.writerow([key.replace('_', ' ').title()])
                if isinstance(value[0], dict):
                    # Write headers
                    headers = value[0].keys()
                    writer.writerow(headers)
                    # Write data
                    for item in value:
                        writer.writerow([item.get(h, '') for h in headers])
                writer.writerow([])
        
        return output.getvalue()
    
    @staticmethod
    def export_to_html(data):
        """Export report data to HTML"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{data.get('report_type', 'Report')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .summary {{ background-color: #e7f3ff; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>{data.get('report_type', 'Security Report')}</h1>
            <p><strong>Generated:</strong> {data.get('generated_at', '')}</p>
        """
        
        # Add summary
        if 'summary' in data:
            html += '<div class="summary"><h2>Summary</h2><ul>'
            for key, value in data['summary'].items():
                html += f'<li><strong>{key.replace("_", " ").title()}:</strong> {value}</li>'
            html += '</ul></div>'
        
        # Add tables for list data
        for key, value in data.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                html += f'<h2>{key.replace("_", " ").title()}</h2>'
                html += '<table><thead><tr>'
                
                # Headers
                for header in value[0].keys():
                    html += f'<th>{header.replace("_", " ").title()}</th>'
                html += '</tr></thead><tbody>'
                
                # Data
                for item in value:
                    html += '<tr>'
                    for val in item.values():
                        html += f'<td>{val}</td>'
                    html += '</tr>'
                html += '</tbody></table>'
        
        html += '</body></html>'
        return html
