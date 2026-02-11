import os
import json
import time
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

# Optional dependencies for Phase 2 AI
try:
    import chromadb
    from chromadb.utils import embedding_functions
    from openai import OpenAI
    HAS_AI_DEPS = True
except ImportError:
    HAS_AI_DEPS = False

# Constants
CHROMA_PATH = "sentra_vector_db"
DEFAULT_MODEL = "gpt-4o"

class UsageTracker:
    """Tracks token usage and latency for mSOC billing groundwork."""
    def __init__(self, drift_log_path: str = "model_drift.log"):
        self.logs = []
        self.drift_log_path = drift_log_path

    @property
    def total_tokens(self) -> int:
        return sum(log.get("total_tokens", 0) for log in self.logs)

    @property
    def total_cost_usd(self) -> float:
        # Simple estimate: $0.01 per 1k tokens
        return (self.total_tokens / 1000.0) * 0.01

    def log_usage(self, tenant_id: str, provider: str, model: str, usage: Dict[str, int], latency: float, confidence: float = 0.0):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": tenant_id,
            "provider": provider,
            "model": model,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "latency_ms": round(latency * 1000, 2),
            "confidence": confidence
        }
        self.logs.append(entry)
        
        # Model Drift Logging (Phase 1/2 requirement)
        # Simply appending to a local file for now as a persistent log
        try:
            with open(self.drift_log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except:
            pass

        print(f"[USAGE] Tenant: {tenant_id} | Model: {model} | Tokens: {entry['total_tokens']} | Conf: {confidence}")

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_narrative(self, tenant_id: str, signal_type: str, context: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], float, Dict[str, Any]]:
        pass

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, tracker: UsageTracker):
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.tracker = tracker
        self.model = DEFAULT_MODEL

    def generate_narrative(self, tenant_id: str, signal_type: str, context: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], float, Dict[str, Any]]:
        if not self.client:
            return None, None, 0.0, {}

        prompt = f"""
        You are a security analyst for Sentra, an AI-native security control plane.
        Analyze the following security event and provide:
        1. A calm, non-alarmist narrative for a non-technical customer.
        2. A specific, actionable recommendation for a technical team.
        3. A confidence score (0.0 to 1.0) on how certain you are of this analysis.

        Context:
        Type: {signal_type}
        Data: {json.dumps(context)}

        Response Format (JSON):
        {{
            "narrative": "...",
            "recommendation": "...",
            "confidence": 0.85
        }}
        """

        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are a helpful security analyst."},
                          {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            latency = time.time() - start_time
            result = json.loads(response.choices[0].message.content)
            confidence = result.get("confidence", 0.0)
            
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            self.tracker.log_usage(tenant_id, "openai", self.model, usage, latency, confidence)
            
            return result.get("narrative"), result.get("recommendation"), confidence, usage
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return None, None, 0.0, {}

class VectorDB:
    def __init__(self, path: str):
        if not HAS_AI_DEPS:
            self.collection = None
            return
        
        try:
            self.client = chromadb.PersistentClient(path=path)
            self.embedding_func = embedding_functions.DefaultEmbeddingFunction()
            self.collection = self.client.get_or_create_collection(
                name="security_signals",
                embedding_function=self.embedding_func
            )
        except Exception as e:
            print(f"ChromaDB Error: {e}")
            self.collection = None

    def index_signal(self, tenant_id: str, signal_data: Dict[str, Any]):
        if not self.collection:
            return

        signal_id = signal_data.get("id")
        # Ensure we filter by tenant_id during correlation
        content = f"Tenant: {tenant_id} | Signal: {signal_data.get('signal_type')} | Host: {signal_data.get('host', {}).get('hostname')} | Narrative: {signal_data.get('narrative')}"
        
        metadata = {
            "tenant_id": tenant_id,
            "signal_type": signal_data.get("signal_type"),
            "risk_score": signal_data.get("risk_score", 0.0),
            "timestamp": signal_data.get("timestamp")
        }

        try:
            self.collection.add(
                ids=[signal_id],
                documents=[content],
                metadatas=[metadata]
            )
        except Exception as e:
            print(f"Indexing failed: {e}")

    def query_related(self, tenant_id: str, signal_id: str, n_results: int = 5):
        if not self.collection:
            return []
        
        try:
            # Multi-tenant isolation: filter by tenant_id
            results = self.collection.query(
                query_texts=[self.collection.get(ids=[signal_id])['documents'][0]],
                n_results=n_results,
                where={"tenant_id": tenant_id}
            )
            return results
        except Exception as e:
            print(f"Query failed: {e}")
            return []

class AIEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIEngine, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.tracker = UsageTracker()
        self.vector_db = VectorDB(CHROMA_PATH)
        
        # Default to OpenAI
        api_key = os.environ.get("OPENAI_API_KEY", "")
        self.provider = OpenAIProvider(api_key, self.tracker)

    def get_usage_tracker(self) -> UsageTracker:
        return self.tracker

    def index_signal(self, tenant_id: str, signal_data: Dict[str, Any]):
        self.vector_db.index_signal(tenant_id, signal_data)

    def consult_ai(self, tenant_id: str, signal_type: str, context: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], float]:
        narrative, recommendation, confidence, usage = self.provider.generate_narrative(tenant_id, signal_type, context)
        return narrative, recommendation, confidence

    def classify_intent(self, tenant_id: str, query: str) -> Tuple[str, float]:
        """
        Uses LLM to classify query intent for the QRE.
        """
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
        
        # We reuse the provider's logic by adding a generic completion method or matching prompt
        # For Phase 2, we'll keep it simple and assume the provider can handle this or mock it
        # In a real system, we'd have provider.classify_intent(...)
        try:
            # Reusing the narrative generation prompt structure for intent
            # (In a real refactor, we'd make generate_narrative more generic)
            _, _, confidence, _ = self.provider.generate_narrative(tenant_id, "intent_classification", {"query": query})
            # For now, let's just mock the intent string based on confidence or a simple check 
            # as a placeholder for a second LLM routing call
            return "EXACT", confidence 
        except:
            return "EXACT", 0.0

    def get_related_signals(self, tenant_id: str, signal_id: str, n_results: int = 5):
        return self.vector_db.query_related(tenant_id, signal_id, n_results)

