document.addEventListener('DOMContentLoaded', () => {
    const recordButton = document.getElementById('recordButton');
    const exportButton = document.getElementById("exportBtn");

    const loadingIndicator = document.getElementById('loading-indicator');
    const listeningIndicator = document.getElementById('microphone-indicator')


    const statusDiv = document.getElementById('status');
    let mediaRecorder;
    let isRecording = false;
    const socket = io.connect(`${window.location.protocol}//${window.location.hostname}:${window.location.port}`);

    recordButton.addEventListener('click', () => {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            console.log("Record button clicked");
            if (!isRecording) {
                startRecording();
            } else {
                stopRecording();
            }
        } else {
            console.error('MediaDevices API not available');
            document.getElementById('mediaDevicesError').classList.remove('hidden');

        }
    });

    function startRecording() {
        // The API is available
        navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            console.log("Microphone access granted");
            listeningIndicator.classList.remove('hidden');

            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start(2000);

            console.log("Recording started");

            mediaRecorder.addEventListener('dataavailable', event => {
                console.log("Data available from recording");
                if (event.data.size > 0) {
                    socket.emit('audio_chunk', event.data);
                }
            });

            isRecording = true;
            recordButton.textContent = 'Stop Recording';
            statusDiv.textContent = 'Status: Recording';
            recordButton.classList.remove('bg-blue-500 hover:bg-blue-700')
            recordButton.classList.add('bg-red-500 hover:bg-red-700')
        })
        .catch(error => {
            console.error('Error accessing the microphone:', error);
            loadingIndicator.classList.add('hidden');
        });
    };

    function stopRecording() {

        mediaRecorder.stop();
        console.log("Recording stopped");

        isRecording = false
        recordButton.textContent = 'Start Recording';
        statusDiv.textContent = 'Status: Idle';

        listeningIndicator.classList.add('hidden');
        loadingIndicator.classList.remove('hidden');

        exportButton.disabled = false;
        exportButton.classList.remove('hidden');
    };

    socket.on('connect', function() {
        console.log('WebSocket connected');
    });

    socket.on('transcription', data => {
        // Update the transcription result on the page
        document.getElementById('transcriptionResult').textContent = 'Transcription: ' + data.text;
    });

/*
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

*/