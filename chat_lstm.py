# Bibliotecas y Modulos
import json
import requests
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from typing import List, Dict

# API OLLAMA y Modelo
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3.2"

# Carga las intenciones 
with open('intents.json', 'r', encoding='utf-8') as json_data:
    intents = json.load(json_data)

# Nombre del Bot
bot_name = "Tyto"

# Cargar el modelo local y su tokenizado (t5-small)
local_model = AutoModelForSeq2SeqLM.from_pretrained("t5-small")
local_tokenizer = AutoTokenizer.from_pretrained("t5-small")

# Funcion para el Pronmt
def build_prompt(user_input: str, intents_data: Dict) -> str:
    prompt = f"{intents_data['general_instructions']}\n\n"
    prompt += "A continuación, algunos ejemplos de cómo responder a diferentes tipos de preguntas:\n"

    # Itera sobre los intents para añadir contexto y ejemplos al prompt
    for intent in intents_data["intents"]:
        examples = ", ".join(intent["examples"])
        prompt += f"- Situación: {intent['context']}\n"
        prompt += f"  Ejemplos de entrada: {examples}\n"
        prompt += f"  Estilo de respuesta: {intent['response_style']}\n"

    # Añade la entrada del usuario al final del prompt
    prompt += f"\nPregunta del usuario: {user_input}\n"
    prompt += f"Respuesta de {bot_name}: "
    return prompt

# Funcion para la Respuesta del Modelo local (t5)
def get_response_from_local_model(msg):
    print(f"[DEBUG] Usando el modelo local (T5)")  # Mensaje de depuración
    inputs = local_tokenizer(msg, return_tensors="pt")
    outputs = local_model.generate(inputs["input_ids"], max_length=150)
    response = local_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Funcion para la Respuesta del Modelo Ollama (Llama 3.2)
def get_response(msg: str) -> str:
    try:
        prompt = build_prompt(msg, intents)
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.8,
            "max_tokens": 70
        }
        print(f"[DEBUG] Intentando usar Ollama ({MODEL_NAME})")  # Mensaje de depuración
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        print(f"[DEBUG] Respuesta exitosa de Ollama")  # Confirmación
        return result["response"].strip()
    except Exception as e:
        print(f"[DEBUG] Error con Ollama: {str(e)}. Cambiando al modelo local.")  # Mostrar el error
        return get_response_from_local_model(msg)

# Interactuar con el chatbot en la consola
if __name__ == "__main__":
    print("¡Hablemos! (escribe 'salir' para terminar)")
    while True:
        sentence = input("Tú: ")
        if sentence.lower() == "salir":
            break
        resp = get_response(sentence)
        print(f"{bot_name}: {resp}")
