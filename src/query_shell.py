import argparse
from qre import QueryRouter
from storage import StorageFactory

def main():
    parser = argparse.ArgumentParser(description="Sentra Query Shell (QRE Beta)")
    parser.add_argument("--tenant-id", default="braoucloud-prod", help="Tenant context")
    args = parser.parse_args()

    router = QueryRouter()
    print("Sentra AI-Native Query Shell")
    print("Type your security question (or 'exit' to quit)")
    print("-" * 30)

    while True:
        try:
            query = input(f"[{args.tenant_id}] > ")
            if query.lower() in ['exit', 'quit']:
                break
            
            if not query.strip():
                continue

            # 1. Route the query using QRE
            decisions = router.route(args.tenant_id, query)
            
            for decision in decisions:
                engine_name = decision['engine']
                intent = decision['intent']
                conf = decision['confidence']
                
                print(f"\n[QRE Decision]")
                print(f"  Target Engine: {engine_name}")
                print(f"  Detected Intent: {intent} (Confidence: {conf:.2f})")
                print(f"  Reasoning: Guided by security taxonomy v1")
                
                # 2. Execute via Storage Layer
                storage = StorageFactory.get_storage(engine_name)
                results = storage.query(args.tenant_id, decision['sub_query'])
                
                print(f"[Results from {engine_name}]")
                for r in results:
                    print(f"  - {r}")
            print("-" * 30)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
