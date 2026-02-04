# 🤖 AI, Kafka & Ollama Integration Guide

This guide details how to integrate **Ollama (Local LLM)** and **Kafka (Event Streaming)** into the DERE SIEM project, alongside the existing AI capabilities.

---

## 🧠 Ollama Integration (Local AI)

Ollama allows running large language models locally, providing privacy and reducing costs compared to cloud APIs like OpenAI.

### Why Ollama?
1.  **Privacy**: Sensitive logs never leave your infrastructure.
2.  **Cost**: Free to run (requires hardware resources).
3.  **Latency**: Can be faster for local network inference.

### Setup
1.  **Install Ollama**: Follow instructions at [ollama.com](https://ollama.com).
2.  **Pull a Model**:
    ```bash
    ollama pull llama3
    # or for faster/smaller models:
    ollama pull mistral
    ```
3.  **Python Integration**:
    The `threats/ai_engine.py` is already configured to support Ollama.
    
    ```python
    from threats.ai_engine import AIAssistant
    
    # Initialize with Ollama
    assistant = AIAssistant(provider='ollama')
    
    analysis = assistant.analyze_log("Suspicious failed login from 192.168.1.50")
    print(analysis)
    ```

---

## 📨 Kafka Integration (High-Throughput Streaming)

Kafka is used to ingest massive amounts of logs from various sources (firewalls, servers, routers) without overwhelming the database or the AI engine.

### Why Kafka?
1.  **Decoupling**: Log producers don't need to wait for the SIEM to process logs.
2.  **Buffering**: Handles traffic spikes (e.g., during a DDoS attack) without crashing.
3.  **Real-time**: Enables stream processing for immediate threat detection.

### Architecture
1.  **Producers**: Agents on servers send logs to Kafka topic `threat-logs`.
2.  **Consumer**: Django background worker (Celery or standalone script) reads from `threat-logs`.
3.  **Processing**:
    -   Consumer decodes JSON log.
    -   Sends high-severity logs to **Ollama** for analysis.
    -   Runs **Anomaly Detection** (Scikit-learn).
    -   Saves to Postgres database.

### Setup
1.  **Install Kafka**: Use Docker or local install.
    ```bash
    # Docker Compose example
    services:
      zookeeper:
        image: confluentinc/cp-zookeeper:latest
        environment:
          ZOOKEEPER_CLIENT_PORT: 2181
          
      kafka:
        image: confluentinc/cp-kafka:latest
        depends_on: [zookeeper]
        ports: ["9092:9092"]
        environment:
          KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
          KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
          KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ```
2.  **Run Consumer**:
    You can run the consumer as a management command (needs to be implemented) or a standalone script.
    
    *Example Management Command (`threats/management/commands/run_kafka.py`):*
    ```python
    from django.core.management.base import BaseCommand
    from threats.kafka_consumer import ThreatLogConsumer

    class Command(BaseCommand):
        help = 'Runs the Kafka consumer for threat logs'

        def handle(self, *args, **options):
            consumer = ThreatLogConsumer()
            consumer.start_listening()
    ```

---

## 🛠️ Combined Workflow

1.  **Log Generation**: A firewall detects a port scan.
2.  **Ingestion**: Log is sent to Kafka `threat-logs`.
3.  **Consumption**: `ThreatLogConsumer` picks up the message.
4.  **AI Analysis**:
    -   `AnomalyDetector` checks if this IP has unusual behavior.
    -   `AIAssistant` (Ollama) analyzes the payload for specific exploit signatures.
5.  **Action**:
    -   If Score > Threshold: Block IP automatically.
    -   Alert saved to DB.
    -   Dashboard updates in real-time.

## 📦 Requirements
Ensure these are in your `requirements.txt`:
-   `kafka-python`
-   `ollama`
-   `scikit-learn`
-   `numpy`
-   `pandas`
