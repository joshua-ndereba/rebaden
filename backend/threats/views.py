from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ThreatLog, BlockedIP
from .serializers import ThreatLogSerializer, BlockedIPSerializer
from .ai_engine import AIAssistant, AnomalyDetector
import json

class ThreatLogViewSet(viewsets.ModelViewSet):
    queryset = ThreatLog.objects.all().order_by('-timestamp')
    serializer_class = ThreatLogSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Manually trigger AI analysis for a specific log"""
        log = self.get_object()
        assistant = AIAssistant(provider='ollama') # Or 'openai' based on env
        
        # Construct log message
        log_message = f"IP: {log.ip_address}, URL: {log.url}, Method: {log.method}, Body: {log.body}"
        
        analysis = assistant.analyze_log(log_message)
        
        log.details = analysis
        log.save()
        
        return Response({'status': 'analyzed', 'analysis': analysis})

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get statistics for the dashboard"""
        total_threats = ThreatLog.objects.count()
        high_severity = ThreatLog.objects.filter(severity__in=['HIGH', 'CRITICAL']).count()
        blocked_ips = BlockedIP.objects.count()
        
        return Response({
            'total_threats': total_threats,
            'high_severity_threats': high_severity,
            'blocked_ips': blocked_ips
        })

class BlockedIPViewSet(viewsets.ModelViewSet):
    queryset = BlockedIP.objects.all().order_by('-blocked_at')
    serializer_class = BlockedIPSerializer
    permission_classes = [IsAuthenticated]
