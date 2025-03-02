# Bibliotecas
import pandas as pd
import json

# Funcion que genera los datos de entrenamiento
def train():
    with open('intents.json', 'r', encoding='utf-8') as json_data:
        intents = json.load(json_data)

    # Lista para almacenar los mensajes (chatbot y usuario)
    data = []

  # Iteracion sobre cada intencion 
    for intent in intents['intents']:
        for user_msg in intent['examples']:
            bot_response = f"Respuesta de Tyto: {intent['response_style']}"
            data.append({"input": user_msg, "output": bot_response})
    
    # Crear el DataFrame una sola vez con todos los datos
    df = pd.DataFrame(data, columns=['input', 'output'])
    df.to_csv('train_data.csv', index=False)

# El codigo solo se ejecute en el principal
if __name__ == "__main__":
    train()


