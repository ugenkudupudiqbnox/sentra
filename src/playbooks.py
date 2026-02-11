from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class PlaybookAction(BaseModel):
    name: str
    target: str           # e.g., "host", "user", "ip"
    action: str           # e.g., "block", "notify", "reset_password"
    parameters: Dict[str, Any] = {}
    require_approval: bool = True

class SecurityPlaybook(BaseModel):
    id: str
    name: str
    trigger_signal: str   # e.g., "ssh_brute_force"
    min_risk_score: float = 0.5
    actions: List[PlaybookAction]

class PlaybookEngine:
    """
    Manages and triggers security playbooks based on incoming signals.
    Phase 3: Automated and Gated Responses.
    """
    
    def __init__(self):
        self.playbooks = [
            SecurityPlaybook(
                id="PB-001",
                name="Contain Brute Force",
                trigger_signal="ssh_brute_force",
                min_risk_score=0.7,
                actions=[
                    PlaybookAction(name="Network Block", target="ip", action="block", parameters={"duration": "1h"}),
                    PlaybookAction(name="Slack Alert", target="user", action="notify", require_approval=False)
                ]
            ),
            SecurityPlaybook(
                id="PB-002",
                name="Sensitive IAM Audit",
                trigger_signal="privilege_escalation",
                min_risk_score=0.4,
                actions=[
                    PlaybookAction(name="Log Review", target="host", action="audit", require_approval=True)
                ]
            )
        ]

    def get_recommendations(self, signal_type: str, risk_score: float) -> List[SecurityPlaybook]:
        """Finds applicable playbooks for a given signal."""
        return [pb for pb in self.playbooks if pb.trigger_signal == signal_type and risk_score >= pb.min_risk_score]
