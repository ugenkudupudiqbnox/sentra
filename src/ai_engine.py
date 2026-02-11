import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load local environment variables if present
load_dotenv()

# Optional dependencies for Phase 2 AI
try:
    import chromadb
    from chromadb.utils import embedding_functions
    from openai import OpenAI
    HAS_AI_DEPS = True
except ImportError:
    HAS_AI_DEPS = False

# Initialize clients
CHROMA_PATH = "sentra_vector_db"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

collection = None
client = None

if HAS_AI_DEPS:
    try:
        # ChromaDB Setup
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        embedding_func = embedding_functions.DefaultEmbeddingFunction()
        collection = chroma_client.get_or_create_collection(
            name="security_signals",
            embedding_function=embedding_func
        )
        # OpenAI Client
        client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    except Exception as e:
        print(f"Warning: Failed to initialize AI deps: {e}")
        HAS_AI_DEPS = False

class AIEngine:
    @staticmethod
    def index_signal(signal_data):
        """
        Stores and indexes a security signal in ChromaDB for correlation.
        """
        if not HAS_AI_DEPS or not collection:
            return

        signal_id = signal_data.get("id")
        content = f"Signal: {signal_data.get('signal')} | Host: {signal_data.get('hostname')} | User: {signal_data.get('user')} | Narrative: {signal_data.get('narrative')}"
        
        try:
            collection.add(
                ids=[signal_id],
                documents=[content],
                metadatas=[{
                    "signal_type": signal_data.get("signal"),
                    "hostname": signal_data.get("hostname"),
                    "user": signal_data.get("user"),
                    "risk_score": signal_data.get("risk_score", 0.0),
                    "timestamp": signal_data.get("timestamp")
                }]
            )
        except Exception as e:
            print(f"Indexing failed: {e}")

    @staticmethod
    def consult_ai(signal_type, context):
        """
        Phase 2: Use LLM for intelligent narrative and recommendations.
        """
        if not HAS_AI_DEPS or not client:
            return None, None

        prompt = f"""
        You are a security analyst for Sentra, an AI-native security control plane.
        Analyze the following security event and provide:
        1. A calm, non-alarmist narrative for a non-technical customer.
        2. A specific, actionable recommendation for a technical team.

        Context:
        Type: {signal_type}
        Data: {json.dumps(context)}

        Response Format (JSON):
        {{
            "narrative": "...",
            "recommendation": "..."
        }}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are a helpful security analyst."},
                          {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("narrative"), result.get("recommendation")
        except Exception as e:
            # Silently fail for remote execution
            return None, None

    @staticmethod
    def get_related_signals(signal_id, n_results=5):
        """
        Phase 2: Use Vector DB to find correlated signals across the fleet.
        """
        if not HAS_AI_DEPS or not collection:
            return []
        try:
            results = collection.query(
                query_texts=[collection.get(ids=[signal_id])['documents'][0]],
                n_results=n_results
            )
            return results
        except:
            return []
