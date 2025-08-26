from flask import Flask
from config import Config
import os
import logging

# Configure basic logging for the module if not in debug mode via app
# Basic config can be overridden by app.logger settings if app is in debug mode
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_app(config_class=Config):
    # Explicitamente definimos template_folder y static_folder relativos a 'app'
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_class)

    # Crear directorio de datos si no existe
    # data_dir debe estar fuera de la carpeta app para no ser servido accidentalmente
    # y para facilitar el montaje de volúmenes en contenedores.
    # Si run.py está en la raíz del proyecto, y app es un subdirectorio:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)
    app.config['DATA_DIR'] = data_dir
    logging.info(f"Directorio de datos DATA_DIR inicializado en: {app.config['DATA_DIR']}")

    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    from .api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Flask's app.logger is already configured. 
    # If in debug mode, Flask usually sets it to DEBUG level.
    if app.debug:
        # You can add more specific handlers or formatters for app.logger here if needed
        app.logger.info("Modo DEBUG activado. Logging de Flask configurado.")
    else:
        app.logger.info("Aplicación creada. Logging de Flask configurado.")

    return app 