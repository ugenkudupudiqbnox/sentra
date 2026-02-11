import streamlit as st
import pandas as pd
import json
from datetime import datetime
import sys
import os

# Ensure src is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qre import QueryRouter
from ai_engine import AIEngine
from storage import ClickHouseStorage, ElasticStorage
from schema import SecuritySignal, UserEntity, HostEntity

# Page Config
st.set_page_config(
    page_title="Sentra Control Plane",
    page_icon="🛡️",
    layout="wide",
)

# Initialize AI Engine and QRE
@st.cache_resource
def get_engines():
    return AIEngine(), QueryRouter()

ai_engine, qre_router = get_engines()

# Header
st.title("🛡️ Sentra: AI-Native Security Control Plane")
st.markdown("---")

# Sidebar - Infrastructure Health
st.sidebar.header("📡 Infrastructure Health")
health_data = qre_router.health.registry
for engine, status in health_data.items():
    color = "green" if status["status"] == "HEALTHY" else "red"
    st.sidebar.markdown(f"**{engine}**: :{color}[{status['status']}] ({status['latency_ms']}ms)")

st.sidebar.markdown("---")
st.sidebar.header("📊 AI Usage Metrics")
tracker = ai_engine.get_usage_tracker()
st.sidebar.metric("Tokens Consumed", f"{tracker.total_tokens:,}")
st.sidebar.metric("Estimated Cost", f"${tracker.total_cost_usd:.4f}")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["🌩️ Signal Stream", "🔍 QRE Lab", "🧠 Model Drift"])

with tab1:
    st.header("Real-time Security Signals")
    
    # Mock some data for demonstration if storage is empty
    mock_signals = [
        {
            "id": "sig-101",
            "timestamp": "2026-02-11 14:00:21",
            "signal_type": "brute_force",
            "severity": "CRITICAL",
            "user": "jdoe",
            "ai_narrative": "Detected sequential failed logins from unknown IP targeting admin portal.",
            "status": "investigating"
        },
        {
            "id": "sig-102",
            "timestamp": "2026-02-11 14:05:01",
            "signal_type": "lateral_movement",
            "severity": "HIGH",
            "user": "system_svc",
            "ai_narrative": "Abnormal cross-segment RPC call detected from web-tier to DB-internal.",
            "status": "triaged"
        }
    ]
    
    df_signals = pd.DataFrame(mock_signals)
    
    # Create a custom table with a "View" button for each row
    cols = st.columns([1, 2, 2, 1, 1, 1])
    cols[0].write("**ID**")
    cols[1].write("**Timestamp**")
    cols[2].write("**Type**")
    cols[3].write("**Severity**")
    cols[4].write("**User**")
    cols[5].write("**Action**")

    for signal in mock_signals:
        row = st.columns([1, 2, 2, 1, 1, 1])
        row[0].write(signal["id"])
        row[1].write(signal["timestamp"])
        row[2].write(signal["signal_type"])
        
        # Color code severity
        sev_color = "🔴" if signal["severity"] == "CRITICAL" else "🟠"
        row[3].write(f"{sev_color} {signal['severity']}")
        
        row[4].write(signal["user"])
        if row[5].button("Details", key=f"btn_{signal['id']}"):
            st.session_state.selected_signal = signal

    # Detail View Overlay
    if "selected_signal" in st.session_state:
        sig = st.session_state.selected_signal
        st.markdown("---")
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            c1.subheader(f"🔍 Signal Investigation: {sig['id']}")
            if c2.button("Close X", key="close_details"):
                del st.session_state.selected_signal
                st.rerun()
            
            detail_col1, detail_col2 = st.columns(2)
            with detail_col1:
                st.markdown(f"**Signal Type**: `{sig['signal_type']}`")
                st.markdown(f"**Severity**: {sig['severity']}")
                st.markdown(f"**Timestamp**: {sig['timestamp']}")
                st.markdown(f"**Affected User**: {sig['user']}")
            
            with detail_col2:
                st.markdown("**Status**: `investigating`")
                st.markdown("**Compliance Scope**: SOC2, HIPAA")
                st.markdown("**MITRE ATT&CK**: T1110 (Brute Force)")

            st.info(f"**AI Narrative Analysis**\n\n{sig['ai_narrative']}")
            st.warning("**Recommended Playbook**: Isolated infected host and reset user credentials.")

with tab2:
    st.header("Query Routing Engine (QRE) Explorer")
    st.markdown("Ask natural language questions to investigate the data.")
    
    query_input = st.text_input("Security Query", placeholder="e.g., 'How many failed logins? and is this user risky?'")
    
    if query_input:
        with st.spinner("Routing & Executing..."):
            decisions = qre_router.route("acme-corp", query_input)
            
            for i, dec in enumerate(decisions):
                with st.expander(f"Decision {i+1}: {dec['sub_query']}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Intent", dec['intent'])
                    col2.metric("Target Engine", dec['engine'])
                    col3.metric("Cost Estimate", f"{dec['cost_estimate']} units")
                    
                    st.info(f"**AI Reasoning**: {qre_router.classifier.INTENTS.get(dec['intent'], 'Standard lookup')}")
                    
                    # Simulated results display
                    st.markdown("#### Execution Results")
                    if dec['engine'] == "ClickHouse":
                        with st.container(border=True):
                            res_c1, res_c2 = st.columns(2)
                            res_c1.metric("Analytical Match Count", "142", delta="12%", delta_color="inverse")
                            res_c2.markdown("**Trend**: Login failures are trending up in the last 24h.")
                            st.caption("Data source: ClickHouse Aggregate Tables")
                            
                    elif dec['engine'] == "Elastic":
                        with st.container(border=True):
                            st.markdown("📝 **Forensic Log Summary**")
                            st.write("Retrieved 12 raw events matching the specific forensic pattern.")
                            sample_logs = pd.DataFrame([
                                {"timestamp": "14:00:01", "event": "Failed Login", "source": "1.1.1.1"},
                                {"timestamp": "14:00:05", "event": "Failed Login", "source": "1.1.1.1"},
                                {"timestamp": "14:00:10", "event": "Failed Login", "source": "1.1.1.1"},
                            ])
                            st.dataframe(sample_logs, use_container_width=True)
                            
                    elif dec['engine'] == "VectorDB":
                        with st.container(border=True):
                            st.markdown("🎯 **Pattern Match (Similarity)**")
                            similarity_c1, similarity_c2 = st.columns([1, 2])
                            similarity_c1.metric("Similarity Score", "92%")
                            similarity_c2.info("This behavior highly correlates with a 'Credential Stuffing' attack pattern seen across 3 other tenants.")
                            
                    else:
                        st.success(f"🤖 **AI Decision Support**\n\n**Recommendation**: Immediately block IP 1.1.1.1 and trigger Multi-Factor Authentication (MFA) reset for affected users.\n\n**Confidence**: 95%")

with tab3:
    st.header("AI Governance & Drift")
    st.markdown("Tracking model responses against baseline expectations.")
    
    # Sample drift log visualization
    drift_logs = [
        {"timestamp": "2026-02-01", "drift_score": 0.02, "model": "gpt-4o"},
        {"timestamp": "2026-02-05", "drift_score": 0.05, "model": "gpt-4o"},
        {"timestamp": "2026-02-10", "drift_score": 0.04, "model": "gpt-4o"},
    ]
    st.line_chart(pd.DataFrame(drift_logs).set_index("timestamp"))
    st.caption("Lower drift score indicates consistent reasoning patterns.")

st.markdown("---")
st.caption("Sentra Q2 Analytics Plane • Powered by AI-Native Security Operations")
