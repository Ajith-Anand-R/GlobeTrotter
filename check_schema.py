import requests

def check_schema():
    resp = requests.get("http://127.0.0.1:8000/openapi.json")
    if resp.status_code == 200:
        schema = resp.json()
        paths = schema.get("paths", {})
        budget_path = "/trips/{trip_id}/budget"
        if budget_path in paths:
            print(f"Found path: {budget_path}")
        else:
            print(f"Path {budget_path} NOT FOUND in schema")
            print("Available paths:")
            for p in sorted(paths.keys()):
                print(f" - {p}")
    else:
        print(f"Failed to get schema: {resp.status_code}")

if __name__ == "__main__":
    check_schema()
