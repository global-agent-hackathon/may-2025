import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.tools.reasoning import ReasoningTools
from typing import List, Dict
from dotenv import load_dotenv
import requests
import json
from db_utils import add_entry_in_db, fetch_news_from_db, init_db, update_entry_in_db

load_dotenv()

class AgnoAgent:
    def __init__(self):
        self.model = Gemini(
            id="gemini-2.0-flash",
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.DB_CONFIG = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT")
        }

        init_db(self.DB_CONFIG)

        self.base_prompt = (
            "You are a world-class chess news curator, renowned for your insightful and engaging reporting. "
            "Your task is to provide the latest and most relevant news from the world of chess."
            "Use chess.com , chessbase and lichess news websites as your source."
        )

    def get_news(self):

        existing_news = fetch_news_from_db(self.DB_CONFIG)
        stored_context = self.structure_existing_news(existing_news)

        prompt = f"{self.base_prompt}\n\n" \
                 "Adhere to the following principles:\n" \
                "Your primary goal is to deliver news that meets the highest journalistic standards.  Adhere to the following principles:\n" \
                "Use chess.com , chessbase and lichess news websites as your source.\n" \
                "* Relevancy: Ensure the news is directly related to chess (e.g., tournaments, matches, player profiles, rule changes, major announcements). Avoid tangential or marginally related information.\n" \
                "* Recency: Prioritize covering news only from the year 2025.\n" \
                "* Accuracy: Verify the facts presented in the news.  Cross-reference information from multiple reliable sources to ensure correctness.  Do not include rumors or unverified claims.\n" \
                "* Comprehensiveness: Go beyond simple reporting.  Provide sufficient context and background information to help the reader understand the significance of the news.  Summarize complex events clearly and concisely.\n" \
                "* Objectivity: Present the news in a neutral and unbiased manner.  Avoid expressing personal opinions or taking sides in controversies.  If controversies are reported, present all sides fairly.\n" \
                "* Clarity and Style: Write in clear, concise, and grammatically correct English.  Use a professional and engaging tone.  Avoid jargon or overly technical language, unless it is clearly explained.  The phrasing should be similar to that used by major news outlets like the Associated Press, Reuters, or ESPN.\n" \
                "* Timeliness: Prioritize recent events.  Only include news published within the last 10 days.  Give preference to very recent news.\n" \
                "* Source Reliability: Only use information from reputable sources, such as official tournament websites, FIDE announcements, established chess news publications (e.g., ChessBase, Chess.com), and major news organizations.  Do not use information from personal blogs, forums, or social media unless it can be verified from a more reliable source.\n\n" \
                 "### Stored News Context:\n" \
                 f"{stored_context}\n" \
                 "### Storage and Replacement Logic:\n" \
                 "* Do not repeat existing news or slightly reworded variants.\n" \
                 "* If you can provide a follow-up (continuation/development) to any stored item, prioritize that.\n" \
                 "  - If a follow-up is generated, set `replace_id` to that item's ID and include the new content.\n" \
                 "* If no follow-up is possible, generate a news item on a different topic and set `replace_id` to the oldest item’s ID.\n" \
                 "* let's keep a probability of 60 percent of choosing a follow up news and 40 percent of going ahead with a news on a different topic.\n" \
                 "* If fewer than 3 items were stored in the stored news context: if you generate a follow up news, just follow the same process and generate `replace_id`, else if it's a new news, simply add the new item as a new entry without replacement.\n\n" \
                 "Output a JSON object with these fields:\n" \
                 "- `title`: A concise and attention-grabbing headline that accurately reflects the content of the news.\n" \
                 "- `description`: A detailed summary of the news, including all the essential information.  The summary should be well-structured, easy to read (~150-200 words).\n" \
                 "- `source_links`: array of source URLs\n" \
                 "- `timestamp`: ISO-formatted datetime of generation\n" \
                 "- `replace_id`: ID of the item to replace (null if adding new), This ID should be an integer from the provided set of 3 or less news\n"

        agent = Agent(
            model=self.model,
            tools=[
                DuckDuckGoTools(),
                Newspaper4kTools(),
                ReasoningTools(),
            ],
            instructions=[prompt],
            markdown=False
        )

        response = agent.run("Get the most recent and important chess news.")
        result = json.loads(response.content[7:-3])

        item = {
            "data": {
                "title": result["title"],
                "description": result["description"],
                "source_links": result["source_links"],
            },
            "timestamp": result["timestamp"]
        }

        if result["replace_id"]:
            update_entry_in_db(self.DB_CONFIG, result["replace_id"], item)
        else:
            add_entry_in_db(self.DB_CONFIG, item)

        return item["data"]
    
    def structure_existing_news(self, news_list):
        return "\n".join([
                f"ID: {n['id']} Title: {n['title']} Timestamp: {n['timestamp']}" for n in news_list
            ])
    

def translate_text(source: Dict[str, str], target_languages: List[str]) -> List[Dict[str, any]]:

    url = "https://api.sarvam.ai/translate"
    target_language_codes = ["en-IN", "hi-IN", "bn-IN", "gu-IN", "kn-IN", "ml-IN", "mr-IN", "od-IN", "pa-IN", "ta-IN", "te-IN"]
    translations = []

    for target_lang in target_languages:
        if target_lang not in target_language_codes:
            print(f"Unsupported language code: {target_lang}")
            continue
        
        translation = {}
        for key in source.keys():
            if key == 'source_links':
                continue
            payload = {
                "input": source[key],
                "source_language_code": "auto",
                "target_language_code": target_lang,
                "speaker_gender": "Male",
                "mode": "formal",
                "model": "mayura:v1",
                "enable_preprocessing": False,
                "output_script": "roman",
                "numerals_format": "international",
                "output_script": "fully-native"
            }
            headers = {'api-subscription-key': os.getenv("SARVAM_API_KEY")}

            response = requests.request("POST", url, json=payload, headers=headers)
            if response.status_code == 200:
                translation[key] = (response.json())["translated_text"]
            else:   
                print(f"Error: {response.status_code}")
                print(response.text)
        
        translation['target_language_code'] = target_lang
        translations.append(translation)

    return translations
