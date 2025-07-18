from supabase import create_client
import httpx
import os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # not the anon key!

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


# Example user helpers

async def get_user_by_token(token: str):
    url = f"{SUPABASE_URL}/auth/v1/user"
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": SUPABASE_SERVICE_KEY,
    }

    response = httpx.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# 2. Fetch the user from your `profiles` table using user_id
async def get_user_by_id(user_id: str):
    result = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    return result.data
"""async def get_user_by_token(token: str):
        return {
        "id": "695b51b9-5c93-4992-95fb-3eba6671d4f2",  
        "email": "serhatalpacar@outlook.com",
        "name": "Logan"
    }"""
""""
    print("🧪 Received token:", token)    
    ""Get user information by token - returns None if invalid token instead of raising exception""
    
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {token}"
    }

    try:
        response = supabase.auth.get_user(token)
        user = response.user
        if user:
            return {"id": user.id, "email": user.email, "name": user.user_metadata.get("name", "User")}
        print("No user found for provided token")
        return None
    except Exception as e:
        print(f"Supabase Auth Error: {e}")
        return None  # Return None instead of raising an exception"""

async def get_user_stats(user_id: str):
    # Simulate activity streak (replace with actual Supabase logic later)
    return {"streak_days": 11}

async def get_user_projects(user_id: str, limit=5):
    response = supabase.from_("projects").select("*").eq("user_id", user_id).limit(limit).execute()
    return response.data if response.data else []

async def get_user_recent_entries(user_id: str, limit=5):
    response = supabase.from_("daily_entries").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
    return response.data if response.data else []

async def get_latest_project(user_id: str):
    response = supabase.from_("projects")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("updated_at", desc=True)\
        .limit(1)\
        .execute()
    return response.data[0] if response.data else None

async def get_latest_journey(project_id: str):
    response = supabase.from_("journeys")\
        .select("*")\
        .eq("project_id", project_id)\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()
    return response.data[0] if response.data else None

async def get_profile_by_user_id(user_id: str):
    response = supabase.from_("profiles").select("name, bio, location, avatar_url").eq("id", user_id).single().execute()
    return response.data if response.data else None
