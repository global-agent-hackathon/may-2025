import re
import base64
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from database.models import MailBase, MailCreate
from mails.constants import INTERNAL_ARCHIVE_TAG

def build_gmail_service(access_token: str) -> Optional[Any]:
    """Builds and returns a Gmail API service object."""
    try:
        creds = Credentials(token=access_token)
        service = build("gmail", "v1", credentials=creds)
        return service
    except Exception as e:
        print(f"Failed to build Gmail service: {e}")
        return None

def parse_from_header(header_value: str) -> tuple[Optional[str], str]:
    """Parses a 'From' header into name and email parts."""
    match = re.match(r'^(.*?)<([^>]+)>$', header_value)
    if match:
        name = match.group(1).strip().replace('"', '')
        email = match.group(2).strip()
        return name if name else None, email
    if '@' in header_value:
        return None, header_value.strip()
    return header_value.strip() if header_value.strip() else None, "unknown@example.com"

def _get_decoded_body_data(part_body: Dict[str, Any]) -> Optional[str]:
    """Decodes base64 email body data."""
    body_data = part_body.get("data")
    if body_data:
        try:
            return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="replace")
        except Exception as e:
            print(f"Error decoding base64 body data: {e}")
            return None
    return None

def _extract_content_from_parts(parts: List[Dict[str, Any]]) -> tuple[str, str]:
    """Recursively extracts plain and HTML content from email parts."""
    plain_content_list = []
    html_content_list = []
    
    for part in parts:
        mime_type = part.get("mimeType", "").lower()
        
        if "parts" in part and part.get("parts"):
            nested_plain, nested_html = _extract_content_from_parts(part["parts"])
            if nested_plain:
                plain_content_list.append(nested_plain)
            if nested_html:
                html_content_list.append(nested_html)
        else:
            decoded_data = _get_decoded_body_data(part.get("body", {}))
            if decoded_data:
                if mime_type == "text/plain":
                    plain_content_list.append(decoded_data)
                elif mime_type == "text/html":
                    html_content_list.append(decoded_data)

    return "\n".join(plain_content_list).strip(), "\n".join(html_content_list).strip()

def parse_gmail_message_full(message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parses a full Gmail message resource into a dictionary for DB storage."""
    parsed_data: Dict[str, Any] = {}
    
    gmail_id = message_data.get("id")
    if not gmail_id:
        print("Warning: Message data missing 'id'. Skipping.")
        return None
    parsed_data["gmail_message_id"] = gmail_id
    
    parsed_data["snippet"] = message_data.get("snippet")

    payload = message_data.get("payload", {})
    headers = payload.get("headers", [])
    
    from_address_found = False
    to_address_found = False
    for header in headers:
        name = header.get("name", "").lower()
        value = header.get("value", "")
        if name == "from":
            name_val, email_val = parse_from_header(value)
            parsed_data["from_name"] = name_val
            parsed_data["from_address"] = email_val
            from_address_found = True
        elif name == "to":
            name_val, email_val = parse_from_header(value)
            parsed_data["to_name"] = name_val
            parsed_data["to_address"] = email_val
            to_address_found = True
        elif name == "subject":
            parsed_data["subject"] = value
    
    if not from_address_found or not parsed_data.get("from_address") or parsed_data.get("from_address") == "unknown@example.com":
        print(f"Warning: Could not reliably parse 'From' address for message {gmail_id}. Check raw headers if issues persist.")
        parsed_data.setdefault("from_address", "unknown@example.com")
        parsed_data.setdefault("from_name", None)
    
    if not to_address_found or not parsed_data.get("to_address") or parsed_data.get("to_address") == "unknown@example.com":
        parsed_data.setdefault("to_address", "unknown@example.com")
        parsed_data.setdefault("to_name", None)

    internal_date_ms_str = message_data.get("internalDate")
    if internal_date_ms_str:
        try:
            parsed_data["message_timestamp"] = datetime.fromtimestamp(int(internal_date_ms_str) / 1000.0, tz=timezone.utc)
        except (ValueError, TypeError) as e:
             print(f"Warning: Could not parse internalDate '{internal_date_ms_str}' for message {gmail_id}: {e}. Using current time.")
             parsed_data["message_timestamp"] = datetime.now(timezone.utc)
    else:
        parsed_data["message_timestamp"] = datetime.now(timezone.utc)

    content_plain = ""
    content_html = ""
    mime_type = payload.get("mimeType", "").lower()

    if "parts" in payload and payload.get("parts"):
        content_plain, content_html = _extract_content_from_parts(payload["parts"])
    elif payload.get("body"):
        decoded_data = _get_decoded_body_data(payload.get("body", {}))
        if decoded_data:
            if mime_type == "text/plain":
                content_plain = decoded_data
            elif mime_type == "text/html":
                content_html = decoded_data
            elif not content_plain and not content_html:
                 content_plain = decoded_data

    parsed_data["content_plain"] = content_plain if content_plain else None
    parsed_data["content_html"] = content_html if content_html else None

    gmail_labels = message_data.get("labelIds", [])
    db_tags = list(set(gmail_labels))

    non_archive_labels = {"INBOX", "SENT", "IMPORTANT"}
    is_archived_candidate = not any(lbl in non_archive_labels for lbl in db_tags)
    
    if is_archived_candidate:
        db_tags.append(INTERNAL_ARCHIVE_TAG)
    
    parsed_data["tags"] = list(set(db_tags))

    final_parsed_data = {}
    for field_name in MailBase.model_fields.keys(): # Use MailBase for complete field list
        final_parsed_data[field_name] = parsed_data.get(field_name)
    
    try:
        MailCreate.model_validate(final_parsed_data)
    except Exception as e:
        print(f"Error: Parsed data for message {gmail_id} failed MailCreate validation: {e}")
        print(f"Problematic final_parsed_data: {final_parsed_data}")
        return None

    return final_parsed_data