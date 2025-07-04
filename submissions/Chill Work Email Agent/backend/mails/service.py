from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import datetime, timezone
import uuid

from database.models import Mail, MailTagValue, MailRead
from .constants import DB_TAG_MAP
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from core.config import settings
from .schemas import SendMailRequest
from core.utils import decrypt_value, encrypt_value
from core.weaviate_client import get_weaviate_client, WEAVIATE_CLASS_NAME

def ingest_sent_mail_to_graphlit_task(
    user_id_str: str,
    app_message_id: str,
    to_address: str,
    from_address_actual: str,
    from_name_actual: Optional[str],
    subject: str,
    content_plain: str,
    content_html: Optional[str],
    message_timestamp_iso: str
):
    """
    Prepares and ingests sent mail content to Graphlit as a background task.
    """
    weaviate_client = get_weaviate_client()
    if not weaviate_client:
        print(f"Background task: Weaviate client not available. Skipping ingestion for app_message_id: {app_message_id}")
        return

    print(f"Background task: Starting Weaviate ingestion for app_message_id: {app_message_id}, user: {user_id_str}")

    body_for_vectorization = content_plain.strip()
    if not body_for_vectorization and content_html:
        import re
        body_for_vectorization = re.sub('<[^<]+?>', '', content_html).strip()

    properties_for_weaviate = {
        "appUserId": user_id_str,
        "messageId": app_message_id,
        "sourceType": "email_sent_by_app",
        "fromAddress": from_address_actual,
        "fromName": from_name_actual or "",
        "toAddress": to_address,
        "subject": subject,
        "bodyPlainText": body_for_vectorization,
        "tags": [MailTagValue.SENT.value],
        "messageTimestampISO": message_timestamp_iso
    }

    try:
        email_collection = weaviate_client.collections.get(WEAVIATE_CLASS_NAME)
        result_uuid = email_collection.data.insert(properties=properties_for_weaviate)

        print(f"Background task: Successfully ingested app-sent email {app_message_id} to Weaviate. Object UUID: {result_uuid}")
    except Exception as e:
        print(f"Background task: Failed to ingest app-sent email {app_message_id} to Weaviate: {e}")

def get_mails_by_category_logic(
    user_id: int, 
    category: MailTagValue, 
    db: Session, 
    skip: int, 
    limit: int
) -> List[MailRead]:
    db_tag_to_query = DB_TAG_MAP.get(category)
    
    if not db_tag_to_query:
        raise HTTPException(status_code=400, detail=f"Invalid mail category mapping for: {category.value}")

    statement = (
        select(Mail)
        .where(Mail.user_id == user_id, Mail.tags.contains([db_tag_to_query]))
        .order_by(Mail.message_timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    
    mails_db = db.exec(statement).all()
    
    decrypted_mails: List[MailRead] = []
    for mail_db_instance in mails_db:
        mail_read_data = mail_db_instance.model_dump(exclude={"user"})
        mail_read_data["from_address"] = decrypt_value(mail_db_instance.from_address)
        mail_read_data["from_name"] = decrypt_value(mail_db_instance.from_name)
        mail_read_data["to_address"] = decrypt_value(mail_db_instance.to_address)
        mail_read_data["subject"] = decrypt_value(mail_db_instance.subject)
        mail_read_data["snippet"] = decrypt_value(mail_db_instance.snippet)
        mail_read_data["content_html"] = decrypt_value(mail_db_instance.content_html)
        mail_read_data["content_plain"] = decrypt_value(mail_db_instance.content_plain)
        try:
            decrypted_mail_read_obj = MailRead.model_validate(mail_read_data)
            decrypted_mails.append(decrypted_mail_read_obj)
        except Exception as e:
            print(f"Error validating MailRead for mail ID {mail_db_instance.id} after decryption: {e}")
            decrypted_mails.append(MailRead(**mail_read_data))
    
    return decrypted_mails

def send_email_via_mailtrap(
    db: Session,
    user_id: int,
    actual_user_email: str,
    actual_user_name: Optional[str],
    mail_data: SendMailRequest
) -> Mail:
    """
    Sends an email using Mailtrap SMTP and saves it to the database.
    """
    if actual_user_name:
        display_from_name = f"{actual_user_name} (via Email Agent App)"
        from_header_display = formataddr((str(Header(display_from_name, 'utf-8')), settings.MAIL_FROM_ADDRESS))
    else:
        from_header_display = settings.MAIL_FROM_ADDRESS

    if mail_data.content_html:
        msg = MIMEMultipart('alternative')
        msg.attach(MIMEText(mail_data.content_plain, 'plain', 'utf-8'))
        msg.attach(MIMEText(mail_data.content_html, 'html', 'utf-8'))
    else:
        msg = MIMEText(mail_data.content_plain, 'plain', 'utf-8')

    msg['Subject'] = Header(mail_data.subject, 'utf-8')
    msg['From'] = from_header_display
    msg['To'] = mail_data.to_address

    try:
        with smtplib.SMTP(settings.MAILTRAP_SMTP_HOST, settings.MAILTRAP_SMTP_PORT) as server:
            server.ehlo()
            if settings.MAILTRAP_SMTP_PORT in [587, 2525]:
                server.starttls()
                server.ehlo()
            server.login(settings.MAILTRAP_SMTP_USERNAME, settings.MAILTRAP_SMTP_PASSWORD)
            server.sendmail(settings.MAIL_FROM_ADDRESS, [mail_data.to_address], msg.as_string())
        print(f"Email sent successfully to {mail_data.to_address} via Mailtrap.")

        generated_message_id = f"app_sent_{uuid.uuid4()}"
        snippet = (mail_data.content_plain[:100] + '...') if len(mail_data.content_plain) > 100 else mail_data.content_plain

        mail_to_save = Mail(
            user_id=user_id,
            gmail_message_id=generated_message_id,
            from_address=encrypt_value(actual_user_email),
            from_name=encrypt_value(actual_user_name),
            to_address=encrypt_value(mail_data.to_address),
            to_name=None,
            message_timestamp=datetime.now(timezone.utc),
            subject=encrypt_value(mail_data.subject),
            snippet=encrypt_value(snippet),
            content_html=encrypt_value(mail_data.content_html),
            content_plain=encrypt_value(mail_data.content_plain),
            tags=[MailTagValue.SENT.value]
        )
        
        db.add(mail_to_save)
        db.commit()
        db.refresh(mail_to_save)
        print(f"Sent email (ID: {mail_to_save.id}, AppMsgID: {generated_message_id}) saved to DB for user {user_id}.")
        return mail_to_save

    except smtplib.SMTPException as e:
        db.rollback()
        print(f"SMTP Error sending email: {e}")
        raise Exception(f"Failed to send email via Mailtrap: {e}")
    except Exception as e:
        db.rollback()
        print(f"An unexpected error occurred during email sending or DB save: {e}")
        raise Exception(f"Unexpected error sending email: {e}")

def send_email_via_mailtrap_sync_part(
    db: Session,
    user_id: int,
    actual_user_email: str,
    actual_user_name: Optional[str],
    mail_data: SendMailRequest
) -> Mail:
    """
    Synchronous part of sending an email via Mailtrap and saving to the database.
    """
    return send_email_via_mailtrap(db, user_id, actual_user_email, actual_user_name, mail_data)