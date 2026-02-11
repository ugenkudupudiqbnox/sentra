import json
import re
import datetime
from typing import Dict, Any, List, Optional, Tuple
from ai_engine import AIEngine

class HealthMonitor:
    """Monitors the availability and latency of downstream engines."""
    
    def __init__(self):
        self.registry = {
            "ClickHouse": {"status": "HEALTHY", "latency_ms": 10},
            "Elastic": {"status": "HEALTHY", "latency_ms": 45},
            "VectorDB": {"status": "HEALTHY", "latency_ms": 230},
            "Kafka/Flink": {"status": "HEALTHY", "latency_ms": 5},
            "AI Control Plane": {"status": "HEALTHY", "latency_ms": 1200}
        }

    def get_optimal_engine(self, primary_engine: str) -> str:
        """Returns the primary engine if healthy, else finds a fallback."""
        if self.registry.get(primary_engine, {}).get("status") == "HEALTHY":
            return primary_engine
        
        # Simple fallback logic: if primary is down, use Elastic as catch-all
        print(f"[QRE] Warning: Primary engine {primary_engine} is UNHEALTHY. Falling back to Elastic.")
        return "Elastic"

    def update_status(self, engine: str, status: str, latency: int):
        if engine in self.registry:
            self.registry[engine]["status"] = status
            self.registry[engine]["latency_ms"] = latency

class IntentClassifier:
    """Classifies query intent into one of the canonical QRE categories."""
    
    INTENTS = {
        "EXACT": "Forensic / Precise matching",
        "ANALYTICAL": "Aggregation / Trends",
        "SIMILARITY": "Similarity / Pattern matching",
        "STREAMING": "Reactive / Continuous",
        "DECISION": "Judgment / Synthesis"
    }

    def __init__(self):
        self.ai = AIEngine()

    def classify(self, tenant_id: str, query: str) -> Tuple[str, float]:
        """
        Uses LLM to classify intent, with a rule-based fallback.
        """
        # Rule-based fallback for common keywords
        query_lower = query.lower()
        if any(w in query_lower for w in ["how many", "top", "average", "count", "trend"]):
            return "ANALYTICAL", 0.95
        if any(w in query_lower for w in ["similar", "like this", "matches pattern"]):
            return "SIMILARITY", 0.95
        if any(w in query_lower for w in ["is this", "should I", "risk of"]):
            return "DECISION", 0.85
        
        # LLM classification via AI Engine
        intent, confidence = self.ai.classify_intent(tenant_id, query)
        if confidence > 0.0:
            return intent, confidence
        
        return "EXACT", 0.70  # Default fallback

class QueryDecomposer:
    """Decomposes compound queries into individual engine sub-queries."""
    
    def decompose(self, query: str) -> List[Dict[str, str]]:
        """
        Simple keyword-based decomposition for Phase 1/2.
        Example: "Is this similar to X and how often did Y happen?"
        """
        sub_queries = []
        
        # Split by common conjunctions
        parts = re.split(r' and | plus | as well as ', query, flags=re.IGNORECASE)
        
        classifier = IntentClassifier()
        for part in parts:
            intent, confidence = classifier.classify("system", part.strip())
            sub_queries.append({
                "sub_query": part.strip(),
                "intent": intent,
                "confidence": confidence
            })
            
        return sub_queries

class CostEstimator:
    """
    Estimates the relative cost of executing a query on a specific engine.
    Used for cost-aware routing decisions.
    """
    ENGINE_BASE_COSTS = {
        "Elastic": 5.0,        # High cost for forensic indexing and keyword search
        "ClickHouse": 1.0,     # Low cost for analytical aggregates
        "VectorDB": 3.0,       # Moderate cost for embedding search
        "Kafka/Flink": 2.0,    # Real-time processing overhead
        "AI Control Plane": 10.0 # High cost per LLM token consultation
    }

    @staticmethod
    def estimate(engine: str, query: str) -> float:
        """
        Predicts cost based on engine type and query complexity.
        In a real system, this would inspect data volume or expected shard hits.
        """
        base_cost = CostEstimator.ENGINE_BASE_COSTS.get(engine, 1.0)
        
        # Complexity penalty
        complexity = len(query.split()) * 0.1
        total_estimate = round(base_cost + complexity, 2)
        
        return total_estimate

class QueryRouter:
    """Routes queries to the optimal engine based on intent."""

    ENGINE_MAPPING = {
        "EXACT": "Elastic",
        "ANALYTICAL": "ClickHouse",
        "SIMILARITY": "VectorDB",
        "STREAMING": "Kafka/Flink",
        "DECISION": "AI Control Plane"
    }

    def __init__(self):
        self.classifier = IntentClassifier()
        self.decomposer = QueryDecomposer()
        self.health = HealthMonitor()
        self.audit_log = "qre_audit.json"

    def _log_decision(self, decision: Dict[str, Any]):
        """Persist routing decision for auditability (FR-4)."""
        try:
            with open(self.audit_log, "a") as f:
                f.write(json.dumps(decision) + "\n")
        except Exception as e:
            print(f"[QRE] Error writing audit log: {e}")

    def route(self, tenant_id: str, query: str) -> List[Dict[str, Any]]:
        # Check if compound
        sub_queries = self.decomposer.decompose(query)
        decisions = []
        
        for sq in sub_queries:
            primary_engine = self.ENGINE_MAPPING.get(sq["intent"], "Elastic")
            
            # Health-aware routing
            engine = self.health.get_optimal_engine(primary_engine)
            
            cost_estimate = CostEstimator.estimate(engine, sq["sub_query"])
            
            decision = {
                "original_query": query,
                "sub_query": sq["sub_query"],
                "tenant_id": tenant_id,
                "intent": sq["intent"],
                "confidence": sq["confidence"],
                "engine": engine,
                "cost_estimate": cost_estimate,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            decisions.append(decision)
            self._log_decision(decision)
            print(f"[QRE] Route: '{sq['sub_query']}' -> {engine} ({sq['intent']}, Cost: {cost_estimate})")
            
        return decisions

if __name__ == "__main__":
    # Quick test
    router = QueryRouter()
    test_queries = [
        "top 5 failed logins by IP and show logs for IP 192.168.1.1",
        "is this login similar to the brute force attack yesterday and should I block this user?"
    ]
    for q in test_queries:
        print(f"\nDecomposing: {q}")
        router.route("test-tenant", q)
