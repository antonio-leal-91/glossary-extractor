import threading
import webview
from app import app
import time

def run_flask():
    print(">>> Iniciando servidor Flask...")
    app.run(debug=False, port=5000)

if __name__ == '__main__':
    print(">>> Iniciando hilo Flask...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    time.sleep(2)
    print(">>> Mostrando ventana WebView...")
    webview.create_window("GlossaryExtractor", "http://127.0.0.1:5000", width=1200, height=800)
    webview.start(gui='edgechromium')  # 👈 ESTA LÍNEA ES IMPRESCINDIBLE
