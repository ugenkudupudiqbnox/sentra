# 🌊 Flink Playbook: Real-Time Signal Processing at Scale

This playbook outlines the deployment and stream-processing strategy for Apache Flink to power the Sentra AI Control Plane's real-time enrichment and correlation layer.

## 1. Cluster Architecture
For PB-scale log processing, use **Flink on Kubernetes (Native)** or **Flink on YARN** to handle dynamic scaling.

- **JobManager**: 2 nodes (High Availability via ZooKeeper/Kubernetes).
- **TaskManager**: Multiple nodes, scaled based on **Parallelism** requirements ($Partitions \times Parallelism$).
- **State Backend**: **RocksDB** is mandatory for large-scale stateful operations (like 1-hour correlation windows).

## 2. Stream Processing Strategy
Sentra's Flink jobs are divided into three performance-optimized stages:

### Stage A: Normalization (Stateless)
- **Goal**: Convert raw strings into Sentra JSON signals.
- **Tuning**: High parallelism, low memory per TaskManager.
- **Logic**: RFC5424 parsing and Regex Extraction.

### Stage B: Enrichment (I/O Bound)
- **Goal**: Add Geo-IP, Threat Intel, and Identity data.
- **Tuning**: Use `AsyncFunction` for external API calls (AbuseIPDB, etc.) to prevent pipeline backpressure.
- **Checkpointing**: Enable every 1-5 minutes to ensure "exactly-once" delivery.

### Stage C: Windowed Correlation (Stateful)
- **Goal**: Group signals by `hostname` or `user` over 10m/1h windows.
- **Logic**: Use `TumblingEventTimeWindows` or `SlidingEventTimeWindows`.
- **State Cleanup**: Set `StateTtlConfig` to prevent RocksDB from growing indefinitely.

## 3. Performance Tuning (`flink-conf.yaml`)

### Memory Management
```yaml
taskmanager.memory.process.size: 16g
taskmanager.memory.managed.fraction: 0.4  # RocksDB memory
taskmanager.numberOfTaskSlots: 4          # Map to CPU cores
```

### RocksDB State Backend
```yaml
state.backend: rocksdb
state.backend.incremental: true           # Mandatory for large state
state.checkpoints.dir: s3://sentra-flink/checkpoints/
```

### Network Stack
```yaml
taskmanager.network.memory.max: 2g        # Buffer capacity for high-throughput
taskmanager.network.netty.numThreads: 8
```

## 4. Operational Best Practices
- **Backpressure Monitoring**: Watch Flink's "Backpressure" tab. If high, increase parallelism or optimize the `AsyncFunction`.
- **Watermarks**: Use `BoundedOutOfOrdernessTimestampExtractor` to handle delayed logs from remote servers.
- **Side Outputs**: Route "malformed logs" or "failed enrichments" to a side output for separate auditing without crashing the main pipeline.

## 5. Deployment Workflow
1. **Containerize**: Package Flink job as a fat JAR.
2. **Submit**: `flink run -m cluster-address:8081 -p 64 -c com.sentra.SignalEngine sentra-engine.jar`
3. **Savepoints**: Always trigger a `savepoint` before updating any processing logic to avoid data loss.

---
*Maintained by Sentra Security Engineering*
