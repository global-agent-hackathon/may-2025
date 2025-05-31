from flask import request, jsonify, session, current_app
from app.api import bp
from app.agent_core.chat_handler import handle_message
import uuid
import logging

@bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    current_app.logger.info(f"Solicitud POST a /api/chat recibida. Datos: {data}")

    if not data or 'message' not in data:
        current_app.logger.warning("Solicitud a /api/chat sin 'message' en los datos.")
        return jsonify({'error': 'No se proporcionó el mensaje'}), 400
    
    user_message = data['message']
    current_app.logger.debug(f"Mensaje del usuario: {user_message}")
    
    if 'session_id' not in session:
        session['session_id'] = uuid.uuid4().hex
        current_app.logger.info(f"Nueva session_id generada: {session['session_id']}")
    if 'user_id' not in session:
        # Por ahora, user_id es igual a session_id. Podría cambiar si se implementa autenticación.
        session['user_id'] = session['session_id']
        current_app.logger.info(f"Nuevo user_id generado (igual a session_id): {session['user_id']}")

    user_id = session['user_id']
    session_id = session['session_id']
    current_app.logger.debug(f"Usando user_id: {user_id}, session_id: {session_id} para manejar el mensaje.")

    try:
        response_md = handle_message(user_message, user_id=user_id, session_id=session_id)
        current_app.logger.info(f"Respuesta generada exitosamente para session_id: {session_id}")
        current_app.logger.debug(f"Contenido de la respuesta (primeros 100 caracteres): {response_md[:100]}...")
        return jsonify({'response': response_md})
    except Exception as e:
        # Este error ya se loggea con exc_info=True, lo cual es bueno.
        current_app.logger.error(f"Error en la ruta /api/chat al llamar a handle_message para session_id {session_id}: {e}", exc_info=True)
        return jsonify({'error': f'Ocurrió un error interno al procesar tu solicitud.'}), 500 