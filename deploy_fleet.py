import json
import subprocess
import sys
import os

# Fleet Configuration
SERVERS = [
    {"host": "115.124.120.142", "port": "5522", "user": "stpi", "name": "braoucloud1"},
    {"host": "115.124.120.143", "port": "5522", "user": "stpi", "name": "braoucloud2"}
]

REMOTE_PATH = "/tmp/parse_auth_log.py"
OUTPUT_DIR = "reports"

def run_command(cmd):
    """Executes a shell command and returns output."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}", file=sys.stderr)
        return None

def deploy_and_run():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for server in SERVERS:
        print(f"--- Processing {server['name']} ({server['host']}) ---")
        
        # 1. SCP the script to the remote server
        print(f"Deploying script to {server['name']}...")
        scp_cmd = f"scp -P {server['port']} parse_auth_log.py {server['user']}@{server['host']}:{REMOTE_PATH}"
        run_command(scp_cmd)

        # 2. Run the script via SSH with sudo
        print(f"Analyzing logs on {server['name']}...")
        remote_out = f"/tmp/{server['name']}.json"
        ssh_cmd = (
            f"ssh -p {server['port']} {server['user']}@{server['host']} "
            f"\"sudo python3 {REMOTE_PATH} --output {remote_out} > /dev/null\""
        )
        run_command(ssh_cmd)

        # 3. Retrieve the resulting JSON
        print(f"Retrieving signals from {server['name']}...")
        local_target = os.path.join(OUTPUT_DIR, f"{server['name']}.json")
        fetch_cmd = f"scp -P {server['port']} {server['user']}@{server['host']}:{remote_out} {local_target}"
        run_command(fetch_cmd)
        
        print(f"Done. Report saved to {local_target}\n")

    # 4. Run Aggregation
    print("--- Generating Fleet Summary ---")
    json_files = [os.path.join(OUTPUT_DIR, f"{s['name']}.json") for s in SERVERS]
    agg_cmd = f"python3 aggregate_weekly.py {' '.join(json_files)}"
    subprocess.run(agg_cmd, shell=True)

if __name__ == "__main__":
    deploy_and_run()
