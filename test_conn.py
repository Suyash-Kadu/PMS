import os
import socket
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("supabase_url")

if url:
    host = url.replace("https://", "").strip()
    print(f"Trying to connect to {host} on port 443...")
    try:
        sock = socket.create_connection((host, 443), timeout=5)
        print("Connection successful!")
        sock.close()
    except Exception as e:
        print(f"Connection failed: {e}")
else:
    print("supabase_url not found in .env")
