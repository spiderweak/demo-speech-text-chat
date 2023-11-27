document.addEventListener('DOMContentLoaded', () => {
    const recordButton = document.getElementById('recordButton');
    const stopButton = document.getElementById('stopButton');
    const exportButton = document.getElementById("exportBtn");

    const loadingIndicator = document.getElementById('loading-indicator');
    const listeningIndicator = document.getElementById('microphone-indicator')

    let mediaRecorder;
    let audioChunks = [];

    recordButton.addEventListener('click', () => {
        console.log("Record button clicked");

        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            // The API is available
            listeningIndicator.classList.remove('hidden');
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    console.log("Microphone access granted");

                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.start();

                    console.log("Recording started");

                    mediaRecorder.addEventListener('dataavailable', event => {
                        console.log("Data available from recording");
                        audioChunks.push(event.data);
                    });

                    stopButton.disabled = false;
                    recordButton.disabled = true;

                    mediaRecorder.addEventListener('stop', () => {
                        console.log("Recording stopped");
                        listeningIndicator.classList.add('hidden');
                        loadingIndicator.classList.remove('hidden');

                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        console.log("Audio Blob created", audioBlob);
                        audioChunks = [];

                        sendAudioToServer(audioBlob);

                        stopButton.disabled = true;
                        recordButton.disabled = false;
                        exportButton.disabled = false;
                        exportButton.classList.remove('hidden');
                    });
                })
                .catch(error => {
                    console.error('Error accessing the microphone:', error);
                    loadingIndicator.classList.add('hidden');
                });
        } else {
            console.error('MediaDevices API not available');
            document.getElementById('mediaDevicesError').classList.remove('hidden');
        }
    });

    stopButton.addEventListener('click', () => {
        console.log("Stop button clicked");
        mediaRecorder.stop();
    });
});

function sendAudioToServer(audioBlob) {
    console.log("Sending audio to server");
    const loadingIndicator = document.getElementById('loading-indicator');

    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');

    fetch('/upload-audio', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("Server response:", data);
        document.getElementById('transcriptionResult').textContent = data.transcription || 'No transcription available';
        loadingIndicator.classList.add('hidden');
    })
    .catch(error => {
        console.error("Error sending audio to server:", error);
        loadingIndicator.classList.add('hidden');
    });
}

