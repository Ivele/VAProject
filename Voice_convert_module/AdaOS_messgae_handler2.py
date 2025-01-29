import os
import requests
from flask import Flask, request, jsonify
from AdaOS_StT_Class import Get_voice_message

app = Flask(__name__)
audio_processor = Get_voice_message(save_directory="output")

# Адреса 
TARGET_URLS = [
    "http://127.0.0.1:5001/receive",  
    "http://TEEESSSTTTTS.ru/listen"   
]

@app.route("/upload", methods=["POST"])
def upload_audio():
    print('start upload')

    if "audio" not in request.files:
        return jsonify({"error": "Файл не найден в запросе."}), 400

    audio_file = request.files["audio"]
    file_path = os.path.join("temp", audio_file.filename)
    os.makedirs("temp", exist_ok=True)
    audio_file.save(file_path)

    
    print("Обработка аудиофайла началась")

    try:
        text = audio_processor.process_audio(file_path)
        output_file = audio_processor.save_text(text, os.path.splitext(audio_file.filename)[0])

        
        responses = []
        for url in TARGET_URLS:
            try:
                print(text)
                response = requests.post(url, json={"text": text})
                responses.append({"url": url, "status_code": response.status_code, "response": response.text})
            except Exception as e:
                responses.append({"url": url, "error": str(e)})

        return jsonify({
            "message": "Файл обработан успешно.",
            "output_file": output_file,
            "responses": responses
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(file_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
