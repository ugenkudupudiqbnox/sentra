# 🏗️ Kafka Playbook: PB-Scale Log Ingestion

This playbook outlines the deployment and tuning strategy for a production-grade Kafka cluster capable of handling **Petabyte-scale** ingestion for the Sentra AI Control Plane.

## 1. Physical Architecture (The "Iron" Layer)
For PB-scale, avoid generic instances. You need high-throughput I/O.

- **Storage**: NVMe SSDs are mandatory. Use **XFS** filesystem with `noatime`.
- **Network**: Minimum 25Gbps NICs. 100Gbps preferred for inter-broker replication.
- **CPU**: High core counts for `num.io.threads` and compression overhead.
- **RAM**: Large amount (64GB+) but limit JVM Heap to 32GB; leave the rest for **OS Page Cache**.

## 2. Operating System Tuning
Apply these settings to `/etc/sysctl.conf`:

```bash
# Network stack hardening for high-throughput
net.core.wmem_max = 16777216
net.core.rmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.ipv4.tcp_window_scaling = 1
vm.max_map_count = 262144
```

## 3. PB-Scale Broker Configuration (`server.properties`)
Standard configurations will fail under PB-scale pressure.

### High-Throughput I/O
```properties
num.network.threads=12      # Increase based on CPU cores
num.io.threads=24           # At least 2x the number of disks
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
```

### Strategic Retention & Log Management
```properties
log.segment.bytes=1073741824 # 1GB segments
log.retention.hours=168      # 7 days (Tune based on storage cost)
log.retention.check.interval.ms=300000
```

### Reliability vs Performance
```properties
num.partitions=64           # Minimum for high parallelism
default.replication.factor=3
min.insync.replicas=2
unclean.leader.election.enable=false
```

## 4. Tiered Storage (The PB-Scale Secret)
To handle Petabytes without exponentially growing your NVMe costs:
1. **Hot Tier**: Local NVMe SSDs (Retention: 24-48 hours).
2. **Cold Tier**: S3 / GCS / Azure Blob Storage (Retention: 30-365 days).
*Used via Kafka's Tiered Storage API or Confluent-style tiered storage.*

## 5. Producer Tuning (Log Collectors)
Sentra agents must use these settings:
- **Compression**: `lz4` (Highest speed) or `zstd` (Best ratio).
- **Batching**: `batch.size=131072` (128KB) and `linger.ms=50`.
- **Acks**: `acks=1` for performance, `acks=all` for audit-critical logs.

## 6. Monitoring & Health
Mandatory metrics to watch:
- **Under Replicated Partitions (URP)**: Must be 0.
- **Request Handler Idle Ratio**: Should stay > 0.3.
- **Network Processor Avg Idle Ratio**: Should stay > 0.3.
- **Disk I/O Wait**: Monitor for bottlenecked storage.

---
*Maintained by Sentra Security Engineering*
