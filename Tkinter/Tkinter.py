import os
import requests
import customtkinter as ctk
from tkinter import filedialog, END
import pyaudio
import wave
import threading
from flask import Flask, request, jsonify
import queue
import json

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Interface")
        self.root.geometry("500x600")

        # Chat display
        self.chat_display = ctk.CTkTextbox(self.root, height=400, width=480, wrap="word")
        self.chat_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.chat_display.configure(state="disabled")

        # Message input
        self.message_entry = ctk.CTkEntry(self.root, width=350, placeholder_text="Enter your message")
        self.message_entry.grid(row=1, column=0, padx=10, pady=10)

        # Send button
        self.send_button = ctk.CTkButton(self.root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        # Upload audio button
        self.upload_button = ctk.CTkButton(self.root, text="Upload Audio", command=self.upload_audio)
        self.upload_button.grid(row=2, column=0, padx=10, pady=10)

        # Record audio button
        self.record_button = ctk.CTkButton(self.root, text="Record Audio", command=self.record_audio)
        self.record_button.grid(row=2, column=1, padx=10, pady=10)

        # Target address for sending text
        self.text_target_url = "http://127.0.0.1:5002/receive"  # Address for text messages
        self.audio_target_url = "http://127.0.0.1:5000/upload"  # Address for audio

        # Recording attributes
        self.is_recording = False
        self.recording_thread = None
        self.audio_frames = []

        # Queue for updating chat from server thread
        self.message_queue = queue.Queue()

        # Start Flask server
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()

        # Polling for messages from server
        self.poll_messages()

    def poll_messages(self):
        while not self.message_queue.empty():
            message = self.message_queue.get()
            self.update_chat(message)
        self.root.after(100, self.poll_messages)

    def send_message(self):
        message = self.message_entry.get()
        if not message.strip():
            self.update_chat("You: [Empty message]")
            return

        self.update_chat(f"You: {message}")

        try:
            response = requests.post(self.text_target_url, json={"message": message})
            print(response.json())
            if response.status_code == 200:
                server_response = response.json()
                
                self.update_chat(f"Server: {server_response.get('status', 'success')} - {server_response.get('message', '')}")
            else:
                self.update_chat(f"Server Error: {response.status_code}")
        except Exception as e:
            self.update_chat(f"Error: {str(e)}")

        self.message_entry.delete(0, END)

    def upload_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3;*.m4a")])
        if not file_path:
            self.update_chat("You: [No file selected]")
            return

        self.update_chat(f"You: Uploading file {os.path.basename(file_path)}...")

        try:
            with open(file_path, "rb") as audio_file:
                files = {"audio": (os.path.basename(file_path), audio_file)}
                response = requests.post(self.audio_target_url, files=files)
                if response.status_code == 200:
                    server_response = response.json()
                    self.update_chat(f"Server: {server_response.get('status', 'success')} - {server_response.get('text', '')}")
                else:
                    self.update_chat(f"Server Error: {response.status_code}")
        except Exception as e:
            self.update_chat(f"Error: {str(e)}")

    def record_audio(self):
        if not self.is_recording:
            self.is_recording = True
            self.audio_frames = []
            self.update_chat("You: Recording started...")
            self.recording_thread = threading.Thread(target=self._record_audio_thread)
            self.recording_thread.start()
        else:
            self.is_recording = False
            self.recording_thread.join()
            self.update_chat("You: Recording stopped. Saving file...")
            self._save_recorded_audio()

    def _record_audio_thread(self):
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 44100

        p = pyaudio.PyAudio()
        stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

        try:
            while self.is_recording:
                data = stream.read(chunk)
                self.audio_frames.append(data)
        except Exception as e:
            self.update_chat(f"Error during recording: {str(e)}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def _save_recorded_audio(self):
        file_path = "recorded_audio.wav"
        try:
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.audio_frames))

            self.update_chat(f"You: Recorded audio saved as {file_path}. Uploading...")
            self._upload_recorded_audio(file_path)
        except Exception as e:
            self.update_chat(f"Error during saving: {str(e)}")

    def _upload_recorded_audio(self, file_path):
        try:
            with open(file_path, "rb") as audio_file:
                files = {"audio": (os.path.basename(file_path), audio_file)}
                response = requests.post(self.audio_target_url, files=files)
                if response.status_code == 200:
                    server_response = response.json()
                    self.update_chat(f"Server: {server_response.get('status', 'success')} - {server_response.get('text', '')}")
                else:
                    self.update_chat(f"Server Error: {response.status_code}")
        except Exception as e:
            self.update_chat(f"Error: {str(e)}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def update_chat(self, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert(END, message + "\n")
        self.chat_display.see(END)
        self.chat_display.configure(state="disabled")

    def start_server(self):
        app = Flask(__name__)

        @app.route("/receive", methods=["POST"])
        def receive_message():
            
            data = request.json
            
            if "message" in data:
                self.message_queue.put(f"Received: {data['message']}")
                return jsonify({"status": "success"}), 200
            return jsonify({"error": "Invalid data"}), 400

        app.run(host="127.0.0.1", port=5001, debug=False)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Optional, can be "light"
    root = ctk.CTk()
    app = ChatApp(root)
    root.mainloop()