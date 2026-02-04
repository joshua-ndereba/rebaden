import json
import logging
from kafka import KafkaConsumer
from django.conf import settings
from .models import ThreatLog
from .ai_engine import AnomalyDetector, AIAssistant

logger = logging.getLogger(__name__)

class ThreatLogConsumer:
    """
    Kafka Consumer for processing threat logs in real-time.
    """
    def __init__(self, topic='threat-logs'):
        self.topic = topic
        self.consumer = None
        self.ai_detector = AnomalyDetector()
        self.ai_assistant = AIAssistant(provider='ollama') # Use Ollama for local processing
        
        # Try to initialize Kafka consumer
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='threat-detection-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {e}")

    def start_listening(self):
        """Start consuming messages"""
        if not self.consumer:
            logger.warning("Kafka consumer not initialized. Skipping.")
            return

        logger.info(f"Listening for threat logs on topic: {self.topic}")
        
        for message in self.consumer:
            log_data = message.value
            self.process_log(log_data)

    def process_log(self, log_data):
        """Process a single log entry"""
        try:
            # 1. Basic validation
            if not log_data.get('ip_address'):
                return

            # 2. AI Analysis (Ollama)
            # For high throughput, you might only send suspicious logs to AI
            ai_analysis = ""
            if log_data.get('severity') in ['HIGH', 'CRITICAL']:
                ai_analysis = self.ai_assistant.analyze_log(json.dumps(log_data))

            # 3. Anomaly Detection (if model is trained)
            # In a real app, you'd load a pre-trained model
            # anomalies = self.ai_detector.predict([log_data])
            
            # 4. Save to DB
            ThreatLog.objects.create(
                ip_address=log_data.get('ip_address'),
                url=log_data.get('url', ''),
                method=log_data.get('method', 'GET'),
                headers=log_data.get('headers', {}),
                body=log_data.get('body', ''),
                threat_type=log_data.get('threat_type', 'Unknown'),
                severity=log_data.get('severity', 'LOW'),
                ai_confidence=0.8, # Placeholder
                action_taken=log_data.get('action_taken', 'FLAGGED'),
                details=ai_analysis or "Processed via Kafka"
            )
            
        except Exception as e:
            logger.error(f"Error processing log: {e}")
