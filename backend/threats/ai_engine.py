import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class BehaviorAnalyzer:
    """Analyze user behavior patterns"""
    
    def __init__(self):
        self.clusterer = DBSCAN(eps=0.5, min_samples=5)
    
    def analyze_user_behavior(self, user_events):
        """Detect unusual user behavior"""
        if len(user_events) < 5:
            return []
        
        # Extract behavior features
        features = []
        for event in user_events:
            # Simple feature extraction for demo
            features.append([
                event.get('timestamp').hour if event.get('timestamp') else 0,
                len(event.get('url', ''))
            ])
        
        features = np.array(features)
        if len(features) == 0:
            return []

        # Cluster behaviors
        clusters = self.clusterer.fit_predict(features)
        
        # Find outliers (cluster -1)
        anomalies = []
        for i, cluster in enumerate(clusters):
            if cluster == -1:
                anomalies.append({
                    'event': user_events[i],
                    'reason': 'Unusual behavior pattern detected'
                })
        
        return anomalies

class AnomalyDetector:
    """Detect anomalies in security events using machine learning"""
    
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def extract_features(self, events):
        """Extract numerical features from events"""
        features = []
        
        for event in events:
            # Handle both dict and object access
            get_val = lambda x, k: x.get(k) if isinstance(x, dict) else getattr(x, k, None)
            
            timestamp = get_val(event, 'timestamp')
            severity = get_val(event, 'severity')
            threat_type = get_val(event, 'threat_type')
            ip_address = get_val(event, 'ip_address')
            
            feature_vector = [
                # Time-based features
                timestamp.hour if timestamp else 0,
                timestamp.weekday() if timestamp else 0,
                
                # Severity encoding
                {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}.get(severity, 0),
                
                # Category encoding
                hash(threat_type) % 100 if threat_type else 0,
                
                # IP-based features
                int(ip_address.split('.')[-1]) if ip_address and '.' in ip_address else 0,
            ]
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def train(self, events):
        """Train the anomaly detection model"""
        if len(events) < 10: # Reduced for demo purposes, usually 100+
            return False
        
        features = self.extract_features(events)
        if len(features) == 0:
            return False
            
        features_scaled = self.scaler.fit_transform(features)
        
        self.model.fit(features_scaled)
        self.is_trained = True
        
        return True
    
    def predict(self, events):
        """Predict anomalies in new events"""
        if not self.is_trained:
            return []
        
        features = self.extract_features(events)
        if len(features) == 0:
            return []
            
        features_scaled = self.scaler.transform(features)
        
        predictions = self.model.predict(features_scaled)
        scores = self.model.score_samples(features_scaled)
        
        anomalies = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:  # Anomaly detected
                anomalies.append({
                    'event': events[i],
                    'anomaly_score': abs(score),
                    'confidence': min(abs(score) * 100, 100)
                })
        
        return anomalies

class ThreatClassifier:
    """Classify threats using machine learning"""
    
    def __init__(self):
        self.model = MultinomialNB()
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.is_trained = False
    
    def train(self, events_with_labels):
        """Train threat classifier"""
        if len(events_with_labels) < 10:
            return False
        
        messages = [e['body'] or '' for e, _ in events_with_labels]
        labels = [label for _, label in events_with_labels]
        
        if not messages:
            return False

        X = self.vectorizer.fit_transform(messages)
        self.model.fit(X, labels)
        self.is_trained = True
        
        return True
    
    def predict(self, events):
        """Predict threat type for events"""
        if not self.is_trained:
            return []
        
        messages = [e.get('body', '') or '' for e in events]
        X = self.vectorizer.transform(messages)
        
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        
        results = []
        for i, (pred, probs) in enumerate(zip(predictions, probabilities)):
            results.append({
                'event': events[i],
                'threat_type': pred,
                'confidence': max(probs) * 100
            })
        
        return results

class AIAssistant:
    """AI-powered assistant for SIEM (using OpenAI or Ollama)"""
    
    def __init__(self, provider='openai'):
        self.provider = provider
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = None
        
        if self.provider == 'openai' and self.api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                pass
        elif self.provider == 'ollama':
            try:
                import ollama
                self.client = ollama
            except ImportError:
                pass
    
    def analyze_log(self, log_message):
        """Analyze a log message"""
        prompt = f"Analyze this security log and identify any threats or concerns:\n\n{log_message}"
        
        if self.provider == 'ollama':
            try:
                response = self.client.chat(model='llama3', messages=[
                    {'role': 'user', 'content': prompt},
                ])
                return response['message']['content']
            except Exception as e:
                return f"Ollama Error: {str(e)}"
        
        elif self.client: # OpenAI
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a cybersecurity expert analyzing security logs."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"OpenAI Error: {str(e)}"
        
        return "No AI provider configured"
