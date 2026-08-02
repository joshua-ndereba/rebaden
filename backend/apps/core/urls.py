from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    
    # Core
    path('', views.index, name='index'),
    path('api/', views.api_home, name='api_home'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Events & Logs
    path('events/', views.events, name='events'),
    path('logs/', views.logs_view, name='logs'),
    
    # Alerts
    path('alerts/', views.alerts, name='alerts'),
    path('alerts/<int:alert_id>/', views.alert_detail, name='alert_detail'),
    

    
    # Threat Intelligence
    path('threat-intel/', views.threat_intel, name='threat_intel'),
    path('threat-intel/ioc/<int:ioc_id>/', views.ioc_detail, name='ioc_detail'),
    
    # Investigations & Incident Response
    path('investigations/', views.investigations, name='investigations'),
    path('investigations/<str:case_id>/', views.investigation_detail, name='investigation_detail'),
    path('playbooks/', views.playbooks, name='playbooks'),
    path('playbooks/<int:playbook_id>/', views.playbook_detail, name='playbook_detail'),
    
    # Detection & Correlation
    path('detection-rules/', views.detection_rules, name='detection_rules'),
    path('detection-rules/<int:rule_id>/', views.rule_detail, name='rule_detail'),
    
    # MITRE ATT&CK
    path('mitre-attack/', views.mitre_attack, name='mitre_attack'),
    path('mitre-attack/<str:technique_id>/', views.mitre_technique_detail, name='mitre_technique_detail'),
    

    
    # UEBA
    path('ueba/', views.ueba, name='ueba'),
    path('ueba/anomaly/<int:anomaly_id>/', views.anomaly_detail, name='anomaly_detail'),
    
    # Compliance
    path('compliance/', views.compliance, name='compliance'),
    path('compliance/<int:framework_id>/', views.compliance_framework_detail, name='compliance_framework_detail'),
    
    # Reports
    path('reports/', views.reports, name='reports'),

    # Admin Panel
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/user/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
    
    # Documentation / Help
    path('documentation/', views.documentation_page, name='documentation_page'),
    
    # User Profile & Account Management
    path('profile/', views.user_profile, name='user_profile'),
    
    # Advanced Search
    path('search/', views.advanced_search, name='advanced_search'),
    
    # Investigation Management
    path('investigations/create/', views.create_investigation, name='create_investigation'),
    
    # Reports & Export
    path('reports/generate/', views.generate_report_view, name='generate_report_view'),
    path('export/events/', views.export_events, name='export_events'),
    
    # API Endpoints
    path('api/events/', views.api_events, name='api_events'),
    path('api/alerts/stats/', views.api_alerts_stats, name='api_alerts_stats'),
    path('api/threat-map/', views.api_threat_map, name='api_threat_map'),
]