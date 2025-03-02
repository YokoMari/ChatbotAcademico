# Bibliotecas y Modulos
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
from chatlstm import get_response
from datetime import datetime
import json
import os
import bcrypt
import uuid

# Aplicacion en FLASK
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave_secreta_segura")

# Usuario de la Interfaz de Administraccion
USERS = {
    "admin": bcrypt.hashpw(b"1234", bcrypt.gensalt())
}

# Pagina de Inicio
@app.route("/")
def index():
    return render_template("index.html")

# Pagina de Login 
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").encode("utf-8")
        
        if username in USERS and bcrypt.checkpw(password, USERS[username]):
            session["logged_in"] = True
            return redirect(url_for("conversations"))
        
      return render_template("login.html", error="Credenciales incorrectas")
    return render_template("login.html")

# Pagina de Cierre de sesion
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

# Pagina de Administraccion
@app.route("/conversations")
def conversations():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    # Donde se almacenan las conversaciones
    log_file = "conversations.json"                              
    conversations = {}

    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                for entry in data:
                    user_id = entry["user_id"]
                    if user_id not in conversations:
                        conversations[user_id] = []
                    conversations[user_id].append(entry)
            except json.JSONDecodeError:
                conversations = {}

    return render_template("conversations.html", conversations=conversations)

# Interaccion con el Chatbot
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"answer": "Mensaje vacío no permitido"}), 400
    
    text = data["message"].strip()
    if not text:
        return jsonify({"answer": "Mensaje vacío no permitido"}), 400

    user_id = request.cookies.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())

    # Respuesta del Chatbot
    response = get_response(text)
    resp = make_response(jsonify({"answer": response}))
    resp.set_cookie("user_id", user_id, max_age=3600)

    # Registra la conversacion en el conversacion.json
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_only = datetime.now().strftime('%H:%M:%S')
    log_file = "conversations.json"
    conversations = []

    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as file:
            try:
                conversations = json.load(file)
            except json.JSONDecodeError:
                conversations = []

    # Lista de Conversaciones
    conversations.append({
        "user_id": user_id, 
        "timestamp": timestamp, 
        "time_only": time_only, 
        "user": text, 
        "bot": response
    })

    # Actualiza JSON
    with open(log_file, "w", encoding="utf-8") as file:
        json.dump(conversations, file, ensure_ascii=False, indent=4)

    return resp

# Ejecuta la Aplicacion
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
