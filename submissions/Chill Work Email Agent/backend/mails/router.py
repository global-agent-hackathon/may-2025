from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from datetime import timezone
from database.session import Session
from core.dependencies import get_db_session, get_current_user_session
from database.models import MailRead, MailTagValue, Mail
from . import service as mails_service
from .schemas import SendMailRequest

router = APIRouter(prefix="/api/mails", tags=["mails"])

@router.post("/send", response_model=MailRead, status_code=status.HTTP_201_CREATED)
async def send_mail_endpoint(
    mail_request: SendMailRequest,
    background_tasks: BackgroundTasks,
    session_data: dict = Depends(get_current_user_session),
    db: Session = Depends(get_db_session)
):
    user_info = session_data.get("user_info")
    user_id_int = session_data.get("user_id")

    if not user_id_int or not user_info or not user_info.get("email"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User email or ID not found in session. Cannot send mail."
        )

    actual_user_email = user_info["email"]
    actual_user_name = user_info.get("name")

    saved_mail_db_object: Optional[Mail] = None

    try:
        saved_mail_db_object = mails_service.send_email_via_mailtrap_sync_part(
            db=db,
            user_id=user_id_int,
            actual_user_email=actual_user_email,
            actual_user_name=actual_user_name,
            mail_data=mail_request
        )
        
        if not saved_mail_db_object:
            raise HTTPException(status_code=500, detail="Failed to send email or save to DB.")

        background_tasks.add_task(
            mails_service.ingest_sent_mail_to_graphlit_task,
            user_id_str=str(user_id_int),
            app_message_id=saved_mail_db_object.gmail_message_id,
            to_address=mail_request.to_address,
            from_address_actual=actual_user_email,
            from_name_actual=actual_user_name,
            subject=mail_request.subject,
            content_plain=mail_request.content_plain,
            content_html=mail_request.content_html,
            message_timestamp_iso=saved_mail_db_object.message_timestamp.astimezone(timezone.utc).isoformat()
        )
        
        from core.utils import decrypt_value
        decrypted_response_data = saved_mail_db_object.model_dump()
        decrypted_response_data["from_address"] = decrypt_value(saved_mail_db_object.from_address)
        decrypted_response_data["from_name"] = decrypt_value(saved_mail_db_object.from_name)
        decrypted_response_data["subject"] = decrypt_value(saved_mail_db_object.subject)
        decrypted_response_data["snippet"] = decrypt_value(saved_mail_db_object.snippet)
        decrypted_response_data["content_html"] = decrypt_value(saved_mail_db_object.content_html)
        decrypted_response_data["content_plain"] = decrypt_value(saved_mail_db_object.content_plain)

        return MailRead(**decrypted_response_data)

    except Exception as e:
        print(f"Error in send_mail_endpoint: {e}")
        if "Failed to send email via Mailtrap" in str(e):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/{category}", response_model=List[MailRead])
async def get_mails_by_category_endpoint(
    category: MailTagValue,
    session_data: dict = Depends(get_current_user_session),
    db: Session = Depends(get_db_session),
    skip: int = 0,
    limit: int = 50
):
    user_id = session_data["user_id"]
    
    try:
        mails = mails_service.get_mails_by_category_logic(
            user_id=user_id,
            category=category,
            db=db,
            skip=skip,
            limit=limit
        )
        return mails
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error in get_mails_by_category_endpoint: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching mails.")