# GlossaryExtractor 🧠🌐

Aplicación web para extracción y traducción automática de términos clave desde documentos multiformato (PDF, DOCX, Excel, TXT, XLIFF...).

![Render Ready](https://img.shields.io/badge/deploy-Render-blue?logo=render)

## 🚀 Funcionalidades

- Subida de múltiples archivos simultáneamente.
- Extracción automática de términos por bloque de texto.
- Traducción automática usando **OpenAI** o **DeepSeek**.
- Exportación de glosarios en **.txt** y **.xlsx**.
- Interfaz web multilingüe (ES / EN).

## 🧪 Tecnologías usadas

- Python 3
- Flask
- OpenAI API / DeepSeek API
- Bootstrap 5
- Gunicorn (para despliegue)
- PDFPlumber, Pandas, lxml, python-docx

## 📁 Estructura principal

```bash
├── app.py                 # Lógica principal Flask
├── main.py                # Arranque local con PyWebView (opcional)
├── requirements.txt       # Dependencias del proyecto
├── Procfile               # Configuración para Render
├── templates/
│   └── index.html         # Interfaz web
├── static/
│   └── globalingua-logo.png
├── .gitignore
└── README.md
```

## 🧑‍💻 Cómo ejecutar localmente

```bash
python3 -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
python main.py
```

> ⚠️ Asegúrate de tener una variable de entorno llamada `OPENAI_API_KEY` en un archivo `.env` o en tu sistema.

## 🌍 Despliegue en Render

1. Subir este proyecto a GitHub.
2. Crear un nuevo Web Service en [https://render.com](https://render.com).
3. Usar los siguientes parámetros:

   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `gunicorn app:app`

4. Agregar la variable `OPENAI_API_KEY` en el entorno de Render.

## 📄 Licencia

Este proyecto está desarrollado por Globalingua © 2025.
