from flask import current_app
from agno.agent import Agent
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
import os
import logging # Ensure logging is imported

# Importar configuraciones y herramientas específicas del agente
from .agent_config import (
    FirecrawlTool,
    FIRECRAWL_INSTRUCTION,
    FIRECRAWL_TEMPLATE,
    AGENT_INSTRUCTIONS
)

# Variable global para el agente, inicializada una vez
_agent = None
_agent_storage = None

def get_agent_storage():
    """Inicializa y/o devuelve la instancia de SqliteStorage."""
    global _agent_storage
    current_app.logger.debug("get_agent_storage llamado.")
    if _agent_storage is None:
        current_app.logger.info("Inicializando nueva instancia de SqliteStorage para el agente.")
        data_dir = current_app.config['DATA_DIR']
        db_file_path = os.path.join(data_dir, "agent_sessions.db")
        current_app.logger.debug(f"Ruta de la base de datos de almacenamiento: {db_file_path}")
        _agent_storage = SqliteStorage(
            table_name="agent_sessions", 
            db_file=db_file_path
        )
        current_app.logger.info("SqliteStorage inicializado.")
    else:
        current_app.logger.debug("Usando instancia de SqliteStorage existente.")
    return _agent_storage

def get_agent():
    """Inicializa y/o devuelve la instancia del Agente Agno configurado."""
    global _agent
    current_app.logger.debug("get_agent llamado.")
    if _agent is None:
        current_app.logger.info("Inicializando nueva instancia del Agente Agno.")
        google_api_key = current_app.config.get('GOOGLE_API_KEY')
        firecrawl_api_key = current_app.config.get('FIRECRAWL_API_KEY')

        if not google_api_key:
            current_app.logger.error("GOOGLE_API_KEY no configurada en .env. El agente no se puede inicializar.")
            raise ValueError("GOOGLE_API_KEY no configurada en .env")
        else:
            current_app.logger.debug("GOOGLE_API_KEY encontrada.")
        
        if not firecrawl_api_key:
            # FirecrawlTool itself will raise an error if the key is missing when an instance is created.
            # Logging a warning here is still useful for earlier detection.
            current_app.logger.warning("FIRECRAWL_API_KEY no configurada en .env. La herramienta Firecrawl no funcionará.")
        else:
            current_app.logger.debug("FIRECRAWL_API_KEY encontrada.")

        # Inicializar el modelo
        model_id = "gemini-2.0-flash" # Reverted to original model ID
        current_app.logger.info(f"Inicializando modelo Gemini con ID: {model_id}")
        model = Gemini(
            api_key=google_api_key,
            id=model_id 
        )

        # Inicializar la herramienta Firecrawl
        current_app.logger.info("Inicializando FirecrawlTool.")
        firecrawl_tool = FirecrawlTool(
            api_key=firecrawl_api_key,
            instruction=FIRECRAWL_INSTRUCTION,
            template=FIRECRAWL_TEMPLATE
        )
        tools_list = [firecrawl_tool.search]
        current_app.logger.debug(f"Herramientas configuradas para el agente: {[tool.__name__ for tool in tools_list]}")

        # Obtener el storage
        storage = get_agent_storage()

        # Crear el Agente
        show_tool_calls_flag = current_app.config.get('DEBUG', False)
        current_app.logger.info(f"Creando Agente Agno con instructions, storage, add_history_to_messages=True, show_tool_calls={show_tool_calls_flag}")
        _agent = Agent(
            model=model,
            tools=tools_list,
            instructions=AGENT_INSTRUCTIONS,
            storage=storage,
            add_history_to_messages=True, # Para usar el storage y mantener historial
            show_tool_calls=show_tool_calls_flag # Mostrar logs de herramientas en modo debug
        )
        current_app.logger.info("Agente Agno inicializado exitosamente.")
    else:
        current_app.logger.debug("Usando instancia de Agente Agno existente.")
    return _agent 