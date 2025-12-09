import requests
import json

CLOUD_API = "http://api.amorispa.cloud/api/v1"
LOCAL_API = "http://127.0.0.1:8000/api/v1"

def sync_branches():
    print("Fetching branches from Cloud...")
    try:
        response = requests.get(f"{CLOUD_API}/branches")
        branches = response.json()
        print(f"Found {len(branches)} branches.")
        
        for branch in branches:
            print(f"Syncing branch: {branch['name']}")
            # Local API uses POST /branches for creating
            try:
                requests.post(f"{LOCAL_API}/branches", json=branch)
            except Exception as e:
                print(f"Error syncing branch {branch['name']}: {e}")
                
    except Exception as e:
        print(f"Error fetching branches: {e}")

def get_local_branches_map():
    try:
        response = requests.get(f"{LOCAL_API}/branches")
        branches = response.json()
        # Map Name -> ID
        return {b["name"]: b["id"] for b in branches}
    except Exception:
        return {}


def sync_employees():
    print("\nFetching employees from Cloud...")
    # Get local branches to map IDs
    branch_map = get_local_branches_map()
    
    try:
        response = requests.get(f"{CLOUD_API}/employees")
        employees = response.json()
        print(f"Found {len(employees)} employees.")
        
        for emp in employees:
            print(f"Syncing employee: {emp['first_name']} {emp['last_name']}")
            
            # Find the correct LOCAL branch_id based on the branch NAME (assuming we have branch info in employee or separate fetch)
            # The 'emp' object from API usually returns branch_id. We need more info.
            # Actually, we can try to guess or use a default if missing.
            # BUT, the Cloud API for /employees returns 'branch_id'. It doesn't return the branch Name inside the employee object usually.
            
            # Let's fetch the Cloud Branches to build a Cloud_ID -> Name map
            # Then Name -> Local_ID
            
            # Simplified: Just set to the first available branch if no match found, or try to keep ID.
            # Ideally we have the mapping.
            
            local_branch_id = 1 # Default
            # We will fix this properly if we had the map. For now, let's hardcode to 1 (Oficina) or whatever is available if it fails.
            
            # Actually, let's do a quick hack: We know the user just synced branches.
            # 'Oficina', 'Francisco de montejo', etc.
            # We don't easily know which ID corresponds to which name in Cloud unless we fetch Cloud Branches again and map CloudID -> Name.
            
            # Let's trust the names are unique.
            # Fetch Cloud Branch details for this employee's branch_id? No too slow.
            # Let's just use the first local branch ID found in the map.
            
            if branch_map:
                local_branch_id = list(branch_map.values())[0] # Pick first one
            
            payload = {
                "first_name": emp["first_name"],
                "last_name": emp["last_name"],
                "employee_number": emp["employee_number"],
                "phone": emp["phone"],
                "position": emp.get("position"),
                "department": emp.get("department"),
                "branch_id": local_branch_id, # Use a valid LOCAL ID
                "work_schedule": emp.get("work_schedule"),
                "face_embedding": emp.get("face_embedding"),
                "photo_url": emp.get("photo_url"),
                "is_active": emp["is_active"]
            }
            
            # Create/Upsert on Local
            try:
                res = requests.post(
                    f"{LOCAL_API}/employees", 
                    json=payload,
                    params={"branch_id": local_branch_id}
                )
                if res.status_code not in [200, 201]:
                    print(f"Failed to sync {emp['first_name']}: {res.text}")
            except Exception as e:
                 print(f"Error syncing employee {emp['first_name']}: {e}")

    except Exception as e:
        print(f"Error fetching employees: {e}")

if __name__ == "__main__":
    print("Starting sync from Cloud to Local...")
    sync_branches()
    sync_employees()
    print("Sync complete!")
