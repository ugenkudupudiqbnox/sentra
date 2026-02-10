import zipfile
import os
import glob
from datetime import datetime

def create_audit_bundle():
    """
    Finalizes Phase 3 by aggregating all security decisions, narratives, 
    and raw signal evidence into a single auditor-ready zip archive.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    bundle_name = f"sentra_audit_evidence_{timestamp}.zip"
    
    # Core artifacts for SOC2/ISO audit
    files_to_include = [
        "FLEET_REPORT.md",     # Narrative & Timeline
        "overrides.json",      # Analyst Decisions (Human-in-the-loop)
        "PRD.md",              # Security Model & Scope
        "ARCHITECTURE.md",     # System Design
        "SECURITY_MODEL.md"    # Risk Classification Logic
    ]
    
    # Raw Signal Evidence (Proof of Monitoring)
    raw_reports = glob.glob("reports/*.json")
    files_to_include.extend(raw_reports)
    
    print(f"--- Generating Audit Evidence Bundle ({bundle_name}) ---")
    
    with zipfile.ZipFile(bundle_name, 'w') as zipf:
        for file_path in files_to_include:
            if os.path.exists(file_path):
                print(f"Adding: {file_path}")
                zipf.write(file_path)
            else:
                print(f"Note: {file_path} not found, skipping.")
                
    print(f"\nSUCCESS: Phase 3 Audit Bundle generated: {bundle_name}")

if __name__ == "__main__":
    create_audit_bundle()
