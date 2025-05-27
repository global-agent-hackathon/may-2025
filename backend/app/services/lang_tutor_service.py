from typing import Dict, AsyncGenerator
from app.repositories.lang_tutor_repository import LanguageTutorRepository
from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.utils.log import logger
import asyncio
import json


class LanguageTutorService:
    """
    Service for language learning assistance using multiple AI agents.

    This service validates language-related queries, explains grammar concepts,
    generates vocabulary lists, shares cultural insights, and creates dialogues for practice.
    """

    client: AzureOpenAI
    language_code: str
    repository: LanguageTutorRepository
    knowledge_base: any  

    domain_validator: Agent
    grammar_coach: Agent
    vocab_builder: Agent
    culture_expert: Agent
    dialogue_partner: Agent

    def __init__(self, client: AzureOpenAI, language_code: str = "fr") -> None:
        """
        Initialize the LanguageTutorService with AI agents and resources.

        Args:
            client (AzureOpenAI): The Azure OpenAI client for LLM tasks.
            language_code (str): Target language code (e.g., 'fr' for French). Default is 'fr'.
        """
        self.language_code = language_code
        self.client = client
        self.repository = LanguageTutorRepository(language_code=language_code)
        self.knowledge_base = self.repository.vector_db

        shared_tools = [
            DuckDuckGoTools(),
            ReasoningTools(add_instructions=True),
        ]

        self.domain_validator = Agent(
            model=self.client,
            name="Language Domain Validator",
            tools=shared_tools,
            add_history_to_messages=True,
            instructions=[
                "You are a domain validator for language learning topics.",
                "Accept queries about grammar, vocabulary, speaking, pronunciation, translation, or culture.",
                "Reject topics about math, science, physics, chemistry, programming or any other topic thats not language related.",
                "Be striict that the topic is only language",
                "Respond ONLY with 'VALID' or 'INVALID: [reason]'.",
            ],
            markdown=True,
        )

        self.grammar_coach = Agent(
            model=self.client,
            name="Grammar Coach",
            tools=shared_tools,
            add_history_to_messages=True,
            instructions=[
                f"You are a professional grammar coach specializing in {self.language_code}.",
                f"Given a topic, identify grammar structures relevant to {self.language_code}.",
                "For each important structure:",
                "- Explain the rule clearly in **simple English**.",
                f"- Provide at least **one example sentence in {self.language_code}**.",
                "- Then provide the **English translation** under it.",
                "- Highlight key grammar points (gender, verb tense, word order, etc.).",
                "",
                "Format your answer using markdown:",
                "- **Grammar Rule**",
                f"- **Example in {self.language_code}**",
                "- **English Translation**",
                "- **Notes**",
                "",
                "Your explanations must be beginner-friendly, using plain language without jargon.",
            ],
            markdown=True,
        )

        self.vocab_builder = Agent(
            model=self.client,
            name="Vocabulary Builder",
            tools=shared_tools,
            add_history_to_messages=True,
            instructions=[
                f"You are a vocabulary coach helping students learn {self.language_code}.",
                "When given a topic, do the following:",
                "",
                "1. Create a list of 8–12 themed vocabulary words related to the topic.",
                "2. For each word:",
                f"- Give the word in {self.language_code}",
                "- Provide the English translation",
                f"- Provide an example sentence using the word in {self.language_code}",
                "- Provide the English translation of the sentence",
                "3. Format everything clearly using markdown (headers, bullet points, bold titles if needed).",
                "",
                "4. After the vocabulary list, suggest helpful resources for practicing the topic:",
                "- These can be YouTube videos, websites, blog posts, or articles.",
                f"- Prefer resources in {self.language_code} when possible.",
                "- Always use proper clickable markdown links: [Title](URL).",
                "- Recommend at least 2–3 resources.",
                "",
                "If no good resources are found, say: 'Currently no good videos available, but you can practice using the examples above!'",
            ],
            markdown=True,
        )

        self.culture_expert = Agent(
            model=self.client,
            name="Culture Expert",
            tools=shared_tools,
            add_history_to_messages=True,
            instructions=[
                f"You are a cultural and communication expert specializing in {self.language_code}.",
                f"You help learners understand important cultural aspects like idioms, greetings, politeness rules, gestures, and expressions used in the {self.language_code} language.",
                "When given a topic, you should:",
                f"- Provide 3–5 real expressions, idioms, or greetings in {self.language_code}",
                "- For each, include:",
                f"  - The phrase in {self.language_code}",
                "  - Its English translation",
                "  - A short explanation of when and how it is used",
                "  - Mention if it is formal or informal",
                "Use clear markdown formatting with headers like **Phrase**, **Translation**, **Usage**, **Formality**.",
                "Avoid giving only English examples. Always start from the native language perspective.",
            ],
            markdown=True,
        )

        self.dialogue_partner = Agent(
            model=self.client,
            name="Dialogue Partner",
            tools=shared_tools,
            add_history_to_messages=True,
            instructions=[
                f"You are a conversation tutor helping students learn {self.language_code}.",
                f"All dialogue lines MUST be in {self.language_code} (not English), except for the English translation in parentheses below each line.",
                "Create realistic, everyday dialogues based on the given topic.",
                "The dialogue should be between two people: A and B.",
                "Each speaker turn should include:",
                f"- One sentence in {self.language_code} (not English)",
                "- Directly below it, the English translation in parentheses.",
                "Make the conversation 8–12 turns long (4–6 per speaker).",
                "Use simple, natural language that beginners can understand.",
                "Focus on practical real-world usage related to the topic.",
                "Use clear markdown formatting with **bold speaker names**.",
                "NEVER ask the user questions, just generate the full dialogue.",
                "Keep the tone polite but friendly, suitable for learners.",
                f"Do NOT use English for the main dialogue lines. Only use {self.language_code} for the dialogue, and English only for the translation in parentheses.",
                f"If you cannot generate a line in {self.language_code}, skip that turn.",
            ],
            markdown=True,
        )

    async def validate_language_question(self, query: str) -> bool:
        """
        Validate whether the user's query is related to language learning.

        Args:
            query (str): The user's input query.

        Returns:
            bool: True if the query is language-related, False otherwise.
        """
        try:
            logger.info(f"🔵 Validating question: {query}")
            validation_prompt = f"Strictly validate if this is a language learning question: {query}"
            validation = await asyncio.to_thread(self.domain_validator.run, validation_prompt)

            clean_content = validation.content.strip().replace("*", "").upper()
            is_valid = clean_content.startswith("VALID")

            logger.info(f"✅ Validation result (cleaned): {clean_content}")
            return is_valid
        except Exception as e:
            logger.error(f"❌ Error during validation: {str(e)}")
            return False

    async def get_tutoring_session_intro(self, topic: str) -> AsyncGenerator[str, None]:
        """
        Stream the initial language tutoring session with grammar, vocabulary, and cultural tips.

        Args:
            topic (str): The language learning topic requested by the user.

        Yields:
            AsyncGenerator[str, None]: Streaming JSON-formatted events with session updates.
        """
        try:
            logger.info(f"🔵 Starting tutoring session for topic: {topic}")
            yield json.dumps({"type": "status", "content": "Validating question..."}) + "\n"

            is_language = await self.validate_language_question(topic)

            if not is_language:
                logger.warning("❌ Invalid topic detected.")
                yield json.dumps({
                    "type": "error",
                    "content": "Only language learning topics are supported."
                }) + "\n"
                return

            logger.info("📝 Starting Grammar Coach...")
            yield json.dumps({"type": "status", "content": "Generating grammar explanation..."}) + "\n"
            grammar = await asyncio.to_thread(self.grammar_coach.run, topic)
            yield json.dumps({"type": "grammar", "content": grammar.content}) + "\n"

            logger.info("🧠 Starting Vocabulary Builder...")
            yield json.dumps({"type": "status", "content": "Building vocabulary list..."}) + "\n"
            vocab = await asyncio.to_thread(self.vocab_builder.run, topic)
            yield json.dumps({"type": "vocabulary", "content": vocab.content}) + "\n"

            logger.info("🌍 Starting Culture Expert...")
            yield json.dumps({"type": "status", "content": "Adding cultural tips..."}) + "\n"
            culture = await asyncio.to_thread(self.culture_expert.run, topic)
            yield json.dumps({"type": "culture", "content": culture.content}) + "\n"
            logger.info("✅ Culture section completed.")

        except Exception as e:
            logger.error(f"❌ Error during tutoring session: {str(e)}")
            yield json.dumps({
                "type": "error",
                "content": "Sorry, an error occurred during the session."
            }) + "\n"

    async def create_dialogue(self, topic: str) -> Dict[str, str]:
        """
        Generate a language learning dialogue for the user on a given topic.

        Args:
            topic (str): The conversation topic for the dialogue.

        Returns:
            Dict[str, str]: A dictionary with the dialogue content or an error message.
        """
        try:
            logger.info(f"🗣️ Creating dialogue for topic: {topic}")
            dialogue = await asyncio.to_thread(
                self.dialogue_partner.run, f"Create a conversation about: {topic}"
            )
            logger.info("✅ Dialogue created successfully.")
            return {
                "type": "dialogue",
                "content": dialogue.content,
            }
        except Exception as e:
            logger.error(f"❌ Error creating dialogue: {str(e)}")
            return {
                "type": "error",
                "content": "Sorry, I couldn't create the conversation.",
            }
