# Box Shared Link Examples

This document provides examples of how to use the Box shared link tools.

## Creating a Shared Link

To create a shared link for a file, use the `box_create_share_link_tool` function:

```python
# Basic usage with default settings (open access)
shared_link = box_create_share_link_tool(file_id="12345")

# Create a shared link with company-only access
shared_link = box_create_share_link_tool(
    file_id="12345",
    access="company"
)

# Create a password-protected shared link
shared_link = box_create_share_link_tool(
    file_id="12345",
    password="SecurePassword123"
)

# Create a shared link with an expiration date
shared_link = box_create_share_link_tool(
    file_id="12345",
    unshared_at="2023-12-31T23:59:59Z"
)

# Create a shared link with a custom vanity URL
shared_link = box_create_share_link_tool(
    file_id="12345",
    vanity_name="my-important-document"
)

# Create a shared link without download permissions
shared_link = box_create_share_link_tool(
    file_id="12345",
    can_download=False
)
```

## Getting an Existing Shared Link

To retrieve information about an existing shared link, use the `box_get_shared_link_tool` function:

```python
# Get shared link information for a file
shared_link_info = box_get_shared_link_tool(file_id="12345")

# The response will include:
# - URL
# - Download URL
# - Vanity URL (if set)
# - Access level
# - Password protection status
# - Expiration date (if set)
# - Download count
# - Preview count
```

## Removing a Shared Link

To remove a shared link from a file, use the `box_remove_shared_link_tool` function:

```python
# Remove a shared link from a file
result = box_remove_shared_link_tool(file_id="12345")
```

## Complete Example

Here's a complete example workflow:

```python
# Create a shared link
create_result = box_create_share_link_tool(
    file_id="12345",
    access="company",
    can_download=True
)
print(f"Created shared link: {create_result}")

# Get information about the shared link
link_info = box_get_shared_link_tool(file_id="12345")
print(f"Shared link info: {link_info}")

# Remove the shared link when no longer needed
remove_result = box_remove_shared_link_tool(file_id="12345")
print(f"Removed shared link: {remove_result}")
```

## Accessing the Shared Link URL

To extract just the URL from the shared link response:

```python
import json

# Create shared link
response = box_create_share_link_tool(file_id="12345")
response_data = json.loads(response)

# Get the URL
shared_link_url = response_data["url"]
print(f"Shared link URL: {shared_link_url}")
```