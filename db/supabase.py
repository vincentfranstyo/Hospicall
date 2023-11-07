import os
from supabase import create_client, Client
from config import url, api_key

api_url: str = os.environ.get(url)
key: str = os.environ.get(api_key)


def create_supabase_client():
    supabase: Client = create_client(url, key)
    return supabase
