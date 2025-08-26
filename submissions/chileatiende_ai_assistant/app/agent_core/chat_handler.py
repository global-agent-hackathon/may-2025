from flask import current_app
from .agent_setup import get_agent
import logging # Ensure logging is imported, though current_app.logger is used

def handle_message(message: str, user_id: str, session_id: str) -> str:
    """Procesa el mensaje con el agente usando IDs de usuario/sesión y devuelve la respuesta en formato Markdown."""
    current_app.logger.info(f"handle_message llamado para user_id: {user_id}, session_id: {session_id}")
    current_app.logger.debug(f"Mensaje a procesar: {message}")
    
    agent = get_agent() # Obtiene la instancia configurada del agente
    current_app.logger.debug("Instancia del agente obtenida.")
    
    try:
        current_app.logger.debug(f"Llamando a agent.run con user_id: {user_id}, session_id: {session_id}, markdown=True")
        result = agent.run(
            message=message, 
            user_id=user_id, 
            session_id=session_id,
            markdown=True # Aseguramos respuesta en Markdown
        )
        current_app.logger.debug(f"Resultado de agent.run (tipo: {type(result)}): {str(result)[:200]}...") # Loguear tipo y parte del resultado
        
        # Verificar si result tiene el atributo content y no es None
        if hasattr(result, 'content') and result.content is not None:
            current_app.logger.debug("Devolviendo result.content")
            return result.content
        elif isinstance(result, str): # Si agent.run devuelve directamente un string
            current_app.logger.debug("Devolviendo resultado como string directo.")
            return result
        else:
            current_app.logger.error(f"Respuesta inesperada del agente (tipo: {type(result)}): {result} para session_id: {session_id}")
            return "Lo siento, ocurrió un error inesperado al procesar tu solicitud."
            
    except Exception as e:
        current_app.logger.error(f"Error en handle_message para session_id {session_id}: {e}", exc_info=True)
        return f"Lo siento, ocurrió un error al procesar tu mensaje: {str(e)}" 