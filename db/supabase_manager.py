import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("API_URL")
key: str = os.environ.get("API_SERVICE_KEY")


def create_supabase_client():
    supabase: Client = create_client(url, key)
    return supabase
