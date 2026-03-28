import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

class DBManager:
    def __init__(self):
        url = os.getenv("supabase_url")
        key = os.getenv("supabase_key")
        self.client: Client = create_client(url, key)

    def get_projects(self):
        """Fetch all projects for the main table."""
        response = self.client.table("item_master").select("*").execute()
        return response.data

    def update_project(self, project_id, update_data):
        """Update a specific project row."""
        return self.client.table("item_master").update(update_data).eq("id", project_id).execute()

# Initialize a single instance to use across the app
db = DBManager()