-- ClickHouse Schema for Sentra Security Signals v1
-- Optimized for analytical queries and multi-tenant isolation

CREATE DATABASE IF NOT EXISTS sentra;

-- Main Signals Table
CREATE TABLE IF NOT EXISTS sentra.signals (
    id String,
    tenant_id LowCardinality(String),
    schema_version String,
    timestamp DateTime64(3),
    
    signal_type LowCardinality(String),
    severity Enum8('Low' = 1, 'Medium' = 2, 'High' = 3, 'Critical' = 4),
    risk_score Float32,
    
    -- Entity Summaries (Flat for performance)
    user_username String,
    host_hostname String,
    host_ip IPv4,
    process_name String,
    network_source_ip IPv4,
    
    -- Context
    ai_confidence Float32,
    model_name LowCardinality(String),
    
    -- Metadata (JSON)
    mitre_ttps Array(String),
    compliance_controls Array(String)
) 
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (tenant_id, timestamp, signal_type)
TTL timestamp + INTERVAL 90 DAY;

-- Aggregated View for Dashboards (Top failed logins)
CREATE MATERIALIZED VIEW IF NOT EXISTS sentra.daily_risk_metrics
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(day)
ORDER BY (tenant_id, day, signal_type)
AS SELECT
    tenant_id,
    toStartOfDay(timestamp) AS day,
    signal_type,
    count() AS total_count,
    avg(risk_score) AS avg_risk
FROM sentra.signals
GROUP BY tenant_id, day, signal_type;
