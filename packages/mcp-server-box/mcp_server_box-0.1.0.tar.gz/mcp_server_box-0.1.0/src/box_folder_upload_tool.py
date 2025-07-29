"""
Box folder recursive upload tool.

This module provides functionality to recursively upload local folders to Box,
preserving the folder structure and handling file conflicts intelligently.
"""
import fnmatch
import json
import os
import pathlib
from typing import Dict, List, Optional, cast

from boxsdk.exception import BoxAPIException
from mcp.server.fastmcp import Context

from box_ai_agents_toolkit import BoxClient, box_create_folder, box_upload_file


async def box_upload_folder_tool(
    ctx: Context,
    local_folder_path: str,
    box_folder_id: str = "0",
    include_patterns: List[str] = None,
    exclude_patterns: List[str] = None,
    report_progress: bool = True
) -> str:
    """Recursively upload a local folder to Box.
    
    Args:
        ctx (Context): The MCP context.
        local_folder_path (str): Path to the local folder to upload.
        box_folder_id (str): ID of the destination Box folder. Defaults to root ("0").
        include_patterns (List[str], optional): List of file patterns to include (e.g. ["*.pdf", "*.docx"]).
        exclude_patterns (List[str], optional): List of file patterns to exclude (e.g. [".DS_Store", "thumbs.db"]).
        report_progress (bool): Whether to include detailed progress in the result. Defaults to True.
        
    Returns:
        str: JSON string with the result of the upload operation
    """
    # Get the Box client
    box_client: BoxClient = ctx.request_context.lifespan_context.client
    
    result = {
        "status": "success",
        "source_folder": local_folder_path,
        "destination_folder_id": box_folder_id,
        "files_uploaded": 0,
        "files_updated": 0,
        "folders_created": 0,
        "folders_existed": 0,
        "errors": [],
    }
    
    if report_progress:
        result["details"] = []
    
    try:
        # Normalize and check the local folder path
        local_folder = pathlib.Path(os.path.expanduser(local_folder_path))
        if not local_folder.is_dir():
            return json.dumps({
                "status": "failed",
                "error": f"'{local_folder_path}' is not a valid directory"
            })
        
        # Define a helper function for checking patterns
        def should_include(path):
            """Check if a path should be included based on patterns.

            Args:
                path: A pathlib.Path object to check

            Returns:
                bool: True if the path should be included, False otherwise
            """
            path_str = str(path)

            # Check exclude patterns first
            if exclude_patterns:
                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path.name, pattern):
                        return False

            # Then check include patterns
            if include_patterns:
                for pattern in include_patterns:
                    if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path.name, pattern):
                        return True
                return False  # If include patterns specified but none match, exclude

            return True  # Include by default if no patterns match
        
        # Define recursive helper function
        def process_folder(folder_path, current_box_folder_id):
            try:
                # Process all items in the folder
                for item in folder_path.iterdir():
                    # Skip if item doesn't match our include/exclude filters
                    if not should_include(item):
                        continue
                        
                    if item.is_dir():
                        # It's a folder, create it and recursively process
                        try:
                            folder_result = create_box_folder(box_client, item.name, current_box_folder_id)
                            if folder_result["action"] == "created":
                                result["folders_created"] += 1
                            else:
                                result["folders_existed"] += 1
                                
                            if report_progress:
                                result["details"].append(
                                    f"Folder {folder_result['action']}: {item.name} (ID: {folder_result['id']})"
                                )
                                
                            # Recursively process this folder
                            process_folder(item, folder_result["id"])
                            
                        except Exception as e:
                            error_msg = f"Error processing folder {item}: {str(e)}"
                            result["errors"].append(error_msg)
                            if report_progress:
                                result["details"].append(error_msg)
                    else:
                        # It's a file, upload it
                        try:
                            file_result = file_upload(box_client, str(item), current_box_folder_id)
                            if file_result["action"] == "uploaded":
                                result["files_uploaded"] += 1
                            else:
                                result["files_updated"] += 1
                                
                            if report_progress:
                                result["details"].append(
                                    f"File {file_result['action']}: {item.name} (ID: {file_result['id']})"
                                )
                                
                        except Exception as e:
                            error_msg = f"Error uploading file {item}: {str(e)}"
                            result["errors"].append(error_msg)
                            if report_progress:
                                result["details"].append(error_msg)
            
            except Exception as e:
                error_msg = f"Error processing folder {folder_path}: {str(e)}"
                result["errors"].append(error_msg)
                if report_progress:
                    result["details"].append(error_msg)
        
        # Start the recursive upload
        process_folder(local_folder, box_folder_id)
            
        # Update the final status
        if result["errors"]:
            result["status"] = "partial" if (result["files_uploaded"] > 0 or result["files_updated"] > 0) else "failed"
                
    except Exception as e:
        result["status"] = "failed"
        result["errors"].append(f"Fatal error: {str(e)}")
    
    return json.dumps(result)


