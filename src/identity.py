from typing import Dict, Optional

class IdentityService:
    """
    Simulates an organizational identity service (LDAP/AzureAD).
    In production, this would bridge to an external IDP.
    """
    
    # Mock database mapping local handles to corporate identities
    MOCK_IDP = {
        "stpi": {
            "email": "ugen@braoucloud.com",
            "role": "Cloud Architect",
            "department": "Security Architecture"
        },
        "root": {
            "email": "security-alert@braoucloud.com",
            "role": "System Administrator",
            "department": "Infrastructure Ops"
        },
        "admin": {
            "email": "admin@braoucloud.com",
            "role": "IT Support",
            "department": "Corporate IT"
        }
    }

    @staticmethod
    def resolve_user(username: str) -> Dict[str, Optional[str]]:
        """Resolves a local username to an organizational identity."""
        identity = IdentityService.MOCK_IDP.get(username, {})
        return {
            "org_identity": identity.get("email"),
            "job_role": identity.get("role")
        }
