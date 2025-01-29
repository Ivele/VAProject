import torch
import whisper
import os

class Get_voice_message:
    def __init__(self, save_directory, model_path="quantized_whisper_model.pth"):
        self.save_directory = save_directory
        os.makedirs(self.save_directory, exist_ok=True)
        model = whisper.load_model("turbo")
        model.load_state_dict(torch.load(model_path))
        self.model = model.eval()

    def process_audio(self, audio_path):
        result = self.model.transcribe(audio_path)
        return result["text"]

    def save_text(self, text, filename):
        file_path = os.path.join(self.save_directory, f"{filename}.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text)
        return file_path