def file_upload(client: BoxClient, file_path: str, folder_id: str, new_file_name: str = "") -> Dict:
    """Upload a file to Box. Handles binary and text files appropriately.
    
    Args:
        client (BoxClient): Box client instance
        file_path (str): Path to the file to upload
        folder_id (str): ID of the destination folder
        new_file_name (str): Optional new name to give the file in Box
        
    Returns:
        dict: Information about the uploaded file (ID and name)
    """
    try:
        # Normalize the path and check if file exists
        file_path_expanded = os.path.expanduser(file_path)
        if not os.path.isfile(file_path_expanded):
            raise FileNotFoundError(f"File '{file_path}' not found.")

        # Determine the file name to use
        actual_file_name = new_file_name.strip() or os.path.basename(file_path_expanded)
        
        # Determine file extension to detect binary types
        _, ext = os.path.splitext(actual_file_name)
        binary_exts = {".docx", ".pptx", ".xlsx", ".pdf", ".jpg", ".jpeg", ".png", ".gif", 
                       ".zip", ".mp3", ".mp4", ".avi", ".mov", ".exe", ".tar", ".gz", ".rar"}
        
        # Read file content as bytes for binary types, else as text
        if ext.lower() in binary_exts:
            # Binary file: read raw bytes
            with open(file_path_expanded, "rb") as f:
                content = f.read()
        else:
            # Text file: read as UTF-8
            with open(file_path_expanded, "r", encoding="utf-8") as f:
                content = f.read()
                
        # Check if file exists already (preflight check)
        file_id = None
        try:
            # Get the folder
            folder = client.folder(folder_id).get()
            # Try preflight check for uploading a new file
            folder.preflight_check(os.path.getsize(file_path_expanded), actual_file_name)
        except BoxAPIException as err:
            if err.code == "item_name_in_use":
                # File exists, get its ID
                file_id = err.context_info["conflicts"]["id"]
            else:
                raise err
                
        # Upload or update the file
        if file_id is not None:
            # Update existing file (new version)
            file = client.file(file_id).update_contents(file_path_expanded)
            return {"id": file.id, "name": file.name, "action": "updated"}
        else:
            # Upload new file
            result = box_upload_file(client, content, actual_file_name, folder_id)
            result["action"] = "uploaded"
            return result
            
    except Exception as e:
        raise Exception(f"Error uploading file: {str(e)}")


def create_box_folder(client: BoxClient, folder_name: str, parent_folder_id: str) -> Dict:
    """Create a folder in Box, or get it if it already exists.
    
    Args:
        client (BoxClient): Box client instance
        folder_name (str): Name of the folder to create
        parent_folder_id (str): ID of the parent folder
        
    Returns:
        dict: Information about the created/existing folder
    """
    try:
        # Try to create the folder
        try:
            folder = box_create_folder(client, folder_name, parent_folder_id)
            return {"id": folder.id, "name": folder.name, "action": "created"}
        except BoxAPIException as err:
            if err.code == "item_name_in_use":
                # Folder exists, get its ID
                conflicts = err.context_info["conflicts"]
                if isinstance(conflicts, list):
                    folder_id = conflicts[0]["id"]
                else:
                    folder_id = conflicts["id"]
                
                folder = client.folder(folder_id).get()
                return {"id": folder.id, "name": folder.name, "action": "exists"}
            else:
                raise err
                
    except Exception as e:
        raise Exception(f"Error creating folder: {str(e)}")