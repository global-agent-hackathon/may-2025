from typing import List, Dict, AsyncGenerator
from agno.models.azure import AzureOpenAI
from app.repositories.physics_tutor_repository import PhysicsTutorRepository
from agno.agent import Agent
from agno.team import Team
from rich.console import Console
from agno.utils.log import logger
import asyncio
import json
from app.core.config import settings
import warnings

warnings.filterwarnings("ignore", category=ResourceWarning)


class PhysicsTutorService:
    """
    Service for physics tutoring using AI agents for validation, explanations, problem solving, and visualizations.
    """

    def __init__(self, client: AzureOpenAI, repository: PhysicsTutorRepository) -> None:
        """
        Initialize the PhysicsTutorService.

        Args:
            client (AzureOpenAI): The OpenAI client for communication.
            repository (PhysicsTutorRepository): The physics knowledge repository.
        """
        self.client = client
        self.repository = repository
        self.console = Console()

        # Initialize domain validator agent
        self.domain_validator = Agent(
            model=self.client,
            name="Domain Validator",
            instructions=[
                "You are a physics domain validator.",
                "Your role is to determine if a question could be answered using physics knowledge.",
                "Consider questions about:",
                "- Classical mechanics and motion",
                "- Forces and energy",
                "- Thermodynamics and heat",
                "- Waves and oscillations",
                "- Electricity and magnetism",
                "- Optics and light",
                "- Modern physics and quantum mechanics",
                "- Relativity and spacetime",
                "- Fluid dynamics and pressure",
                "- Astrophysics and cosmology",
                "Be inclusive in your validation - if a question could be answered using physics concepts, consider it valid.",
                "Return 'VALID' for questions that could be answered using physics knowledge.",
                "Return 'INVALID: [reason]' only for questions completely unrelated to physics.",
                "Log your reasoning for the validation decision.",
            ],
            knowledge=self.repository.physics_knowledge,
            add_history_to_messages=True,
            markdown=True,
            debug_mode=True,
        )

        # Initialize specialized agents with optimized settings
        self.concept_explainer = Agent(
            model=self.client,
            name="Concept Explainer",
            instructions=[
                "You are an expert physics tutor specializing in explaining complex concepts clearly.",
                "For physics questions:",
                "- Break down physics concepts into understandable parts",
                "- Use analogies and real-world examples when appropriate",
                "- Include mathematical equations when necessary, but explain them clearly",
                "- Always maintain scientific accuracy",
                "- Format your response in markdown with clear sections",
                "- Keep responses concise and focused",
                "Topics you can help with:",
                "- Classical mechanics and motion",
                "- Forces and energy",
                "- Thermodynamics and heat",
                "- Waves and oscillations",
                "- Electricity and magnetism",
                "- Optics and light",
                "- Modern physics and quantum mechanics",
                "- Relativity and spacetime",
                "- Fluid dynamics and pressure",
                "- Astrophysics and cosmology",
                "If you're unsure about a concept, acknowledge it and suggest related topics you can explain.",
                "Always provide helpful and educational responses.",
            ],
            knowledge=self.repository.physics_knowledge,
            add_history_to_messages=True,
            add_datetime_to_instructions=True,
            markdown=True,
            debug_mode=True,
        )

        self.problem_solver = Agent(
            model=self.client,
            name="Problem Solver",
            instructions=[
                "You are an expert in solving physics problems.",
                "Only proceed if the question is physics-related.",
                "Show step-by-step solutions with clear explanations.",
                "Include units and significant figures in calculations.",
                "Highlight key concepts and formulas used.",
                "Provide alternative approaches when possible.",
                "Format your response in markdown with clear sections.",
                "Keep examples concise and focused.",
            ],
            knowledge=self.repository.physics_knowledge,
            add_history_to_messages=True,
            markdown=True,
            debug_mode=False,
        )

        self.visualizer = Agent(
            model=self.client,
            name="Visualizer",
            instructions=[
                "You are an expert in creating physics diagrams and visualizations.",
                "Only create visualizations for physics-related concepts.",
                "Describe diagrams that would help explain the physics concept.",
                "Include labels, forces, and important measurements.",
                "Use standard physics notation and conventions.",
                "Format your response in markdown with clear sections.",
                "Keep visual descriptions concise and clear.",
            ],
            knowledge=self.repository.physics_knowledge,
            add_history_to_messages=True,
            markdown=True,
            debug_mode=False,
        )

        # Collaborative agent team
        self.team: Team = Team(
            name="Physics Education Team",
            description="A team of specialized agents for physics education",
            model=self.client,
            members=[
                self.domain_validator,
                self.concept_explainer,
                self.problem_solver,
                self.visualizer,
            ],
        )

    async def validate_physics_question(self, query: str) -> bool:
        """
        Check if a user's question is suitable for physics.

        Args:
            query (str): The user's question.

        Returns:
            bool: True if valid for physics, False otherwise.
        """
        try:
            logger.info(f"Starting physics validation for query: {query}")
            query_lower = query.lower()
            chemistry_keywords = [
                "chemical bond",
                "molecule",
                "reaction",
                "ph",
                "acid",
                "base",
            ]
            if any(keyword in query_lower for keyword in chemistry_keywords):
                logger.info("Detected chemistry-related query, rejecting.")
                return False
            validation_prompt = (
                f"Strictly validate if this is a physics question: {query}"
            )
            validation = await asyncio.to_thread(
                self.domain_validator.run, validation_prompt
            )
            is_valid = (
                "VALID" in validation.content.upper()
                and "INVALID" not in validation.content.upper()
            )
            return is_valid
        except Exception as e:
            logger.error(f"Error in validate_physics_question: {str(e)}")
            return False

    async def search_physics_concept(self, query: str) -> List[Dict[str, str]]:
        """
        Search the physics knowledge base for related concepts.

        Args:
            query (str): The search query.

        Returns:
            List[Dict[str, str]]: List of concept summaries.
        """
        try:
            results = await asyncio.to_thread(self.repository.search_knowledge, query)
            if not results:
                explanation = await asyncio.to_thread(self.concept_explainer.run, query)
                return [{"id": "1", "content": explanation.content, "type": "concept"}]
            return [
                {"id": str(i + 1), "content": result, "type": "concept"}
                for i, result in enumerate(results)
            ]
        except Exception as e:
            logger.error(f"Error in search_physics_concept: {str(e)}")
            return []

    async def stream_explanation(self, query: str) -> AsyncGenerator[str, None]:
        """
        Stream a step-by-step explanation of a physics concept.

        Args:
            query (str): The user's physics question.

        Yields:
            AsyncGenerator[str, None]: JSON-formatted explanation content.
        """
        try:
            yield (
                json.dumps({"type": "status", "content": "Validating question..."})
                + "\n"
            )
            is_physics = await self.validate_physics_question(query)
            if not is_physics:
                yield (
                    json.dumps(
                        {"type": "error", "content": "Invalid question for physics."}
                    )
                    + "\n"
                )
                return

            yield (
                json.dumps(
                    {"type": "status", "content": "Generating concept explanation..."}
                )
                + "\n"
            )
            explanation = await asyncio.to_thread(self.concept_explainer.run, query)
            yield (
                json.dumps({"type": "explanation", "content": explanation.content})
                + "\n"
            )

            yield (
                json.dumps(
                    {"type": "status", "content": "Generating example problems..."}
                )
                + "\n"
            )
            problems = await asyncio.to_thread(
                self.problem_solver.run,
                f"Generate example problems based on: {explanation.content}",
            )
            yield json.dumps({"type": "problems", "content": problems.content}) + "\n"

            yield (
                json.dumps({"type": "status", "content": "Generating visual aids..."})
                + "\n"
            )
            visuals = await asyncio.to_thread(
                self.visualizer.run, f"Create diagrams based on: {explanation.content}"
            )
            yield json.dumps({"type": "visuals", "content": visuals.content}) + "\n"

        except Exception as e:
            logger.error(f"Error in stream_explanation: {str(e)}")
            yield json.dumps({"type": "error", "content": str(e)}) + "\n"

    async def get_concept_explanation(self, query: str) -> Dict[str, str]:
        """
        Get a full explanation, problems, and visuals for a physics concept.

        Args:
            query (str): The user's question.

        Returns:
            Dict[str, str]: Explanation, problems, and visual aids.
        """
        try:
            is_physics = await self.validate_physics_question(query)
            if not is_physics:
                return {
                    "content": "Sorry, I can only help with physics-related questions.",
                    "problems": "",
                    "visuals": "",
                    "type": "error",
                }

            explanation_task = asyncio.to_thread(self.concept_explainer.run, query)
            problems_task = asyncio.to_thread(
                self.problem_solver.run, f"Create problems based on: {query}"
            )
            visuals_task = asyncio.to_thread(
                self.visualizer.run, f"Create visuals for: {query}"
            )
            explanation, problems, visuals = await asyncio.gather(
                explanation_task, problems_task, visuals_task
            )

            return {
                "content": explanation.content,
                "problems": problems.content,
                "visuals": visuals.content,
                "type": "explanation",
            }
        except Exception as e:
            logger.error(f"Error getting concept explanation: {str(e)}")
            return {
                "content": "Sorry, there was an error processing your query.",
                "problems": "",
                "visuals": "",
                "type": "error",
            }
