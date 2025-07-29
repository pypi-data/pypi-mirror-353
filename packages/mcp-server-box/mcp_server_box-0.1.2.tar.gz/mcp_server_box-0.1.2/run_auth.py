from box_ai_agents_toolkit import authorize_app, get_oauth_client

print("Running authorization flow...")
try:
    result = authorize_app()
    print(f"Authorization result: {result}")
    
    print("Testing client connection...")
    client = get_oauth_client()
    user = client.users.get_user_me()
    print(f"Connected as: {user.name}")
except Exception as e:
    print(f"Error: {e}")