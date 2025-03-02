# Bibliotecas
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, Seq2SeqTrainer, Seq2SeqTrainingArguments
from datasets import load_dataset

# Modelo a entrenar
model_name = "t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)  
model = AutoModelForSeq2SeqLM.from_pretrained(model_name) 

# Carga de datos del entrenamiento
dataset = load_dataset("csv", data_files="train.csv")

# Funcion de tokenizacion
def tokenize_function(examples):
    inputs = tokenizer(examples["input"], padding="max_length", truncation=True, max_length=512)
    outputs = tokenizer(examples["output"], padding="max_length", truncation=True, max_length=128)
    return {
        # Diccionario de datos para el entrenamiento
        "input_ids": inputs["input_ids"],
        "attention_mask": inputs["attention_mask"],
        "labels": outputs["input_ids"]
    }

# Funcion de Tokens al dataset 
tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Define los argumentos del entrenamiento
training_args = Seq2SeqTrainingArguments(
    output_dir="fine_tuned_t5",
    per_device_train_batch_size=4,
    num_train_epochs=1,  
    fp16=True,
    save_steps=1000,
    logging_steps=100,
)

# Gestion del entrenamiento
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
)

# Inicia el entrenamiento
trainer.train()  # Model is automatically saved in output_dir
