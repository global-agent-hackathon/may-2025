import subprocess
import sys
import logging
from app import create_app

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_tests():
    """Runs pytest and returns the exit code."""
    logging.info("Ejecutando pruebas...")
    # Note: Adjust the command if your pytest is not directly on PATH
    # or if you need to activate a virtual environment first in a shell script.
    # For direct Python execution, ensure pytest is installed in the environment.
    try:
        # We use sys.executable to ensure we run pytest with the same python interpreter
        result = subprocess.run([sys.executable, "-m", "pytest", "--cov=app"], capture_output=True, text=True, check=False)
        if result.stdout:
            logging.info(f"Pytest stdout:\n{result.stdout}")
        if result.stderr:
            logging.error(f"Pytest stderr:\n{result.stderr}")
        return result.returncode
    except FileNotFoundError:
        logging.error("Error: pytest no encontrado. Asegúrate de que esté instalado y en tu PATH.")
        logging.error("Puedes instalarlo con: pip install pytest pytest-cov")
        return -1 # Indicate a setup error
    except Exception as e:
        logging.error(f"Ocurrió un error inesperado al ejecutar pytest: {e}")
        return -1 # Indicate an unexpected error

app = create_app()

if __name__ == '__main__':
    test_exit_code = run_tests()
    if test_exit_code == 0:
        logging.info("Todas las pruebas pasaron. Iniciando la aplicación...")
        app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', False))
    elif test_exit_code == 5: # pytest specific exit code: no tests collected
        logging.warning("Advertencia: No se recolectaron pruebas por pytest. Iniciando la aplicación de todas formas...")
        logging.warning("Asegúrate de que tus pruebas estén correctamente configuradas.")
        app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', False))
    else:
        logging.error("Las pruebas fallaron o ocurrió un error. La aplicación no se iniciará.")
        logging.error(f"Pytest finalizó con el código de salida: {test_exit_code}")
        sys.exit(test_exit_code) # Exit with pytest's error code 