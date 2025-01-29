FROM python:3.10-slim

WORKDIR /app

# Копируем файлы
COPY /app_stt/AdaOS_messgae_handler.py /app/AdaOS_messgae_handler.py
COPY /app_stt/AdaOS_StT_Class.py /app/AdaOS_StT_Class.py
COPY ./requirements.txt /app/requirements.txt 
COPY ./quantized_whisper_model.pth /app/quantized_whisper_model.pth

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg gcc python3-dev git && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости Python
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "AdaOS_messgae_handler.py"]
