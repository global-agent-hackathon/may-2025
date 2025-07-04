import json
from groq import Groq
from typing import List, Dict, Optional
from datetime import datetime, date

from core.config import settings
from core.weaviate_client import get_weaviate_client, WEAVIATE_CLASS_NAME
from weaviate.classes.query import Filter, MetadataQuery

GROQ_CLIENT = Groq(api_key=settings.GROQ_API_KEY)
LLM_MODEL = "llama-3.1-8b-instant"

class QueryAgent:
    """
    QueryAgent is used to answer user queries based on the mails stored in the memory
    """
    def __init__(self,llm_model:str=LLM_MODEL):
        self.weaviate = get_weaviate_client()
        self.llm = GROQ_CLIENT
        self.model = llm_model

    async def answer_query(self, user_id: str, query: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        This function is used to answer the query of the user
        """
        if not self.weaviate:
            return "I'm sorry, I cannot access the knowledge base at the moment."
        
        try:
            email_collection = self.weaviate.collections.get(WEAVIATE_CLASS_NAME)
            
            response = email_collection.query.bm25(
                query=query,
                limit=5,
                filters=Filter.by_property("appUserId").equal(user_id),
                query_properties=["bodyPlainText", "subject", "fromAddress"],
                return_properties=["subject", "fromAddress", "toAddress", "bodyPlainText", "messageTimestampISO", "tags"],
                return_metadata=MetadataQuery(score=True)
            )

            retrieved_info_text = "No relevant information found in your emails for this query."
            if response.objects:
                retrieved_info_text = "Based on your emails, here's some relevant information:\n"
                for i, obj in enumerate(response.objects):
                    props = obj.properties
                    metadata = obj.metadata
                    retrieved_info_text += f"\n--- Email Snippet {i+1} "
                    if metadata:
                        if metadata.score is not None:
                             retrieved_info_text += f"(Score: {metadata.score:.4f}) "
                    retrieved_info_text += "---\n"
                    
                    retrieved_info_text += f"Subject: {props.get('subject', 'N/A')}\n"
                    retrieved_info_text += f"From: {props.get('fromAddress', 'N/A')}\n"
                    if props.get('toAddress'):
                        retrieved_info_text += f"To: {props.get('toAddress', 'N/A')}\n"

                    ts_iso_value = props.get('messageTimestampISO')
                    date_str_display = "N/A"

                    if isinstance(ts_iso_value, str) and ts_iso_value:
                        try:
                            dt_obj = datetime.fromisoformat(ts_iso_value.replace('Z', '+00:00'))
                            date_str_display = dt_obj.strftime('%Y-%m-%d')
                        except ValueError as ve_parse:
                            print(f"Warning: Could not parse timestamp string '{ts_iso_value}' for object. Error: {ve_parse}")
                            date_str_display = f"Invalid Date ({ts_iso_value[:10]}...)"
                        except TypeError as te_parse:
                            print(f"Warning: TypeError parsing timestamp '{ts_iso_value}'. This is unexpected if it's a string. Error: {te_parse}")
                            date_str_display = f"Unparseable Date ({ts_iso_value[:10]}...)"
                    elif ts_iso_value is not None:
                        print(f"Warning: messageTimestampISO is not a string: {ts_iso_value} (type: {type(ts_iso_value)})")
                        date_str_display = "Invalid Date Format"
                    
                    retrieved_info_text += f"Date: {date_str_display}\n"
                    
                    body_snippet = props.get('bodyPlainText', '')[:300]
                    retrieved_info_text += f"Content: {body_snippet}...\n"
                retrieved_info_text += "\n---\n"
            
            system_prompt = (
                "You are an AI assistant answering questions based on a user's email history from a vector database. "
                "Use ONLY the provided email snippets to answer. If not found, say so. Do not make up info."
            )
            prompt_messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                for msg_hist in conversation_history:
                    role = "assistant" if msg_hist["sender"] == "llm" else "user"
                    prompt_messages.append({"role": role, "content": msg_hist["text"]})

            user_content = f"User's question: \"{query}\"\n\nRetrieved from email history:\n{retrieved_info_text}"
            prompt_messages.append({"role": "user", "content": user_content})

            chat_completion = self.llm.chat.completions.create(
                messages=prompt_messages, model=self.model, temperature=0.3, max_tokens=500
            )
            return chat_completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"QueryAgent error with Weaviate: {e}")
            import traceback
            traceback.print_exc()
            return "I encountered an error trying to query your email history."


class WritingAgent:
    """
    Writing agent is used to help the user to drafts the mails
    """
    def __init__(self):
        self.weaviate = get_weaviate_client()
        self.llm = GROQ_CLIENT
        self.model = LLM_MODEL

    async def draft_email(self, user_id: str, recipient_to: str, user_prompt: str, current_draft_content: Optional[str] = None) -> Dict[str, str]:
        try:
            context_from_weaviate = ""
            if self.weaviate:
                try:
                    email_collection = self.weaviate.collections.get(WEAVIATE_CLASS_NAME)
                    search_query_for_context = f"Context for email to {recipient_to} about {user_prompt}"
                    if current_draft_content: search_query_for_context += f" current draft: {current_draft_content[:100]}"

                    response = email_collection.query.bm25(
                        query=search_query_for_context,
                        limit=2,
                        filters=Filter.by_property("appUserId").equal(user_id),
                        query_properties=["bodyPlainText", "subject"],
                        return_properties=["subject", "bodyPlainText"]
                    )
                    if response.objects:
                        context_from_weaviate = "For context, here's some related past information:\n"
                        for obj in response.objects:
                            props = obj.properties
                            context_from_weaviate += f"- Subject: {props.get('subject', '')} | Snippet: {props.get('bodyPlainText', '')[:100]}...\n"
                        context_from_weaviate += "\n---\n"
                except Exception as e_wv_write:
                    print(f"WritingAgent: Error fetching context from Weaviate: {e_wv_write}")
            
            system_prompt = (
                "You are an AI assistant that helps users draft professional and effective emails. "
                "Generate a suitable subject line and email body based on the user's instructions, the recipient, and any current draft content. "
                "If context from past emails is provided, use it to inform the tone and content. "
                "The output should be a JSON object with two keys: 'subject' and 'body'."
            )
            
            user_content = f"Recipient (To): {recipient_to}\n"
            user_content += f"User's instruction/goal for the email: \"{user_prompt}\"\n"
            if current_draft_content:
                user_content += f"Current draft content (refine or build upon this): \"{current_draft_content}\"\n"
            if context_from_weaviate:
                user_content += context_from_weaviate
            user_content += "\nPlease generate the email subject and body."

            prompt_messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}]
            chat_completion = self.llm.chat.completions.create(
                messages=prompt_messages, model=self.model, temperature=0.7, max_tokens=1000, response_format={"type": "json_object"}
            )
            response_content = chat_completion.choices[0].message.content
            
            
            try:
                email_draft = json.loads(response_content)
                if "subject" not in email_draft or "body" not in email_draft:
                    return {"subject": "Draft generated by AI Agent", "body": response_content}
                return email_draft
            except json.JSONDecodeError:
                return {"subject": "Draft (AI Error)", "body": response_content}


        except Exception as e:
            print(f"WritingAgent error: {e}")
            return {"subject": "Error", "body": "Failed to generate draft. Please try again."}
        
class DailySummaryAgent:
    """
    Daily Summary agent will help the user to provide insights about recents mails 
    """
    def __init__(self):
        self.weaviate = get_weaviate_client()
        self.llm = GROQ_CLIENT
        self.model = LLM_MODEL

    async def get_daily_summary(self, user_id: str) -> str:
        if not self.weaviate:
            return "I'm sorry, I cannot access the knowledge base for the daily summary."

        try:
            today_date = date.today()
            
            email_collection = self.weaviate.collections.get(WEAVIATE_CLASS_NAME)
            filters = Filter.by_property("appUserId").equal(user_id)
            
            response = email_collection.query.fetch_objects(
                filters=filters,
                limit=10,
                return_properties=["subject", "fromAddress", "bodyPlainText"]
            )

            todays_emails_texts = []
            if response.objects:
                for obj in response.objects:
                    props = obj.properties
                    text = f"From: {props.get('fromAddress', 'N/A')}\nSubject: {props.get('subject', 'N/A')}\nBody: {props.get('bodyPlainText', '')[:500]}..."
                    todays_emails_texts.append(text)
            
            if not todays_emails_texts:
                return f"No emails found in the knowledge base for today ({today_date.strftime('%B %d, %Y')}) to summarize."

            MAX_CONTEXT_FOR_SUMMARY = 7000
            concatenated_texts = "\n\n---\n\n".join(todays_emails_texts)
            if len(concatenated_texts) > MAX_CONTEXT_FOR_SUMMARY:
                concatenated_texts = concatenated_texts[:MAX_CONTEXT_FOR_SUMMARY] + "\n... (content truncated)"
            
            system_prompt = "Summarize these emails for today..."
            user_content = f"Please summarize emails from {today_date.strftime('%B %d, %Y')}:\n\n{concatenated_texts}"
            prompt_messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}]
            chat_completion = self.llm.chat.completions.create(
                messages=prompt_messages, model=self.model, temperature=0.5, max_tokens=600
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"DailySummaryAgent error with Weaviate: {e}")
            return "Error generating daily summary from the knowledge base."