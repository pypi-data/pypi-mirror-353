#!/usr/bin/env python3
import os
import sys
import json
from box_ai_agents_toolkit import get_oauth_client, get_ccg_client, box_upload_file

def upload_folder(local_folder_path, box_folder_id="0"):
    """Upload all files in a local folder to Box.

    Args:
        local_folder_path (str): Path to the local folder containing files to upload
        box_folder_id (str): ID of the destination Box folder

    Returns:
        dict: Results of the upload operation
    """
    # Get Box client
    use_ccg = os.environ.get("BOX_USE_CCG", "").lower() in ("true", "1", "yes")

    if use_ccg:
        client = get_ccg_client()
    else:
        client = get_oauth_client()

    # Validate the folder path
    if not os.path.isdir(local_folder_path):
        return {"error": f"Folder not found: {local_folder_path}"}

    # Get folder contents
    files = [f for f in os.listdir(local_folder_path) if os.path.isfile(os.path.join(local_folder_path, f))]

    if not files:
        return {"error": f"No files found in folder: {local_folder_path}"}

    results = {
        "folder": local_folder_path,
        "destination_folder_id": box_folder_id,
        "files_uploaded": [],
        "errors": []
    }

    # Upload each file
    for filename in files:
        file_path = os.path.join(local_folder_path, filename)
        try:
            # Determine file extension to detect binary types
            _, ext = os.path.splitext(filename)
            binary_exts = {".docx", ".pptx", ".xlsx", ".pdf", ".jpg", ".jpeg", ".png", ".gif",
                           ".mp3", ".mp4", ".avi", ".mov", ".exe", ".tar", ".gz", ".rar"}

            # Read file content appropriately
            if ext.lower() in binary_exts:
                # Binary file: read raw bytes
                with open(file_path, "rb") as f:
                    content = f.read()
            else:
                # Text file: read as UTF-8
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

            # Upload the file using the toolkit function
            result = box_upload_file(client, content, filename, box_folder_id)

            results["files_uploaded"].append({
                "name": filename,
                "id": result['id'],
                "size": os.path.getsize(file_path)
            })

            print(f"Uploaded: {filename} (ID: {result['id']})")

        except Exception as e:
            error_msg = f"Error uploading {filename}: {str(e)}"
            results["errors"].append(error_msg)
            print(error_msg)

    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload_folder.py <folder_path> [destination_folder_id]")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    destination_id = sys.argv[2] if len(sys.argv) > 2 else "0"
    
    print(f"Uploading folder: {folder_path} to Box folder ID: {destination_id}")
    result = upload_folder(folder_path, destination_id)
    
    # Print the result
    print("\nUpload results:")
    print(json.dumps(result, indent=2))
    
    # Save results to a file
    with open("folder_upload_results.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Results saved to folder_upload_results.json")