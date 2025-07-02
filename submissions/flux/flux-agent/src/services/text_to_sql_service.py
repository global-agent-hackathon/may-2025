import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from constants.enums import AnalysisType, DatabaseConfig
from core.database import DatabaseService
from agents.sql_agent import SQLAgent
from models.chat_models import ChatMessage, ChatResponse, TextContentBlock, CSVContentBlock
from utils.data_processors import DataProcessor
from utils.logger import get_logger

logger = get_logger()


class TextToSQLService:
    def __init__(self):
        self.database_service = DatabaseService()
        self.sql_agent = SQLAgent(self.database_service)
        self.data_processor = DataProcessor()
    
    def generate_response(
        self, 
        form_id: Optional[str] = None,
        form_response_id: Optional[str] = None,
        user_message: str = "",
        chat_history: List[ChatMessage] = [],
        form_config: Optional[Any] = None,
        form_response_data: Optional[Any] = None,
        user_id: Optional[str] = None
    ) -> ChatResponse:
        
        # Set context for the SQL agent
        self.sql_agent.set_context(
            form_id=form_id, 
            form_response_id=form_response_id,
            user_message=user_message,
            user_id=user_id
        )
        
        # Build instructions for the agent
        instructions = self._build_instructions(
            form_id, form_response_id, form_config, form_response_data, chat_history
        )
        
        try:
            # Execute query and get analysis in one step (restored original logic)
            summary_text = self.sql_agent.execute_query(user_message, instructions, user_id)
            
            content_blocks = [TextContentBlock(text=summary_text)]
            
            # Generate CSV data if either:
            # 1. Result set is large (> BATCH_SIZE), OR
            # 2. SQL agent explicitly requested CSV via return_csv=True
            results = self.sql_agent.last_results
            should_generate_csv = (
                results and (
                    len(results) > DatabaseConfig.BATCH_SIZE or 
                    self.sql_agent.return_csv_requested
                )
            )
            
            if should_generate_csv:
                csv_data = self.data_processor.rows_to_form_data_csv(results)
                if csv_data:
                    csv_description = f"Full table with {len(results)} rows"
                    if self.sql_agent.return_csv_requested and len(results) <= DatabaseConfig.BATCH_SIZE:
                        csv_description += " (CSV requested by analysis)"
                    
                    content_blocks.append(
                        CSVContentBlock(
                            data=csv_data,
                            description=csv_description
                        )
                    )
            
            return ChatResponse(
                content_blocks=content_blocks,
                sourceQuery=self.sql_agent.last_query,
                timestamp=datetime.now().isoformat(),
            )
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return self._create_error_response(f"Sorry, I ran into an error: {e}")
    
    def _build_instructions(
        self, 
        form_id: Optional[str], 
        form_response_id: Optional[str],
        form_config: Optional[Any],
        form_response_data: Optional[Any],
        chat_history: List[ChatMessage]
    ) -> List[str]:
        
        schema_info = self._extract_schema_info(form_config)
        response_info = json.dumps(form_response_data, indent=2) if form_response_data else "{}"
        history_block = self._build_history_block(chat_history)
        
        filter_info = self._build_filter_info(form_id, form_response_id)
        
        # Build the correct filter syntax example based on what we have
        if form_id:
            filter_syntax_example = f'WHERE "FormResponse"."formId" = \'{form_id}\''
            csv_example = f'run_sql_query(\'SELECT * FROM "FormResponse" WHERE "FormResponse"."formId" = \\"{form_id}\\"\', return_csv=True)'
            required_filter = f'"FormResponse"."formId" = \'{form_id}\''
            filter_type = "formId"
        else:
            filter_syntax_example = f'WHERE "FormResponse"."id" = \'{form_response_id}\''
            csv_example = f'run_sql_query(\'SELECT * FROM "FormResponse" WHERE "FormResponse"."id" = \\"{form_response_id}\\"\', return_csv=True)'
            required_filter = f'"FormResponse"."id" = \'{form_response_id}\''
            filter_type = "form response ID"
        
        return [
            "You are an expert assistant that can inspect form submissions stored in Postgres.",
            self._get_db_schema(),
            self._get_fields_description(form_config),
            f"The form data structure is as follows (JSON schema or config):\n{schema_info}",
            "If you need examples, here is a sample form submission (JSON):",
            response_info,
            "Conversation so far (latest last):",
            history_block,
            "",
            "🚨 CRITICAL SECURITY REQUIREMENT 🚨",
            f"EVERY SINGLE SQL QUERY MUST INCLUDE THIS EXACT FILTER: {required_filter}",
            f"You are restricted to analyzing data for this specific {filter_type} ONLY.",
            "",
            "MANDATORY SQL REQUIREMENTS:",
            f"✅ REQUIRED: Every query MUST contain: {filter_syntax_example}",
            f"✅ REQUIRED: Use exact table name: \"FormResponse\"",
            f"✅ REQUIRED: Use double quotes for column names: \"FormResponse\".\"formId\"",
            "❌ FORBIDDEN: Never omit the form filter",
            "❌ FORBIDDEN: Never use backticks (```)",
            "❌ FORBIDDEN: Never modify the form ID value",
            "",
            "JSON DATA EXTRACTION:",
            "The 'data' column contains JSON. Use PostgreSQL JSON operators to extract fields:",
            "✅ data->>'field_name' AS field_name (extracts as text)",
            "✅ data->'field_name' AS field_name (extracts as JSON)",
            "✅ (data->>'field_name')::integer AS field_name (cast to integer)",
            "",
            "CORRECT QUERY EXAMPLES WITH JSON EXTRACTION:",
            f"✅ SELECT data->>'name' AS name, data->>'email' AS email FROM \"FormResponse\" WHERE {required_filter}",
            f"✅ SELECT COUNT(*) FROM \"FormResponse\" WHERE {required_filter}",
            f"✅ SELECT data->>'name' AS name, data->>'skills' AS skills FROM \"FormResponse\" WHERE {required_filter} ORDER BY \"createdAt\"",
            f"✅ SELECT data FROM \"FormResponse\" WHERE {required_filter} ORDER BY \"createdAt\"",
            "",
            "WRONG QUERY EXAMPLES (WILL FAIL):",
            "❌ SELECT COUNT(*) FROM \"FormResponse\" (missing filter)",
            "❌ SELECT name, email FROM \"FormResponse\" (fields don't exist as columns)",
            "❌ SELECT * FROM FormResponse WHERE formId = 'some-id' (wrong quoting)",
            "❌ SELECT * FROM `FormResponse` WHERE `formId` = 'id' (backticks not allowed)",
            "",
            filter_info["note"],
            f"Example correct query: {filter_info['example']}",
            "",
            "CSV DATA INSTRUCTIONS:",
            "- If the user asks for 'export', 'download', 'CSV', 'spreadsheet', or 'table data', set return_csv=True",
            "- If the user wants to 'see all data', 'full results', or 'complete list', set return_csv=True", 
            "- For analysis requests without explicit data export needs, use return_csv=False (default)",
            f"- Example: {csv_example} for data exports",
            "",
            "REMEMBER: The filter is MANDATORY for security. Every query must include it!",
            "REMEMBER: Extract data from JSON using data->>'field_name' syntax!"
        ]
    
    def _extract_schema_info(self, form_config: Optional[Any]) -> str:
        if form_config and isinstance(form_config, dict):
            if "schema" in form_config and isinstance(form_config["schema"], dict):
                fields_only = {
                    "title": form_config.get("title", ""),
                    "fields": form_config["schema"].get("fields", [])
                }
            else:
                fields_only = {
                    "title": form_config.get("title", ""),
                    "fields": form_config.get("fields", [])
                }
            return json.dumps(fields_only, indent=2)
        return "{}"
    
    def _build_history_block(self, chat_history: List[ChatMessage]) -> str:
        history_lines = []
        for msg in chat_history[-10:]:
            role_label = "User" if msg.role == "user" else "Assistant"
            history_lines.append(f"- {role_label}: {msg.content}")
        return "\n".join(history_lines)
    
    def _build_filter_info(self, form_id: Optional[str], form_response_id: Optional[str]) -> Dict[str, str]:
        if form_id:
            return {
                "note": "You MUST restrict all queries to the provided formId using the filter.",
                "example": f'SELECT * FROM "FormResponse" WHERE "FormResponse"."formId" = \'{form_id}\''
            }
        else:
            return {
                "note": "You MUST restrict all queries to the provided formResponseId using the filter.",
                "example": f'SELECT * FROM "FormResponse" WHERE "FormResponse"."id" = \'{form_response_id}\''
            }
    
    def _get_db_schema(self) -> str:
        return (
            "Table `FormResponse` columns:\n"
            "- id (STRING, primary key)\n"
            "- data (JSON) – stores the submission fields\n"
            "- formId (STRING) – foreign key to Form.id\n"
            "- createdAt (TIMESTAMP)\n"
            "- updatedAt (TIMESTAMP)\n"
        )
    
    def _get_fields_description(self, form_config: Optional[Any]) -> str:
        if not form_config or not isinstance(form_config, dict):
            return ""
        
        field_list = form_config.get("schema", {}).get("fields", [])
        if not field_list:
            field_list = form_config.get("fields", [])
        
        if field_list:
            parts = []
            for f in field_list:
                label = f.get("label", f.get("id", "?"))
                ftype = f.get("type", "unknown")
                parts.append(f"    • {label} (type: {ftype})")
            return "These are the expected keys in `data` JSON column:\n" + "\n".join(parts)
        
        return ""
    
    def _create_error_response(self, error_message: str) -> ChatResponse:
        return ChatResponse(
            content_blocks=[TextContentBlock(text=error_message)],
            timestamp=datetime.now().isoformat()
        )

    def process_message(
        self,
        message: str,
        form_id: Optional[str] = None,
        form_response_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ChatResponse:
        """Process a chat message and generate a response."""
        try:
            # Use the existing generate_response method which has all the proper logic
            return self.generate_response(
                form_id=form_id,
                form_response_id=form_response_id,
                user_message=message,
                chat_history=[],  # We don't have chat history in this context
                form_config=None,  # We don't have form config in this context
                form_response_data=None,  # We don't have form response data in this context
                user_id=user_id
            )
            
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            return self._create_error_response(f"Sorry, I ran into an error: {e}") 