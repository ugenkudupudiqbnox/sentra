from abc import ABC, abstractmethod
from typing import List, Dict, Any
import json
import requests
from schema import SecuritySignal

class BaseStorage(ABC):
    @abstractmethod
    def ingest(self, signal: SecuritySignal):
        pass

    @abstractmethod
    def query(self, tenant_id: str, query: str) -> List[Dict[str, Any]]:
        pass

class ClickHouseStorage(BaseStorage):
    """Handles analytical queries and high-volume signal ingestion."""
    def __init__(self, host: str = "localhost", port: int = 8123):
        self.url = f"http://{host}:{port}"

    def ingest(self, signal: SecuritySignal):
        """Phase 2: Ingest flattened signal into ClickHouse."""
        # Flat dictionary mapping to db_setup.sql columns
        flattened = {
            "id": signal.id,
            "tenant_id": signal.tenant_id,
            "schema_version": signal.schema_version,
            "timestamp": signal.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "signal_type": signal.signal_type,
            "severity": signal.severity,
            "risk_score": signal.risk_score,
            "user_username": signal.user.username if signal.user else "unknown",
            "host_hostname": signal.host.hostname if signal.host else "unknown",
            "host_ip": str(signal.host.ip) if signal.host and signal.host.ip else "0.0.0.0",
            "process_name": signal.process.name if signal.process else "unknown",
            "network_source_ip": str(signal.network.source_ip) if signal.network and signal.network.source_ip else "0.0.0.0",
            "ai_confidence": signal.ai_confidence,
            "model_name": signal.model_info.get("model", "unknown"),
            "mitre_ttps": signal.mitre_ttps,
            "compliance_controls": [tag.control_id for tag in signal.compliance_tags]
        }
        
        print(f"[ClickHouse] Ingesting signal {signal.id} for tenant {signal.tenant_id}")
        # In a real setup, we'd use the ClickHouse HTTP interface or a dedicated client
        # Example: requests.post(f"{self.url}/?query=INSERT INTO sentra.signals FORMAT JSONEachRow", json=flattened)

    def query(self, tenant_id: str, query: str) -> List[Dict[str, Any]]:
        print(f"[ClickHouse] Executing analytical query for {tenant_id}: {query}")
        return [{"metric": "count", "value": 120, "tenant_id": tenant_id}]

class ElasticStorage(BaseStorage):
    """Handles forensic queries (Keyword search / Full content)."""
    def __init__(self, host: str = "localhost", port: int = 9200):
        self.url = f"http://{host}:{port}"

    def ingest(self, signal: SecuritySignal):
        """Phase 2: Ingest full signal JSON into Elastic for forensic search."""
        index = f"signals-{signal.tenant_id}"
        doc = signal.model_dump()
        print(f"[Elastic] Ingesting full signal {signal.id} into index {index}")
        # Example: requests.post(f"{self.url}/{index}/_doc/{signal.id}", json=doc)

    def query(self, tenant_id: str, query: str) -> List[Dict[str, Any]]:
        print(f"[Elastic] Executing forensic query for {tenant_id}: {query}")
        return [{"timestamp": "2026-02-11T12:00:00", "message": "Failed login", "tenant_id": tenant_id}]

class VectorDBStorage(BaseStorage):
    """Handles similarity search (ChromaDB / VectorDB)."""
    def ingest(self, signal: SecuritySignal):
        print(f"[VectorDB] Embedding and indexing signal {signal.id}")

    def query(self, tenant_id: str, query: str) -> List[Dict[str, Any]]:
        print(f"[VectorDB] Executing similarity search for {tenant_id}: {query}")
        return [{"signal_id": "sig-789", "reason": "98% vector similarity to known brute force pattern"}]

class AIControlPlaneStorage(BaseStorage):
    """Handles judgment/decision queries via LLM."""
    def ingest(self, signal: SecuritySignal):
        pass # AI doesn't ingest directly in this abstraction

    def query(self, tenant_id: str, query: str) -> List[Dict[str, Any]]:
        print(f"[AI Control Plane] Consulting LLM for decision support: {query}")
        # In a real setup, we'd call AIEngine here
        return [{"decision": "CONSENSUS_BLOCK", "risk_reduction": 0.85, "explanation": "Pattern matches coordinated credential stuffing."}]

class StorageFactory:
    @staticmethod
    def get_storage(engine_type: str) -> BaseStorage:
        if engine_type == "ClickHouse":
            return ClickHouseStorage()
        elif engine_type == "Elastic":
            return ElasticStorage()
        elif engine_type == "VectorDB":
            return VectorDBStorage()
        elif engine_type == "AI Control Plane":
            return AIControlPlaneStorage()
        else:
            raise ValueError(f"Unknown storage engine: {engine_type}")
