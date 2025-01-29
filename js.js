async function sendMessage() {
            let message = document.getElementById("message").value;
            if (!message) return;
            appendMessage("Вы: " + message);
            document.getElementById("message").value = "";
            
            let response = await fetch('http://127.0.0.1:8000/api/message', {
                
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: message })
            });
            console.log(JSON.stringify({ text: message }));
            console.log(response);
            let data = await response.json();
            appendMessage("Бот: " + data.response);
        }

        function appendMessage(text) {
            let chatBox = document.getElementById("chat-box");
            let div = document.createElement("div");
            div.classList.add("chat_message");
            div.textContent = text;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        let mediaRecorder;
        let audioChunks = [];
        
        async function startRecording() {
            let stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();
            mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
            mediaRecorder.onstop = async () => {
                let audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioChunks = [];
                let formData = new FormData();
                formData.append("file", audioBlob, "voice.wav");
                
                let response = await fetch('http://127.0.0.1:8000/api/voice', {
                    method: 'POST',
                    body: formData
                });
                let data = await response.json();
                appendMessage("Бот: " + data.response);
            };
            setTimeout(() => mediaRecorder.stop(), 5000);
        }