from typing import List, Dict, AsyncGenerator
import json
import asyncio
from agno.agent import Agent
from agno.team import Team
from agno.models.azure import AzureOpenAI
from app.repositories.mathematics_tutor_repository import MathematicsTutorRepository
from agno.utils.log import logger
from rich.console import Console
import warnings

warnings.filterwarnings("ignore", category=ResourceWarning)


class MathematicsTutorService:
    """
    Service class providing mathematics tutoring functionalities.

    Uses multiple agents for validating mathematical queries, explaining concepts,
    and generating practice problems.
    """

    def __init__(self, client: AzureOpenAI, repository: MathematicsTutorRepository) -> None:
        """
        Initialize the MathematicsTutorService.

        Args:
            client (AzureOpenAI): The Azure OpenAI client instance.
            repository (MathematicsTutorRepository): The repository containing mathematics knowledge.
        """
        self.client = client
        self.repository = repository
        self.console = Console()

        self.domain_validator = Agent(
            model=self.client,
            name="Mathematics Domain Validator",
            instructions=[
                "You are a mathematics domain validator.",
                "Your role is to determine if a question belongs to mathematics.",
                "Consider questions about:",
                "- Algebra and arithmetic",
                "- Geometry and trigonometry",
                "- Calculus and analysis",
                "- Statistics and probability",
                "- Number theory",
                "- Linear algebra",
                "Return 'VALID' for mathematics questions.",
                "Return 'INVALID: [reason]' for non-mathematics questions.",
                "Log your reasoning for validation decisions.",
            ],
            knowledge=self.repository.math_knowledge,
            add_history_to_messages=True,
            markdown=True,
            debug_mode=True,
        )

        self.math_teacher = Agent(
            model=self.client,
            name="Mathematics Teacher",
            instructions=[
                "You are an expert mathematics teacher.",
                "Explain concepts clearly with step-by-step solutions.",
                "Use visual explanations when helpful (using ASCII/markdown).",
                "Include relevant formulas and their explanations.",
                "Provide practice problems with solutions.",
                "Use LaTeX notation for mathematical expressions.",
                "Format responses in clear markdown.",
            ],
            knowledge=self.repository.math_knowledge,
            add_history_to_messages=True,
            markdown=True,
            debug_mode=True,
        )

        self.problem_generator = Agent(
            model=self.client,
            name="Mathematics Problem Generator",
            instructions=[
                "Create engaging mathematics problems.",
                "Generate problems of varying difficulty levels.",
                "Include step-by-step solutions.",
                "Use real-world applications when possible.",
                "Format problems and solutions in clear markdown.",
                "Use LaTeX notation for mathematical expressions.",
            ],
            knowledge=self.repository.math_knowledge,
            add_history_to_messages=True,
            markdown=True,
            debug_mode=False,
        )

        self.team = Team(
            name="Mathematics Education Team",
            description="A team of specialized agents for mathematics education",
            model=self.client,
            members=[self.domain_validator, self.math_teacher, self.problem_generator],
        )

    async def validate_mathematics_question(self, query: str) -> bool:
        """
        Validate if the user's query is a mathematics-related question.

        Args:
            query (str): The user's question to validate.

        Returns:
            bool: True if the query is related to mathematics, False otherwise.
        """
        try:
            logger.info(f"Starting mathematics validation for query: {query}")

            science_keywords = [
                "force", "motion", "velocity", "acceleration",
                "chemical", "reaction", "molecule", "atom",
                "electron", "proton", "neutron",
            ]
            query_lower = query.lower()
            for keyword in science_keywords:
                if keyword in query_lower:
                    logger.info(f"Science keyword found: {keyword}")
                    return False

            validation_prompt = f"""
            Strictly validate if this is a mathematics question: {query}

            Rules:
            1. The question should be about mathematical concepts, not physics or chemistry
            2. Return exactly 'VALID' if it's a mathematics question
            3. Return 'INVALID: [reason]' if it's not a mathematics question
            4. Be strict - if there's any doubt, return INVALID

            Current subject: mathematics
            """
            logger.info("Running domain validator...")
            validation = await asyncio.to_thread(self.domain_validator.run, validation_prompt)
            logger.info(f"Validation response: {validation.content}")

            is_valid = "VALID" in validation.content.upper() and "INVALID" not in validation.content.upper()
            logger.info(f"Final validation result: {is_valid}")
            return is_valid

        except Exception as e:
            logger.error(f"Error in validate_mathematics_question: {str(e)}")
            return False

    async def search_mathematics_concept(self, query: str) -> List[Dict[str, str]]:
        """
        Search for mathematics concepts and return formatted results.

        Args:
            query (str): The user's search query.

        Returns:
            List[Dict[str, str]]: A list of search results as dictionaries containing 'id', 'content', and 'type'.
        """
        try:
            results = await asyncio.to_thread(self.repository.search_knowledge, query)
            if not results:
                explanation = await asyncio.to_thread(self.math_teacher.run, query)
                return [{"id": "1", "content": explanation.content, "type": "concept"}]
            return [{"id": str(i + 1), "content": result, "type": "concept"} for i, result in enumerate(results)]
        except Exception as e:
            logger.error(f"Error in search_mathematics_concept: {str(e)}")
            return []

    async def stream_explanation(self, query: str) -> AsyncGenerator[str, None]:
        """
        Stream a full tutoring session for a mathematical concept, including explanations and practice problems.

        Args:
            query (str): The user's question to explain.

        Yields:
            AsyncGenerator[str, None]: JSON-formatted streaming events for frontend consumption.
        """
        try:
            logger.info("Starting stream explanation with validation...")
            yield json.dumps({"type": "status", "content": "Validating question..."}) + "\n"

            is_math = await self.validate_mathematics_question(query)
            logger.info(f"Mathematics validation result: {is_math}")

            if not is_math:
                error_msg = "This appears to be a science question. Please switch to the appropriate subject (physics/chemistry) for questions about scientific concepts."
                logger.info(f"Rejecting question with message: {error_msg}")
                yield json.dumps({"type": "error", "content": error_msg}) + "\n"
                return

            logger.info("Starting mathematical explanation...")
            yield json.dumps({"type": "status", "content": "Generating explanation..."}) + "\n"
            explanation = await asyncio.to_thread(self.math_teacher.run, query)
            logger.info(f"Explanation generated: {explanation.content[:100]}...")
            yield json.dumps({"type": "explanation", "content": explanation.content}) + "\n"

            logger.info("Starting practice problem generation...")
            yield json.dumps({"type": "status", "content": "Creating practice problems..."}) + "\n"
            problems = await asyncio.to_thread(self.problem_generator.run, f"Create practice problems related to: {query}")
            logger.info(f"Practice problems generated: {problems.content[:100]}...")
            yield json.dumps({"type": "practice", "content": problems.content}) + "\n"

        except Exception as e:
            error_msg = f"Error in stream_explanation: {str(e)}"
            logger.error(error_msg)
            yield json.dumps({"type": "error", "content": error_msg}) + "\n"

    async def get_concept_explanation(self, query: str) -> Dict[str, str]:
        """
        Get a structured explanation and practice problems for a mathematical concept.

        Args:
            query (str): The user's question for explanation.

        Returns:
            Dict[str, str]: A dictionary with explanation, problems, and response type.
        """
        try:
            logger.info(f"Getting concept explanation for query: {query}")
            is_math = await self.validate_mathematics_question(query)

            if not is_math:
                logger.info("Query validation failed - not a mathematics question")
                return {
                    "content": "This appears to be a science question. Please switch to the appropriate subject (physics/chemistry) for questions about scientific concepts.",
                    "practice": "",
                    "type": "error",
                }

            logger.info("Starting concurrent agent tasks...")
            explanation_task = asyncio.to_thread(self.math_teacher.run, query)
            problems_task = asyncio.to_thread(self.problem_generator.run, f"Create practice problems for: {query}")

            explanation, problems = await asyncio.gather(explanation_task, problems_task)
            logger.info("All agent tasks completed successfully")

            return {
                "content": explanation.content,
                "practice": problems.content,
                "type": "explanation",
            }
        except Exception as e:
            error_msg = f"Error getting concept explanation: {str(e)}"
            logger.error(error_msg)
            return {
                "content": "Sorry, there was an error processing your query.",
                "practice": "",
                "type": "error",
            }
