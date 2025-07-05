from fastapi import FastAPI, Form
from twilio.rest import Client
import os
from youtube_agent_team import youtube_team
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Twilio credentials from environment variables
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(ACCOUNT_SID, AUTH_TOKEN)


@app.post("/whatsapp")
async def whatsapp_reply(Body: str = Form(...), From: str = Form(...)):
    """
    This is your WhatsApp webhook for Twilio.
    """
    print(f"Incoming message from {From}: {Body}")
    try:
        response = youtube_team.run(Body)
        reply_text = response.content

        # Send response back to user via Twilio
        message = client.messages.create(
            body=reply_text,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=From
        )
        return {"status": "sent", "sid": message.sid}
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        client.messages.create(
            body=error_msg,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=From
        )
        return {"status": "error", "detail": error_msg}