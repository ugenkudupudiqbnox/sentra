import argparse
import sys
import os

# Fix path to allow running from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qre import QueryRouter
from storage import StorageFactory

def main():
    parser = argparse.ArgumentParser(description="Sentra Query Shell (QRE Beta)")
    parser.add_argument("--tenant-id", default="braoucloud-prod", help="Tenant context")
    args = parser.parse_args()

    router = QueryRouter()
    print("\n" + "="*50)
    print("      SENTRA AI-NATIVE QUERY SHELL (Q2)")
    print("="*50)
    print("Type your security question (or 'exit' to quit)")
    print("Example: 'How many failed logins? and is this IP 1.1.1.1 risky?'")
    print("-" * 50)

    while True:
        try:
            query = input(f"[{args.tenant_id}] > ")
            if query.lower() in ['exit', 'quit']:
                break
            
            if not query.strip():
                continue

            # 1. Route the query using QRE (Decomposition + Health + Cost aware)
            decisions = router.route(args.tenant_id, query)
            
            for decision in decisions:
                engine_name = decision['engine']
                intent = decision['intent']
                conf = decision['confidence']
                cost = decision.get('cost_estimate', 0.0)
                sub_q = decision.get('sub_query', query)
                
                print(f"\n[QRE Decision] ----------------------------------")
                print(f"  Sub-Query:   \"{sub_q}\"")
                print(f"  Intent:      {intent} (Confidence: {conf:.2f})")
                print(f"  Engine:      {engine_name}")
                print(f"  Route Cost:  {cost} units")
                
                # 2. Execute via Storage Layer
                try:
                    storage = StorageFactory.get_storage(engine_name)
                    results = storage.query(args.tenant_id, sub_q)
                    
                    print(f"\n  [Results from {engine_name}]")
                    if isinstance(results, list):
                        for r in results:
                            print(f"    - {r}")
                    else:
                        print(f"    - {results}")
                except ValueError as ve:
                    print(f"  [Error] Routing failed: {ve}")
                except Exception as e:
                    print(f"  [Error] Execution failed: {e}")
            
            print("-" * 50)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    main()
