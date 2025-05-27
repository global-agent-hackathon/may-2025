from typing import List, Dict, AsyncGenerator
from app.repositories.chemistry_tutor_repository import ChemistryTutorRepository
from agno.models.azure import AzureOpenAI
from agno.agent import Agent
from agno.team import Team
from rich.console import Console
from agno.utils.log import logger
import asyncio
import json
import warnings

warnings.filterwarnings("ignore", category=ResourceWarning)


class ChemistryTutorService:
    """
    Service for handling chemistry tutoring functionalities:
    - Domain validation
    - Concept explanations
    - Problem-solving assistance
    - Visual aids generation
    """

    def __init__(self, client: AzureOpenAI, repository: ChemistryTutorRepository) -> None:
        """
        Initialize the ChemistryTutorService with agents for various chemistry tasks.

        Args:
            client (AzureOpenAI): The Azure OpenAI client for LLM interactions.
            repository (ChemistryTutorRepository): The chemistry knowledge repository.
        """
        self.client: AzureOpenAI = client
        self.repository: ChemistryTutorRepository = repository
        self.console: Console = Console()

        # Domain Validator Agent: Checks if a query is chemistry-related
        self.domain_validator: Agent = Agent(
            model=self.client,
            name="Domain Validator",
            instructions=[
                "You are a chemistry domain validator.",
                "Your role is to determine if a question could be answered using chemistry knowledge.",
                "Consider questions about:",
                "- Chemical elements, compounds, and reactions",
                "- Atomic structure and bonding",
                "- States of matter and phase changes",
                "- Acids, bases, and pH",
                "- Organic chemistry and biochemistry",
                "- Thermodynamics and kinetics",
                "- Electrochemistry and redox reactions",
                "- Environmental chemistry",
                "- Chemical safety and laboratory procedures",
                "Be inclusive in your validation - if a question could be answered using chemistry concepts, consider it valid.",
                "Return 'VALID' for questions that could be answered using chemistry knowledge.",
                "Return 'INVALID: [reason]' only for questions completely unrelated to chemistry.",
                "Log your reasoning for the validation decision.",
            ],
            knowledge=self.repository.chemistry_knowledge,
            add_history_to_messages=True,
            markdown=True,
            debug_mode=True,
        )

        # Concept Explainer Agent: Explains chemistry concepts in detail
        self.concept_explainer: Agent = Agent(
            model=self.client,
            name="Concept Explainer",
            instructions=[
                "You are an expert chemistry tutor specializing in explaining complex concepts clearly.",
                "For chemistry questions:",
                "- Break down chemistry concepts into understandable parts",
                "- Use analogies and real-world examples when appropriate",
                "- Include chemical equations and formulas when necessary, but explain them clearly",
                "- Always maintain scientific accuracy",
                "- Format your response in markdown with clear sections",
                "- Keep responses concise and focused",
                "Topics you can help with:",
                "- Chemical elements, compounds, and reactions",
                "- Atomic structure and bonding",
                "- States of matter and phase changes",
                "- Acids, bases, and pH",
                "- Organic chemistry and biochemistry",
                "- Thermodynamics and kinetics",
                "- Electrochemistry and redox reactions",
                "- Environmental chemistry",
                "- Chemical safety and laboratory procedures",
                "If you're unsure about a concept, acknowledge it and suggest related topics you can explain.",
                "Always provide helpful and educational responses.",
            ],
            knowledge=self.repository.chemistry_knowledge,
            add_history_to_messages=True,
            add_datetime_to_instructions=True,
            markdown=True,
            debug_mode=True,
        )

        # Problem Solver Agent: Solves chemistry problems with explanations
        self.problem_solver: Agent = Agent(
            model=self.client,
            name="Problem Solver",
            instructions=[
                "You are an expert in solving chemistry problems.",
                "Only proceed if the question is chemistry-related.",
                "Show step-by-step solutions with clear explanations.",
                "Include units and significant figures in calculations.",
                "Highlight key concepts and formulas used.",
                "Provide alternative approaches when possible.",
                "Format your response in markdown with clear sections.",
                "Keep examples concise and focused.",
            ],
            knowledge=self.repository.chemistry_knowledge,
            add_history_to_messages=True,
            markdown=True,
            debug_mode=False,
        )

        # Visualizer Agent: Creates diagrams and visual aids for chemistry topics
        self.visualizer: Agent = Agent(
            model=self.client,
            name="Visualizer",
            instructions=[
                "You are an expert in creating chemistry diagrams and visualizations.",
                "Only create visualizations for chemistry-related concepts.",
                "Describe molecular structures, reaction mechanisms, and chemical processes.",
                "Include labels, bonds, and important measurements.",
                "Use standard chemistry notation and conventions.",
                "Format your response in markdown with clear sections.",
                "Keep visual descriptions concise and clear.",
            ],
            knowledge=self.repository.chemistry_knowledge,
            add_history_to_messages=True,
            markdown=True,
            debug_mode=False,
        )

        # Team of agents for collaboration
        self.team: Team = Team(
            name="Chemistry Education Team",
            description="A team of specialized agents for chemistry education",
            model=self.client,
            members=[
                self.domain_validator,
                self.concept_explainer,
                self.problem_solver,
                self.visualizer,
            ],
        )

    async def validate_chemistry_question(self, query: str) -> bool:
        """
        Validate if a given query belongs to the chemistry domain.

        Args:
            query (str): The user's question.

        Returns:
            bool: True if the question is chemistry-related, False otherwise.
        """
        try:
            logger.info(f"Starting chemistry validation for query: {query}")
            validation_prompt = f"""
            Strictly validate if this is a chemistry question: {query}

            Rules:
            1. The question should be about chemistry concepts, not physics
            2. Return exactly 'VALID' if it's a chemistry question
            3. Return 'INVALID: [reason]' if it's not a chemistry question
            4. Be strict - if there's any doubt, return INVALID

            Current subject: chemistry
            """
            logger.info("Running domain validator...")
            validation = await asyncio.to_thread(
                self.domain_validator.run, validation_prompt
            )
            logger.info(f"Validation response: {validation.content}")
            is_valid = (
                "VALID" in validation.content.upper()
                and "INVALID" not in validation.content.upper()
            )
            logger.info(f"Final validation result: {is_valid}")
            return is_valid
        except Exception as e:
            logger.error(f"Error in validate_chemistry_question: {str(e)}")
            return False

    async def search_chemistry_concept(self, query: str) -> List[Dict[str, str]]:
        """
        Search for chemistry concepts using the knowledge base and return formatted results.

        Args:
            query (str): The user's search query.

        Returns:
            List[Dict[str, str]]: A list of search results or explanations.
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
            logger.error(f"Error in search_chemistry_concept: {str(e)}")
            return []

    async def stream_explanation(self, query: str) -> AsyncGenerator[str, None]:
        """
        Stream the explanation process with live updates: validation, explanation, problems, and visuals.

        Args:
            query (str): The user's query.

        Yields:
            AsyncGenerator[str, None]: Streaming JSON responses as strings.
        """
        try:
            logger.info("Starting stream explanation with validation...")
            yield json.dumps({"type": "status", "content": "Validating question..."}) + "\n"

            is_chemistry = await self.validate_chemistry_question(query)
            if not is_chemistry:
                error_msg = "This appears to be a invalid question for this subject."
                logger.info(f"Rejecting question with message: {error_msg}")
                yield json.dumps({"type": "error", "content": error_msg}) + "\n"
                return

            logger.info("Validation passed, proceeding with explanation...")
            yield json.dumps({"type": "status", "content": "Generating concept explanation..."}) + "\n"
            explanation = await asyncio.to_thread(self.concept_explainer.run, query)
            yield json.dumps({"type": "explanation", "content": explanation.content}) + "\n"

            logger.info("Starting problem generation...")
            yield json.dumps({"type": "status", "content": "Generating example problems..."}) + "\n"
            problems = await asyncio.to_thread(
                self.problem_solver.run,
                f"Based on this concept: {explanation.content}\nGenerate 1-2 example problems.",
            )
            yield json.dumps({"type": "problems", "content": problems.content}) + "\n"

            logger.info("Starting visual aids generation...")
            yield json.dumps({"type": "status", "content": "Generating visual aids..."}) + "\n"
            visuals = await asyncio.to_thread(
                self.visualizer.run,
                f"Based on this concept: {explanation.content}\nCreate 1-2 visual aids.",
            )
            yield json.dumps({"type": "visuals", "content": visuals.content}) + "\n"

        except Exception as e:
            error_msg = f"Error in stream_explanation: {str(e)}"
            logger.error(error_msg)
            yield json.dumps({"type": "error", "content": error_msg}) + "\n"

    async def get_concept_explanation(self, query: str) -> Dict[str, str]:
        """
        Get a detailed explanation for a chemistry concept, including problems and visuals.

        Args:
            query (str): The user's query.

        Returns:
            Dict[str, str]: A dictionary with content, problems, visuals, and type of response.
        """
        try:
            is_chemistry = await self.validate_chemistry_question(query)
            if not is_chemistry:
                return {
                    "content": "Sorry, I can only help with chemistry-related questions.",
                    "problems": "",
                    "visuals": "",
                    "type": "error",
                }

            explanation_task = asyncio.to_thread(self.concept_explainer.run, query)
            problems_task = asyncio.to_thread(
                self.problem_solver.run,
                f"Based on this concept: {query}\nGenerate 1-2 example problems.",
            )
            visuals_task = asyncio.to_thread(
                self.visualizer.run,
                f"Based on this concept: {query}\nCreate 1-2 visual aids.",
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
