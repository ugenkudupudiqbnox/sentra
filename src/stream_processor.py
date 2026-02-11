import json
import time
from typing import Dict, Any
from parse_auth_log import parse_line, enrich_signal_with_ai, calculate_risk_score
from schema import SecuritySignal, UserEntity, HostEntity, ProcessEntity, NetworkEntity, ComplianceTag
from storage import StorageFactory

class StreamProcessor:
    """
    Phase 1/2: Real-time signal processor.
    In production, this would be a Kafka consumer or Flink job.
    """
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.ch_storage = StorageFactory.get_storage("ClickHouse")
        self.es_storage = StorageFactory.get_storage("Elastic")

    def process_message(self, raw_log_line: str):
        """Processes a single log line into a signal and persists it."""
        event = parse_line(raw_log_line)
        if not event:
            return

        signal = None
        if event['type'] == 'ssh_login':
            signal = SecuritySignal(
                tenant_id=self.tenant_id,
                signal_type="ssh_login",
                severity="Low",
                user=UserEntity(username=event['user']),
                host=HostEntity(hostname=event['hostname'], ip=event['ip']),
                network=NetworkEntity(source_ip=event['ip'])
            )
        elif event['type'] == 'privilege_escalation':
            # Simplified metadata for stream demonstration
            signal = SecuritySignal(
                tenant_id=self.tenant_id,
                signal_type="privilege_escalation",
                severity="Medium",
                user=UserEntity(username=event['user']),
                host=HostEntity(hostname=event['hostname']),
                process=ProcessEntity(name=event.get('command', 'unknown'))
            )

        if signal:
            signal.risk_score = calculate_risk_score(signal.signal_type, signal.severity)
            enriched_signal = enrich_signal_with_ai(signal)
            
            # Persist to multi-engine storage
            self.ch_storage.ingest(enriched_signal)
            self.es_storage.ingest(enriched_signal)
            
            print(f"[STREAM] Processed {signal.signal_type} for {self.tenant_id}")

    def run_simulated(self, sample_logs: list):
        """Simulates ingestion from a stream."""
        print(f"Starting stream processor for tenant: {self.tenant_id}")
        for line in sample_logs:
            self.process_message(line)
            time.sleep(0.5) # Simulate stream delay

if __name__ == "__main__":
    # Test sample
    samples = [
        "2026-02-11T12:00:00.123456+00:00 host1 sshd[123]: Accepted publickey for stpi from 1.2.3.4",
        "2026-02-11T12:05:01.654321+00:00 host1 sudo: stpi : USER=root ; COMMAND=/usr/bin/apt update"
    ]
    processor = StreamProcessor(tenant_id="braoucloud-prod")
    processor.run_simulated(samples)
