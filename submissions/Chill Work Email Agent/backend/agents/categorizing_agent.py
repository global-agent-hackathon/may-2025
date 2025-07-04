from groq import Groq, GroqError
from core.config import settings
from database.models import MailTagValue

class AgnoCategorizationAgent:
    """
    AgnoCategorizationAgent is a class that uses the Agno Agent with Groq to categorize mails
    """
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = model_name

    async def categorize_email(
        self,
        from_address: str,
        subject: str,
        content: str,
        user_instruction: str
    ) -> str | None:
        """
        Categorizes an email into "Important" or "Archive".

        Args:
            from_address: The sender's email address.
            subject: The email subject.
            content: The plain text or HTML content of the email.
            user_instruction: User's specific instructions for categorization.

        Returns:
            A string "Important", "Archive", or None if categorization fails or is ambiguous.
        """
        system_prompt = (
            "You are an expert email categorization assistant. "
            "Your task is to classify an email as 'Important' or 'Archive' based on its content and user-provided instructions. "
            "If an email needs urgent attention, is from a key contact, or matches criteria for importance specified by the user, mark it as 'Important'. "
            "Otherwise, mark it as 'Archive'. "
            "Respond ONLY with the word 'Important' or 'Archive'. Do not add any other text, explanation, or punctuation."
        )
        max_content_length = 4000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "... (truncated)"

        user_prompt = f"""
        Email From: {from_address}
        Email Subject: {subject}
        Email Content:
        ---
        {content}
        ---
        User Instructions for Categorization: {user_instruction}

        Based on all the information above, classify this email.
        Your response must be exactly 'Important' or 'Archive'.
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=10,
            )
            response_content = chat_completion.choices[0].message.content.strip()
            
            if response_content == MailTagValue.IMPORTANT.value:
                return MailTagValue.IMPORTANT.value
            elif response_content == MailTagValue.ARCHIVE.value:
                return MailTagValue.ARCHIVE.value
            else:
                print(f"Warning: AI returned an unexpected categorization: '{response_content}'")
                return None
        except GroqError as e:
            print(f"Groq API error during categorization: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during categorization: {e}")
            return None