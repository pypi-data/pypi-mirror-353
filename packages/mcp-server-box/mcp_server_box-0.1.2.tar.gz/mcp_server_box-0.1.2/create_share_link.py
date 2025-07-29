#!/usr/bin/env python3
import os
import json
from box_ai_agents_toolkit import get_oauth_client, get_ccg_client

def create_share_link(file_id, access="open"):
    """Create a simple open shared link for a Box file.
    
    Args:
        file_id (str): The ID of the file to share
        access (str): Access level - 'open', 'company', or 'collaborators'
        
    Returns:
        dict: Information about the created shared link
    """
    try:
        # Check if we should use Client Credentials Grant instead of OAuth
        use_ccg = os.environ.get("BOX_USE_CCG", "").lower() in ("true", "1", "yes")
        
        if use_ccg:
            client = get_ccg_client()
        else:
            client = get_oauth_client()
        
        # Prepare minimal shared link parameters
        shared_link_params = {
            "access": access
        }
        
        # Create the shared link
        updated_file = client.files.update_file_by_id(
            file_id=file_id,
            shared_link=shared_link_params
        )
        
        # Return the shared link information
        if updated_file.shared_link:
            result = {
                "url": updated_file.shared_link.url,
                "effective_access": updated_file.shared_link.effective_access
            }
            return result
        else:
            return {"error": "Failed to create shared link"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # File IDs for Sendblue README files
    sendblue_readme_files = {
        "Sendblue_README.md": "1853586613797",
        "Sendblue_README_Updated.md": "1853590540589",
        "Sendblue-v1.6_README.md": "1854310449184",
        "Sendblue-v1.6_README_Updated.md": "1854347020539"
    }
    
    print("Creating share links for Sendblue README files:")
    results = {}
    
    for name, file_id in sendblue_readme_files.items():
        print(f"Creating share link for {name} (ID: {file_id})...")
        result = create_share_link(file_id)
        results[name] = result
        print(f"Result: {json.dumps(result, indent=2)}")
        print("-" * 40)
    
    # Save results to a file
    with open("share_links_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to share_links_results.json")