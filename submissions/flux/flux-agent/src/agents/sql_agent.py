import os
import json
import asyncio
import threading
import concurrent.futures
from typing import Dict, Any, Optional, List
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.groq import Groq
from agno.tools import tool

from constants.enums import ModelConfig, ErrorMessages, DatabaseConfig, AnalysisType
from core.database import DatabaseService
from services.memory_service import MemoryService
from utils.logger import get_logger

logger = get_logger()


class SQLAgent:
    def __init__(self, database_service: DatabaseService):
        self.database_service = database_service
        self.memory_service = MemoryService()
        
        self.agent = self._create_agent()
        self.final_reply_agent = self._create_final_reply_agent()
        self.batch_analyzer = self._create_batch_analyzer()
        
        # Context tracking
        self._current_form_id: Optional[str] = None
        self._current_form_response_id: Optional[str] = None
        self._current_user_message: Optional[str] = None
        self._current_user_id: Optional[str] = None
        
        # Query tracking
        self._last_executed_query: Optional[str] = None
        self._last_result_rows: List[Dict[str, Any]] = []
        self._return_csv_requested: bool = False
    
    def _create_agent(self) -> Agent:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError(ErrorMessages.MISSING_API_KEY)
        
        return Agent(
            model=OpenAIChat(id=ModelConfig.GPT_4_NANO, api_key=openai_key),
            name="Flux",
            description="Flux is a friendly, conversational assistant that helps users with their form data and general questions.",
            instructions=[
                "You are Flux, a helpful and friendly assistant.",
                "Your main job is to have natural conversations with users and help them when they need it.",
                "",
                "🚨 CRITICAL: NEVER make multiple tool calls at once. Use ONLY ONE tool call per response.",
                "🚨 CRITICAL: Either respond conversationally OR use a tool, never both.",
                "",
                "RESPOND CONVERSATIONALLY (your default mode):",
                "- Greetings: 'hey', 'hello', 'hi' → Be friendly and welcoming",
                "- Casual conversation: 'how are you', 'thanks', 'goodbye' → Chat naturally",
                "- General questions about forms or processes → Explain helpfully",
                "- Clarification requests → Ask follow-up questions",
                "- When users are just chatting → Be engaging and helpful",
                "",
                "USE run_sql_query TOOL only when users specifically ask about their data:",
                "- 'who is the best candidate?' → Query the data",
                "- 'analyze the submissions' → Query and analyze",
                "- 'how many people applied?' → Count submissions",
                "- 'show me all candidates' → Retrieve candidate data",
                "- 'what are the trends in responses?' → Analyze patterns",
                "",
                "When you do need to query data:",
                "- The FormResponse table contains form submissions with a JSON 'data' column",
                "- Use PostgreSQL JSON operators like data->>'field_name' to extract fields",
                "- Always include the required form filter in your SQL",
                "- Use proper PostgreSQL syntax with double quotes for table/column names",
                "",
                "Remember: You're Flux - be conversational, helpful, and only use tools when actually needed!"
            ],
            tools=self._create_tools(),
            search_knowledge=False,
            read_chat_history=False,
            debug_mode=True,
        )
    
    def _create_final_reply_agent(self) -> Agent:
        model = self._get_preferred_model()
        
        return Agent(
            model=model,
            name="FinalReplyAgent",
            description="Crafts final, comprehensive responses based on analyzed data.",
            instructions=[
                "You are the final stage in a multi-step analysis pipeline.",
                "Your role is to synthesize insights from batch-processed data analysis.",
                "For sentiment analysis: summarize overall sentiment trends and notable patterns.",
                "For other analyses: highlight key findings and meaningful insights.",
                "Never mention technical details about data processing or SQL.",
                "Frame responses naturally as direct answers to the user's question.",
                "When handling batch results, weave them into a cohesive narrative.",
                "If results are part of a larger dataset, explicitly mention this context.",
                "Use clear, engaging language with well-formatted numbers and statistics.",
                "Respond using Markdown formatting (e.g., headings, bold, bullet lists, tables, links) so it renders nicely.",
            ],
            search_knowledge=False,
            read_chat_history=False,
            debug_mode=True,
        )
    
    def _create_batch_analyzer(self) -> Agent:
        model = self._get_preferred_model()
        
        return Agent(
            model=model,
            name="BatchAnalyzer",
            description="Analyzes batches of form submission data.",
            instructions=[
                "You analyze subsets of a larger dataset, one batch at a time.",
                "For sentiment analysis: evaluate text sentiment with detailed reasoning.",
                "For other analyses: extract meaningful patterns and insights.",
                "Remember you're seeing a subset - avoid absolute conclusions.",
                "Format findings consistently for easy aggregation.",
                "Include both quantitative metrics and qualitative observations.",
                "Flag any anomalies or points of interest for final synthesis.",
                "Respond in Markdown with clear formatting (lists, bold, etc.) suitable for end-user display.",
            ],
            search_knowledge=False,
            read_chat_history=False,
            debug_mode=True,
        )
    
    def _get_preferred_model(self):
        openai_key = os.getenv("OPENAI_API_KEY")
        groq_key = os.getenv("GROQ_API_KEY")
        
        if openai_key:
            return OpenAIChat(id=ModelConfig.GPT_4_NANO, api_key=openai_key)
        elif groq_key:
            return Groq(id=ModelConfig.LLAMA_70B, api_key=groq_key)
        else:
            raise ValueError("Either OPENAI_API_KEY or GROQ_API_KEY is required")
    
    def _get_base_instructions(self) -> List[str]:
        return [
            "You are Flux, a conversational assistant helping with form data analysis.",
            "When users need data analysis, you can query the FormResponse table which contains form submissions.",
            "The data column contains JSON with the actual form field values.",
            "For analysis requests:",
            "1. Understand what the user wants to know",
            "2. Write SQL that extracts the relevant fields from the JSON data",
            "3. Include proper filters as required",
            "4. Focus on answering the user's specific question",
            "Remember: You're having a conversation, not just writing SQL queries."
        ]
    
    def _determine_analysis_type(self, user_message: str) -> str:
        """Determine analysis type from user message."""
        message_lower = user_message.lower()
        
        if 'sentiment' in message_lower:
            return AnalysisType.SENTIMENT
        elif any(term in message_lower for term in ['trend', 'pattern', 'correlation']):
            return AnalysisType.TREND
        elif any(term in message_lower for term in ['compare', 'difference', 'versus']):
            return AnalysisType.COMPARATIVE
        else:
            return AnalysisType.GENERAL
    
    def _process_batch(self, batch_data: List[Dict[str, Any]], analysis_type: str, batch_num: int, total_batches: int) -> str:
        """Process a single batch of data using the batch analyzer."""
        try:
            response = self.batch_analyzer.run(
                message=f"Analyze this batch of data for {analysis_type}. "
                       f"This is batch {batch_num} of {total_batches}.\n\n"
                       f"Data: {json.dumps(batch_data, default=str)}",
                messages=[]
            )
            return str(response.content)
        except Exception as e:
            logger.error(f"Error processing batch {batch_num}: {e}")
            return f"Error analyzing batch {batch_num}: {str(e)}"
    
    def _analyze_results_in_batches(self, rows: List[Dict[str, Any]], analysis_type: str) -> str:
        """Analyze query results in batches using parallel processing."""
        if not rows:
            return "No data found to analyze."

        # Split data into batches
        batches = [rows[i:i + DatabaseConfig.BATCH_SIZE] for i in range(0, len(rows), DatabaseConfig.BATCH_SIZE)]
        total_batches = len(batches)
        
        # Process batches in parallel
        batch_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=DatabaseConfig.MAX_WORKERS) as executor:
            future_to_batch = {
                executor.submit(
                    self._process_batch, 
                    batch, 
                    analysis_type,
                    i + 1, 
                    total_batches
                ): i for i, batch in enumerate(batches)
            }
            
            for future in concurrent.futures.as_completed(future_to_batch):
                batch_num = future_to_batch[future]
                try:
                    result = future.result()
                    batch_results.append((batch_num, result))
                except Exception as e:
                    logger.error(f"Batch {batch_num} failed: {e}")
                    batch_results.append((batch_num, f"Error in batch {batch_num}: {str(e)}"))

        # Sort results by batch number
        batch_results.sort(key=lambda x: x[0])
        
        # Generate final comprehensive summary
        final_response = self.final_reply_agent.run(
            message=(
                f"Synthesize the following batch analysis results into a comprehensive response.\n\n"
                f"Analysis type: {analysis_type}\n"
                f"Total records analyzed: {len(rows)}\n"
                f"Number of batches: {total_batches}\n"
                f"User's question: {self._current_user_message}\n\n"
                "Batch results:\n" +
                "\n".join(f"Batch {i+1}:\n{result}" for i, result in batch_results)
            ),
            messages=[]
        )
        
        return str(final_response.content)
    
    def _analyze_small_dataset(self, rows: List[Dict[str, Any]], analysis_type: str) -> str:
        """Analyze small datasets directly without batching."""
        analysis_prompt = (
            f"Analyze this data set ({analysis_type}):\n\n"
            f"Data: {json.dumps(rows, default=str)}\n\n"
            f"Total records: {len(rows)}\n\n"
            f"User's question: {self._current_user_message}\n\n"
            "Guidelines:\n"
            "1. Provide a thorough but concise analysis\n"
            "2. Focus on key insights and patterns\n"
            "3. Use natural, friendly language\n"
            "4. Format numbers and statistics clearly\n"
            "5. Address the user's question directly\n"
        )

        response = self.final_reply_agent.run(
            message=analysis_prompt,
            messages=[]
        )

        return str(response.content)
    
    def _create_tools(self):
        @tool(
            name="run_sql_query",
            description="Execute a SQL query on the Postgres database that contains form submissions. For holistic analysis, you may omit the form_response_id filter. Set return_csv=True if you want to provide CSV data to the user regardless of result set size.",
            show_result=True,
            stop_after_tool_call=True,
        )
        def run_sql_query(sql_query: str, return_csv: bool = False) -> str:
            """Execute the provided SQL and process results appropriately."""
            try:
                # For holistic analysis, we don't enforce the filter
                if self._current_user_message and any(term in self._current_user_message.lower() 
                    for term in ['sentiment', 'analyze all', 'overall', 'holistic', 'trends']):
                    filtered_query = sql_query
                else:
                    filtered_query = self._apply_filters(sql_query)
                
                self._last_executed_query = filtered_query
                self._return_csv_requested = return_csv  # Store the CSV request flag
                
                # Execute SQL query
                rows = self.database_service.execute_query(filtered_query)
                self._last_result_rows = rows
                
                if not rows:
                    return "I couldn't find any matching data for your question."
                
                # Determine analysis type for context
                analysis_type = self._determine_analysis_type(self._current_user_message or "")
                
                # Only use batch processing for large datasets
                if len(rows) > DatabaseConfig.BATCH_SIZE:
                    return self._analyze_results_in_batches(rows, analysis_type)
                
                # For small datasets (≤50 records), analyze directly
                return self._analyze_small_dataset(rows, analysis_type)
                
            except Exception as exc:
                logger.error(f"SQL query execution failed: {exc}")
                return f"Query failed: {exc}"
        
        return [run_sql_query]
    
    def _apply_filters(self, query: str) -> str:
        """Apply required filters based on context."""
        if self._current_form_id:
            if f'"FormResponse"."formId" = \'{self._current_form_id}\'' not in query and f'"formId" = \'{self._current_form_id}\'' not in query:
                raise ValueError(f'Query must contain formId filter with proper quoting: WHERE "FormResponse"."formId" = \'{self._current_form_id}\'')
        elif self._current_form_response_id:
            if f'"FormResponse"."id" = \'{self._current_form_response_id}\'' not in query and f'"id" = \'{self._current_form_response_id}\'' not in query:
                raise ValueError(f'Query must contain form_response_id filter with proper quoting: WHERE "FormResponse"."id" = \'{self._current_form_response_id}\'')
        else:
            raise ValueError("Neither formId nor formResponseId provided for filter validation")
        
        return query
    
    def set_context(self, form_id: Optional[str] = None, form_response_id: Optional[str] = None, user_message: Optional[str] = None, user_id: Optional[str] = None):
        """Set the context for query execution."""
        self._current_form_id = form_id
        self._current_form_response_id = form_response_id
        self._current_user_message = user_message
        self._current_user_id = user_id
    
    def execute_query(self, user_message: str, instructions: List[str], user_id: Optional[str] = None) -> str:
        """Execute a query with the given instructions and return the response."""
        self._current_user_message = user_message
        if user_id:
            self._current_user_id = user_id
        
        # Get relevant context from memory if available (with timeout)
        memory_context = ""
        if self.memory_service.is_enabled() and self._current_user_id:
            try:
                # Use threading with timeout for memory context retrieval
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        self.memory_service.get_user_context, 
                        self._current_user_id, 
                        user_message
                    )
                    memory_context = future.result(timeout=2.0)  # 2 second timeout
                    
                if memory_context:
                    logger.info(f"Retrieved memory context for user {self._current_user_id}")
            except concurrent.futures.TimeoutError:
                logger.warning("Memory context retrieval timed out, proceeding without context")
                memory_context = ""
            except Exception as e:
                logger.warning(f"Memory context retrieval failed: {e}")
                memory_context = ""
        
        # Enhance instructions with memory context
        enhanced_instructions = self._get_base_instructions() + instructions
        if memory_context:
            enhanced_instructions.append(f"Additional context from user's previous interactions: {memory_context}")
        
        self.agent.instructions = enhanced_instructions
        
        try:
            logger.info(f"Processing user message: '{user_message}'")
            run = self.agent.run(message=user_message, messages=[])
            response = str(run.content)
            
            # Store memory asynchronously without blocking (fire and forget)
            if self.memory_service.is_enabled() and self._current_user_id:
                # Start memory storage in a daemon thread that won't block the response
                memory_thread = threading.Thread(
                    target=self._store_memory_background,
                    args=(user_message, response),
                    daemon=True
                )
                memory_thread.start()
            
            return response
        except Exception as e:
            logger.error(f"Failed to execute SQL agent query: {e}")
            raise
    
    def _store_memory_background(self, user_message: str, response: str):
        """Store conversation memory in background thread without blocking."""
        try:
            # Determine if this was a conversational or SQL-based interaction
            query_type = "sql_analysis" if self._last_executed_query else "conversational"
            
            context = {
                "form_id": self._current_form_id,
                "form_response_id": self._current_form_response_id,
                "query_type": query_type
            }
            
            # Store memory with timeout
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    self.memory_service.add_conversation_memory,
                    self._current_user_id,
                    user_message,
                    response,
                    context
                )
                success = future.result(timeout=10.0)  # 10 second timeout for memory storage
            
            if success:
                logger.info(f"Stored {query_type} memory for user {self._current_user_id}")
            else:
                logger.warning(f"Failed to store memory for user {self._current_user_id}")
                
        except concurrent.futures.TimeoutError:
            logger.warning("Memory storage timed out, but response was already returned")
        except Exception as e:
            logger.error(f"Background memory storage failed: {e}")
    
    @property
    def last_query(self) -> Optional[str]:
        return self._last_executed_query
    
    @property
    def last_results(self) -> List[Dict[str, Any]]:
        return self._last_result_rows 

    @property
    def return_csv_requested(self) -> bool:
        return self._return_csv_requested 