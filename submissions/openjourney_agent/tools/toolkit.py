from openjourney_agent.supabase_client import supabase
from agno.tools.toolkit import Toolkit  
from pydantic import BaseModel
from agno.tools import tool
from agno.vectordb.pgvector import PgVector, SearchType
from agno.utils.log import logger
from typing import Optional
from dotenv import load_dotenv
import os
from agno.memory.v2.schema import UserMemory
from agno.memory.v2.memory import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from typing import List
from agno.embedder.google import GeminiEmbedder
from openjourney_agent.vector.custom_pgvector import CustomPgVector
from agno.agent import Agent, AgentKnowledge
from exa_py import Exa

exa = Exa(api_key=os.getenv("EXA_API_KEY"))

memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")
memory = Memory(db=memory_db)

load_dotenv()

gemini_embedder = GeminiEmbedder(dimensions=768)

last_found_profiles = None

vector_db = CustomPgVector(
    table_name="journey_search_view",
    schema="public",
    db_url=os.getenv("SUPABASE_DB_URL"),
    search_type=SearchType.hybrid,
    embedder=GeminiEmbedder(dimensions=768),
)
""""
vector_db = PgVector(
    table_name="journeys",
    schema="public",
    db_url=os.getenv("SUPABASE_DB_URL"),  
    search_type=SearchType.vector,
    embedder=gemini_embedder
)"""

knowledge_base = AgentKnowledge(
    vector_db=vector_db,
    content_column=["id", "title", "description", "embedding", "user_id"],  
)

class SearchQueryInput(BaseModel):
    query: str
class DisplayProfilesInput(BaseModel):
    user_ids: List[str]

