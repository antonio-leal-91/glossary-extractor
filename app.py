from flask import Flask, request, jsonify, render_template, send_file
import os
import pandas as pd
import pdfplumber
from docx import Document
from lxml import etree
import tempfile
import re
import requests
from openai import OpenAI, RateLimitError
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1 GB

# Claves desde entorno
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)
BLOCK_SIZE = 3000  # Tamaño de bloque

def limpiar_termino(termino):
    termino = termino.strip("-•*1234567890. ").strip()
    if termino.isupper():
        return termino
    if re.match(r"^[A-Z][a-z]+(\s[A-Z][a-z]+)*$", termino):
        return termino
    return termino.lower()

def extract_text(file):
    filename = file.filename.lower()
    text = ""

    try:
        if filename.endswith(".xlsx"):
            xls = pd.ExcelFile(file)
            for sheet in xls.sheet_names:
                df = xls.parse(sheet)
                text += " " + " ".join(df.astype(str).values.flatten())

        elif filename.endswith(".csv"):
            df = pd.read_csv(file)
            text = " ".join(df.astype(str).values.flatten())

        elif filename.endswith(".pdf"):
            with pdfplumber.open(file) as pdf:
                text = " ".join(page.extract_text() or "" for page in pdf.pages)

        elif filename.endswith(".docx"):
            doc = Document(file)
            text = " ".join(p.text for p in doc.paragraphs)

        elif filename.endswith((".xliff", ".sdlxliff")):
            tree = etree.parse(file)
            text = " ".join(tree.xpath("//trans-unit/source/text()"))

        elif filename.endswith(".txt"):
            text = file.read().decode("utf-8")
    except Exception as e:
        print("Error extrayendo texto:", e)

    return text

def get_terms_openai(text, source_lang, target_lang):
    if not text.strip():
        return ""

    prompt = (
        f"Del siguiente texto en {source_lang}, extrae aproximadamente 10 términos clave por cada 1000 palabras, uno por línea. "
        f"Para cada término, proporciona una traducción sugerida al {target_lang} separada por tabulador. Evita repeticiones. "
        f"Conserva nombres propios y siglas, y usa minúsculas para términos generales.\n\nTexto:\n{text}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except RateLimitError:
        return ""
    except Exception as e:
        print("OpenAI Error:", e)
        return ""

def get_terms_deepseek(text, source_lang, target_lang):
    if not text.strip():
        return ""
    prompt = (
        f"Del siguiente texto en {source_lang}, extrae aproximadamente 10 términos clave por cada 1000 palabras, uno por línea. "
        f"Para cada término, proporciona una traducción sugerida al {target_lang} separada por tabulador. Evita repeticiones. "
        f"Conserva nombres propios y siglas, y usa minúsculas para términos generales.\n\nTexto:\n{text}"
    )
    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        return response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
    except Exception as e:
        print("DeepSeek Error:", e)
        return ""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process_file():
    uploaded_files = request.files.getlist("files")
    source_lang = request.form.get("source_lang", "ES").upper()
    target_lang = request.form.get("target_lang", "EN").upper()
    provider = request.form.get("provider", "openai").lower()

    all_text = ""
    for file in uploaded_files:
        all_text += extract_text(file) + "\n"

    blocks = [all_text[i:i+BLOCK_SIZE] for i in range(0, len(all_text), BLOCK_SIZE)]
    all_terms = []

    for block in blocks:
        raw = get_terms_deepseek(block, source_lang, target_lang) if provider == "deepseek" else get_terms_openai(block, source_lang, target_lang)

        for line in raw.splitlines():
            if "\t" in line:
                source, target = line.split("\t", 1)
                term = {"source": limpiar_termino(source), "target": target.strip()}
                if term not in all_terms:
                    all_terms.append(term)

    return jsonify({"terms": all_terms, "source_lang": source_lang, "target_lang": target_lang})

@app.route("/export", methods=["POST"])
def export_selected():
    data = request.get_json()
    terms = data.get("terms", [])
    source_lang = data.get("source_lang", "ES")
    target_lang = data.get("target_lang", "EN")

    txt_path = os.path.join(tempfile.gettempdir(), "glosario.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(t["source"] for t in terms))

    df = pd.DataFrame(terms, columns=["source", "target"])
    df.columns = [source_lang, target_lang]
    excel_path = os.path.join(tempfile.gettempdir(), "glosario.xlsx")
    df.to_excel(excel_path, index=False)

    return jsonify({"txt_file": "/download/txt", "excel_file": "/download/excel"})

@app.route("/download/txt")
def download_txt():
    return send_file(
        os.path.join(tempfile.gettempdir(), "glosario.txt"),
        as_attachment=True,
        download_name="glosario.txt"
    )

@app.route("/download/excel")
def download_excel():
    return send_file(
        os.path.join(tempfile.gettempdir(), "glosario.xlsx"),
        as_attachment=True,
        download_name="glosario.xlsx"
    )

@app.errorhandler(RequestEntityTooLarge)
def file_too_large(e):
    return "🚫 El archivo supera el límite de 1 GB permitido.", 413

if __name__ == "__main__":
    app.run(debug=True)
