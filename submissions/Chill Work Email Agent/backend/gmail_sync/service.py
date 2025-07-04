from datetime import timezone
from sqlmodel import Session, select
from fastapi import HTTPException
from googleapiclient.errors import HttpError
from sqlalchemy.exc import IntegrityError

from core.config import settings
from core.utils import encrypt_value
from database.models import Mail, MailTagValue, User, MailRead
from .utils import build_gmail_service, parse_gmail_message_full
from agents.categorizing_agent import AgnoCategorizationAgent
from core.weaviate_client import get_weaviate_client, WEAVIATE_CLASS_NAME
import re 


async def sync_user_mails_logic(user_id: int, access_token: str, db: Session):
    service = build_gmail_service(access_token)
    
    if not service:
        raise HTTPException(status_code=503, detail="Failed to build Gmail service.")
    
    db_user = db.exec(select(User).where(User.id == user_id)).first()
    user_category_instruction = "Please categorize this email. If it seems to require direct attention, action, or is from a significant contact, mark it as 'Important'. Otherwise, if it's informational, a newsletter, or less critical, mark it as 'Archive'." # Default/Dummy
    if db_user and db_user.category_instruction:
        user_category_instruction = db_user.category_instruction
    
    categorization_agent = AgnoCategorizationAgent()
    
    weaviate_client = get_weaviate_client()

    message_ids_to_fetch = set()
    sync_queries = [
        {"labelIds": ["INBOX"], "q": None},
        {"labelIds": ["SENT"], "q": None},
        {"labelIds": None, "q": "-in:inbox -in:sent -is:draft -in:trash -in:spam"}
    ]

    for query_params in sync_queries:
        try:
            list_args = {"userId": "me", "maxResults": settings.MAX_GMAIL_RESULTS_PER_QUERY}
            if query_params["labelIds"]:
                list_args["labelIds"] = query_params["labelIds"]
            if query_params["q"]:
                list_args["q"] = query_params["q"]

            response = service.users().messages().list(**list_args).execute()
            for msg_info in response.get("messages", []):
                message_ids_to_fetch.add(msg_info["id"])
        except HttpError as e:
            print(f"Gmail API error listing messages ({query_params}): {e}")
            if e.resp.status == 401:
                raise HTTPException(status_code=401, detail="Gmail API authentication failed. Please login again.")
    limited_message_ids = list(message_ids_to_fetch)[:settings.MAX_MESSAGES_TO_PROCESS_FULL]

    newly_synced_count = 0
    updated_count = 0
    failed_parsing_count = 0
    api_error_count = 0
    categorization_failed_count = 0
    weaviate_added_count = 0
    weaviate_failed_count = 0
    
    weaviate_batch_data = []

    for msg_id in limited_message_ids:
        parsed_email_data = None
        try:
            message_data_full = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
            parsed_email_data = parse_gmail_message_full(message_data_full)

            if not parsed_email_data:
                failed_parsing_count += 1
                continue

            if "tags" not in parsed_email_data or parsed_email_data["tags"] is None:
                parsed_email_data["tags"] = []
            
            is_sent_mail = MailTagValue.SENT.value in parsed_email_data["tags"]

            existing_mail = db.exec(
                select(Mail).where(Mail.user_id == user_id, Mail.gmail_message_id == parsed_email_data["gmail_message_id"])
            ).first()
            
            if not existing_mail:
                if not is_sent_mail:
                    content_for_agent = parsed_email_data.get("content_plain") or parsed_email_data.get("content_html", "")
                    
                    if content_for_agent:
                        ai_tag = await categorization_agent.categorize_email(
                            from_address=parsed_email_data["from_address"],
                            subject=parsed_email_data.get("subject", ""),
                            content=content_for_agent,
                            user_instruction=user_category_instruction
                        )
                        if ai_tag:
                            if ai_tag not in parsed_email_data["tags"]:
                                parsed_email_data["tags"].append(ai_tag)
                        else:
                            categorization_failed_count += 1
                    else:
                        print(f"Skipping AI categorization for message {msg_id} due to no content_plain or content_html.")
                        categorization_failed_count += 1
                        
                encrypted_data_for_db = {}
                for key, value in parsed_email_data.items():
                    if key in ["from_address", "from_name", "to_address", "subject", "snippet", "content_html", "content_plain"]:
                        encrypted_data_for_db[key] = encrypt_value(value)
                    else:
                        encrypted_data_for_db[key] = value
                
                mail_to_create = Mail(user_id=user_id, **encrypted_data_for_db)
                db.add(mail_to_create)
                newly_synced_count += 1
                
                if weaviate_client and not is_sent_mail and (parsed_email_data.get("content_plain") is not None or parsed_email_data.get("content_html") is not None):
                    
                    content_plain_value = parsed_email_data.get("content_plain")
                    content_html_value = parsed_email_data.get("content_html")
                    body_for_vectorization = ""
                    if content_plain_value is not None:
                        body_for_vectorization = content_plain_value.strip()
                    if not body_for_vectorization and content_html_value is not None:
                        stripped_html = re.sub('<[^<]+?>', '', content_html_value)
                        body_for_vectorization = stripped_html.strip()

                    if body_for_vectorization:
                        properties_for_weaviate = {
                            "appUserId": str(user_id),
                            "messageId": parsed_email_data["gmail_message_id"],
                            "sourceType": "email_received",
                            "fromAddress": parsed_email_data.get('from_address', ''),
                            "fromName": parsed_email_data.get('from_name', ''),
                            "toAddress": parsed_email_data.get('to_address', ''), 
                            "subject": parsed_email_data.get('subject', ''),
                            "bodyPlainText": body_for_vectorization,
                            "tags": parsed_email_data.get("tags", []),
                            "messageTimestampISO": parsed_email_data['message_timestamp'].astimezone(timezone.utc).isoformat()
                        }
                        
                        weaviate_batch_data.append({"properties": properties_for_weaviate, "uuid": None})
                    else:
                        print(f"Skipping Weaviate ingestion for message {msg_id} as no usable body content was found after processing None values.")

        except HttpError as e:
            print(f"Gmail API error fetching message {msg_id}: {e}")
            api_error_count += 1
            if e.resp.status == 401:
                db.rollback() # Rollback before raising to avoid partial commit issues
                raise HTTPException(status_code=401, detail="Gmail API authentication failed during sync. Please login again.")
        except IntegrityError:
            db.rollback()
            print(f"IntegrityError for message {msg_id}, likely already processed or unique constraint violated. Skipping.")
        except Exception as e:
            print(f"Unexpected error processing message {msg_id}: {e}")
            failed_parsing_count += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to commit synced emails to DB: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving emails to database: {e}")

    if weaviate_client and weaviate_batch_data:
        try:
            email_collection = weaviate_client.collections.get(WEAVIATE_CLASS_NAME)
            with email_collection.batch.dynamic() as batch:
                for item_data in weaviate_batch_data:
                     batch.add_object(
                         properties=item_data["properties"], 
                         uuid=item_data["uuid"]
                     )
            print(f"Successfully batched {len(weaviate_batch_data)} objects to Weaviate.")
            weaviate_added_count = len(weaviate_batch_data)
        except Exception as e_weaviate:
            print(f"Error batch inserting objects to Weaviate: {e_weaviate}")
            weaviate_failed_count = len(weaviate_batch_data)
    
    return {
        "newly_synced": newly_synced_count,
        "updated_in_db": updated_count,
        "failed_to_parse": failed_parsing_count,
        "ai_categorization_failed": categorization_failed_count,
        "gmail_api_errors_during_fetch": api_error_count,
        "memories_added": weaviate_added_count,
        "memories_failed": weaviate_failed_count,
        "total_message_ids_considered": len(limited_message_ids)
    }