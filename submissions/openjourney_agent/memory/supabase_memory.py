from supabase import create_client
from datetime import datetime
import os
from agno.storage.base import Storage

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseMemoryDb:
    def __init__(self, table_name="agent_memories"):
        self.table_name = table_name
        self.mode = "supabase"

    def get(self, session_id, key):
        response = supabase.table(self.table_name).select("value").eq("session_id", session_id).eq("key", key).single().execute()
        return response.data["value"] if response.data else None

    def set(self, session_id, key, value):
        existing = supabase.table(self.table_name).select("id").eq("session_id", session_id).eq("key", key).single().execute()
        if existing.data:
            return supabase.table(self.table_name).update({
                "value": value,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", existing.data["id"]).execute()
        else:
            return supabase.table(self.table_name).insert({
                "session_id": session_id,
                "key": key,
                "value": value
            }).execute()

    def delete(self, session_id, key):
        return supabase.table(self.table_name).delete().eq("session_id", session_id).eq("key", key).execute()


class SupabaseSessionStorage(Storage):
    def __init__(self, supabase):
        self.supabase = supabase
        self.mode = "supabase"

    async def read(self, session_id: str) -> str:
        try:
            response = self.supabase.from_("agent_sessions").select("session_data").eq("session_id", session_id).single().execute()
            if response.data and response.data.get("session_data"):
                return response.data["session_data"]
            return ""
        except Exception as e:
            print(f"❌ Failed to read session from Supabase: {e}")
            return ""

    async def write(self, session_id: str, content: str) -> None:
        try:
            # Upsert logic: insert or update based on session_id
            self.supabase.from_("agent_sessions").upsert({
                "session_id": session_id,
                "session_data": content
            }).execute()
        except Exception as e:
            print(f"❌ Failed to write session to Supabase: {e}")