class OpenJourneyToolkit(Toolkit):
    def __init__(self, user_id, knowledge: AgentKnowledge):
        super().__init__(name="openjourney_toolkit")
        self.user_id = user_id
        self.knowledge = knowledge
        self.last_found_profiles = []
        self.register(self.create_journey)
        self.register(self.log_entry)
        self.register(self.create_project)
        self.register(self.resume_latest_project)
        self.register(self.update_project_status)
        self.register(self.display_profiles_from_results)
        #self.register(self.find_related_journeys_and_people)
        self.register(self.show_all_projects)
        self.register(self.exa_search_personal_website)
        self.register(self.get_linkedin_from_name)
        self.register(self.search_founders_in_field)
        self.register(self.get_latest_news_about)
        self.register(self.search_similar_builders)
        self.register(self.compare_startups)

    def create_journey(self, project_id: Optional[str] = None, project_title: Optional[str] = None, title: Optional[str] = None, description: Optional[str] = None, category: str = "general") -> str:
        """
        Create a new journey under an existing project.
        You can provide either `project_id` or `project_title`.
        """
        try:
            if not self.user_id:
                return "❌ No user_id available."

            # Resolve project_id if title is provided
            if not project_id:
                if project_title:
                    response = supabase.from_("projects").select("id").eq("title", project_title).eq("user_id", self.user_id).maybe_single().execute()
                    if response.data:
                        project_id = response.data["id"]
                    else:
                        return f"❌ No project found with title '{project_title}'."
                else:
                    # Fallback: get the most recent project
                    response = supabase.from_("projects").select("id").eq("user_id", self.user_id).order("created_at", desc=True).limit(1).execute()
                    if response.data:
                        project_id = response.data[0]["id"]
                    else:
                        return "❌ No projects found. Please create one first."

            # Fallbacks
            title = title or "Untitled Journey"
            description = description or "No description."

            supabase.table("journeys").insert({
                "user_id": self.user_id,
                "project_id": project_id,
                "title": title,
                "description": description,
                "category": category,
            }).execute()
            return f"✅ Journey '{title}' created."
        except Exception as e:
            return f"❌ Failed to create journey: {e}"

    def log_entry(self, content: str, mood: str = None) -> str:
        try:
            if not self.user_id:
                return "❌ No user_id available."

            data = {
                "user_id": self.user_id,
                "message": content,  # content maps to message here
                "mood": mood,
            }

            memory.add_user_memory(
                    user_id=self.user_id,
                    memory=UserMemory(memory=content, topics=["journal", "mood" if mood else "general"])
                )

            supabase.table("daily_entries").insert(data).execute()
            return "📓 Journal entry saved successfully."
        except Exception as e:
            logger.warning(f"Failed to log entry: {e}")
            return f"❌ Failed to save entry: {e}"
        
    def create_project(self, title: Optional[str] = None, description: Optional[str] = None, status: str = "in_progress") -> str:
        """
        Create a new project when the user provides a title and description.
        Use this tool if the user says they want to create a new project.

        """
        try:
            if not self.user_id:
                return "❌ No user_id available."

            title = title or "Untitled Project"
            description = description or "No description."

            result = supabase.table("projects").insert({
                "user_id": self.user_id,
                "title": title,
                "description": description,
                "status": status,
            }).execute()
            return f"✅ Project '{title}' created."
        except Exception as e:
            return f"❌ Failed to create project: {e}"
        
    def resume_latest_project(self) -> str:
        try:
            project_resp = supabase.from_("projects")\
                .select("*")\
                .eq("user_id", self.user_id)\
                .order("updated_at", desc=True)\
                .limit(1)\
                .execute()

            if not project_resp.data:
                return "❌ You don’t have any active projects yet."

            project = project_resp.data[0]

            journey_resp = supabase.from_("journeys")\
                .select("*")\
                .eq("project_id", project["id"])\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()

            journey = journey_resp.data[0] if journey_resp.data else None
            summary = journey["description"] if journey else "No progress yet."

            return f"🚀 Your latest project is **{project['title']}**. Most recent note:\n\n> {summary}\n\nWant to log your next step?"

        except Exception as e:
            logger.warning(f"Failed to resume latest project: {e}")
            return f"❌ Failed to retrieve latest project info."

    def update_project_status(self, project_id: str, new_status: str) -> str:
        try:
            response = supabase.table("projects").update({
                "status": new_status
            }).eq("id", project_id).execute()

            if response.data:
                return f"✅ Project status updated to **{new_status}**."
            else:
                return "❌ Failed to update the project. Please check the ID."
        except Exception as e:
            return f"❌ Error updating project: {e}"
         
    def display_profiles_from_results(self, meta_datas: list[dict]) -> str:
        "Display a list of user profiles based on metadata from search results."

        if not meta_datas:
            return "No profiles to display."

        profiles = []
        for meta in meta_datas:
            name = meta.get("profile_name", "Unknown")
            location = meta.get("location") or "Unknown"
            bio = meta.get("bio") or "No bio available"
            user_id = meta.get("user_id")
            profile_url = f"https://openjourney.club/profile/{user_id}" if user_id else None

            # 🧠 NEW: Extract social links if present
            github = meta.get("github")
            linkedin = meta.get("linkedin")
            x_handle = meta.get("x")

            links = []
            if github:
                links.append(f"[GitHub](https://github.com/{github})")
            if linkedin:
                links.append(f"[LinkedIn](https://linkedin.com/in/{linkedin})")
            if x_handle:
                links.append(f"[X](https://x.com/{x_handle})")

            social_links = " | ".join(links) if links else "No social links"

            profile_block = f"""**[{name}]({profile_url})**
    🌍 Location: {location}  
    📝 {bio}  
    🔗 {social_links}"""

            profiles.append(profile_block)

        return "\n\n---\n\n".join(profiles)
    
    def find_related_journeys_and_people(self, query: str) -> str:
        """
        Find journeys and related people based on a semantic query.
        """
        
        try:
            results = self.knowledge.search(query)

            user_ids = []
            fallback_profiles = []

            for doc in results:
                print(doc)
                if isinstance(doc, dict):  # If your vector returns plain dict
                     metadata = doc.get("meta_data", {}) or {}
                else:
                    metadata = getattr(doc, "metadata", None) or getattr(doc, "meta_data", {})

                if "user_id" in metadata:
                    user_ids.append(metadata["user_id"])

                elif "profile_name" in metadata or "name" in metadata:
                    fallback_profiles.append(
                        f"""
    👤 **{metadata.get('profile_name') or metadata.get('name', 'Unknown')}**
    📝 {metadata.get('bio', 'No bio available.')}
    🚀 {metadata.get('title', '')}
                        """
                    )

            if user_ids:
                return self.display_profiles_from_results(user_ids)

            if fallback_profiles:
                return "\n---\n".join(fallback_profiles)

            return "⚠️ No related makers found."

        except Exception as e:
            return f"❌ Error finding people: {e}"
        
    def show_all_projects(self) -> str:
        try:
            projects_resp = supabase.from_("projects")\
                .select("*")\
                .eq("user_id", self.user_id)\
                .order("updated_at", desc=True)\
                .execute()

            if not projects_resp.data:
                return "❌ You don’t have any projects yet."

            cards = []
            for project in projects_resp.data:
                title = project.get("title", "Untitled")
                tech_stack = project.get("tech_stack", "Not specified")
                ai_tools = project.get("ai_tools", "")
                status = project.get("status", "Unknown")
                mrr = project.get("mrr", 0)
                arr = project.get("arr", 0)

                # Fetch latest journey for project
                journey_resp = supabase.from_("journeys")\
                    .select("description")\
                    .eq("project_id", project["id"])\
                    .order("created_at", desc=True)\
                    .limit(1)\
                    .execute()

                last_progress = journey_resp.data[0]["description"] if journey_resp.data else "No progress yet."

                card = (
                    f"🧠 **{title}**\n"
                    f"🔧 Tech Stack: {tech_stack}\n"
                    f"🤖 AI Tools: {ai_tools}\n"
                    f"📈 MRR: ${mrr} | ARR: ${arr}\n"
                    f"📌 Status: {status}\n"
                    f"📝 _{last_progress}_\n"
                    f"---"
                )
                cards.append(card)

            return "\n\n".join(cards)

        except Exception as e:
            return f"❌ Failed to retrieve projects: {e}"
        
    def exa_search_personal_website(self, name: str, school: str = '') -> tuple:
        """
        Searches for a personal website based on name and school, excluding major platforms.
        """
        query = f"{name} {school}"
        keyword_search = exa.search_and_contents(
            query, 
            type="keyword", 
            text={"include_html_tags": False}, 
            num_results=1, 
            exclude_domains=['linkedin.com', 'github.com', 'twitter.com']
        )
        if keyword_search.results:
            result = keyword_search.results[0]
            return result.url, result.text
        return (None, None)

    def get_linkedin_from_name(self, name: str, school: str = '') -> str:
        """
        Searches LinkedIn for a person by name and school.
        """
        query = f"{name} {school}"
        keyword_search = exa.search(
            query, 
            num_results=1, 
            type="keyword", 
            include_domains=['linkedin.com']
        )
        if keyword_search.results:
            return keyword_search.results[0].url
        return None
        
    def search_founders_in_field(self, query: str, location: str = "") -> list:
        '''
        Search for startup founders in a specific field and location.
        '''
        search_query = f"{query} startup founder site:linkedin.com"
        if location:
            search_query += f" {location}"
        results = exa.search_and_contents(query=search_query, type="keyword", num_results=5)
        return [(r.title, r.url) for r in results.results]


    def get_latest_news_about(self, term: str) -> str:
        '''
        Get latest startup-related news for a company, person or product.
        '''
        results = exa.search_and_contents(
            query=f"{term} site:techcrunch.com OR site:tech.eu OR site:news.ycombinator.com",
            type="keyword",
            num_results=3
        )
        return "\\n\\n".join([f"📰 [{r.title}]({r.url})\\n{r.text[:200]}..." for r in results.results])


    def search_similar_builders(self, keyword: str) -> list:
        '''
        Find people or projects working on similar topics.
        '''
        results = exa.search_and_contents(
            query=keyword,
            type="keyword",
            num_results=5,
            exclude_domains=[]
        )
        return [(r.title, r.url, r.text[:150]) for r in results.results]


    def compare_startups(self, a: str, b: str) -> str:
        '''
        Compare two startups based on recent web posts.
        '''
        query = f"{a} vs {b} startup comparison"
        results = exa.search_and_contents(query=query, type="keyword", num_results=5)
        return "\\n\\n".join([f"📌 [{r.title}]({r.url})\\n{r.text[:250]}..." for r in results.results])

    
    """
    def display_profiles() -> str:
        global last_found_profiles

        if not last_found_profiles:
            return "⚠️ No recent journeys found to extract profiles from."

        user_ids = list(set([r["user_id"] for r in last_found_profiles if "user_id" in r]))

        if not user_ids:
            return "⚠️ No user IDs found in journeys."

        try:
            response = supabase.from_("profiles").select("*").in_("id", user_ids).execute()
            profiles = response.data

            if not profiles:
                return "⚠️ No matching profiles found."

            formatted = []
            for p in profiles:
                card = f"""\
              #  👤 **{p.get('name', 'Unnamed')}**
              #  📝 **Bio:** {p.get('bio', 'No bio')}
              #  🌍 **Location:** {p.get('location', 'Unknown')}
              #  📬 **Contact:** {p.get('email', 'No email')}
    """
                formatted.append(card)

            return "\n---\n".join(formatted)

        except Exception as e:
            return f"❌ Error fetching profiles: {e}"
    """
        
    """""   
    def find_related_journeys_and_people(query: str) -> str:
        ""
        find_related_journeys_and_people, Find people and journeys related to a topic
        Find journeys and people related to a search query (e.g., AI, e-commerce).

        ""
        results = vector_db.search(query, top_k=5)
        if not results:
            return "No similar journeys found."
        return "\n\n".join([f"{r['title']}: {r['description']}" for r in results])"""