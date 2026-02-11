from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, IPvAnyAddress
from datetime import datetime
import uuid

SCHEMA_VERSION = "1.0.0"

class UserEntity(BaseModel):
    username: str
    uid: Optional[int] = None
    group: Optional[str] = None
    domain: Optional[str] = None

class HostEntity(BaseModel):
    hostname: str
    ip: Optional[IPvAnyAddress] = None
    os: Optional[str] = "Linux"
    role: Optional[str] = None  # e.g., "Production DB", "Edge Proxy"

class ProcessEntity(BaseModel):
    pid: Optional[int] = None
    ppid: Optional[int] = None
    name: str
    path: Optional[str] = None
    args: Optional[List[str]] = None

class NetworkEntity(BaseModel):
    source_ip: Optional[IPvAnyAddress] = None
    dest_ip: Optional[IPvAnyAddress] = None
    source_port: Optional[int] = None
    dest_port: Optional[int] = None
    protocol: Optional[str] = None

class ComplianceTag(BaseModel):
    framework: str  # e.g., "SOC2", "MITRE", "ISO27001"
    control_id: str
    description: Optional[str] = None

class SecuritySignal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    tenant_id: str
    schema_version: str = SCHEMA_VERSION
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    signal_type: str
    severity: str  # Low, Medium, High, Critical
    risk_score: float = 0.0
    
    # Entities
    user: Optional[UserEntity] = None
    host: Optional[HostEntity] = None
    process: Optional[ProcessEntity] = None
    network: Optional[NetworkEntity] = None
    
    # Context & Narrative
    narrative: Optional[str] = None
    recommendation: Optional[str] = None
    ai_confidence: float = 0.0  # AI's self-reported confidence in the narrative
    
    # Metadata & Tags
    compliance_tags: List[ComplianceTag] = []
    mitre_ttps: List[str] = []
    model_info: Dict[str, str] = {} # e.g., {"model": "gpt-4o", "provider": "openai"}
    extra_data: Dict[str, Any] = {}

    def to_json(self):
        return self.model_dump_json()
