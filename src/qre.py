import json
import re
from typing import Dict, Any, List, Optional, Tuple
from ai_engine import AIEngine

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
        self.engine = AIEngine()

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
        
        # LLM classification
        prompt = f"""
        Classify the intent of the following security query into one of these categories:
        - EXACT: Precise matching, forensic logs, specific IP/User/Time.
        - ANALYTICAL: Aggregations, trends, top N, statistics.
        - SIMILARITY: Finding related events, pattern matching, "like this".
        - STREAMING: Alerts, real-time monitoring.
        - DECISION: Risk assessment, judgment calls, recommendations.

        Query: "{query}"

        Response Format (JSON):
        {{
            "intent": "...",
            "confidence": 0.0
        }}
        """

        # We reuse the consult_ai infrastructure but for routing
        # In a real implementation, we might have a specific route_ai method
        # For now, let's mock the LLM classification or use a dedicated method if we added it
        # Since consult_ai is tuned for narratives, let's assume rule-based + future LLM
        
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

    def route(self, tenant_id: str, query: str) -> List[Dict[str, Any]]:
        # Check if compound
        sub_queries = self.decomposer.decompose(query)
        decisions = []
        
        for sq in sub_queries:
            engine = self.ENGINE_MAPPING.get(sq["intent"], "Elastic")
            decision = {
                "original_query": query,
                "sub_query": sq["sub_query"],
                "tenant_id": tenant_id,
                "intent": sq["intent"],
                "confidence": sq["confidence"],
                "engine": engine,
                "timestamp": AIEngine().get_usage_tracker().logs[-1]["timestamp"] if AIEngine().get_usage_tracker().logs else "now"
            }
            decisions.append(decision)
            print(f"[QRE] Route: '{sq['sub_query']}' -> {engine} ({sq['intent']})")
            
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
