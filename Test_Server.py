from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/message")
async def get_message(message: dict):
    user_message = message.get("text")
    # Здесь можно добавить логику обработки сообщения
    bot_response = f"Вы сказали: {user_message}"
    return JSONResponse(content={"response": bot_response})

@app.post("/api/voice")
async def upload_voice(file: UploadFile = File(...)):
    # Укажите путь для сохранения файла
    save_path = f"uploaded_files/{file.filename}"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)  # Создайте директорию, если ее нет

    # Сохранение файла
    with open(save_path, "wb") as f:
        content = await file.read()  # Читаем содержимое файла (асинхронно)
        f.write(content)  # Записываем содержимое в файл

    return JSONResponse(content={"response": "Аудио сообщение получено!", "filename": file.filename})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
