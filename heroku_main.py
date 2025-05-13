# heroku_main.py
from app import app

# Nota: Este archivo permite que Heroku arranque la app
# No debe contener lógica de ejecución adicional
def create_app():
    return app

if __name__ == "__main__":
    app.run(debug=False)
