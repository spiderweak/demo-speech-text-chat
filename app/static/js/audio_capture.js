document.addEventListener('DOMContentLoaded', () => {
    const recordButton = document.getElementById('recordButton');
    const exportButton = document.getElementById("exportBtn");

    const loadingIndicator = document.getElementById('loading-indicator');

    const statusDiv = document.getElementById('status');
    let mediaRecorder;
    let audioChunks = [];
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

            mediaRecorder = new MediaRecorder(stream);

            console.log("Recording started");


            mediaRecorder.ondataavailable = event => {
                console.log(`Chunk received: size = ${event.data.size}, type = ${event.data.type}`);
                audioChunks.push(event.data);
            };
            mediaRecorder.start();

            chunkInterval = setInterval(() => {
                if (audioChunks.length > 0) {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    socket.emit('audio_chunk', audioBlob);
                    console.log(`Emitting audio blob: size = ${audioBlob.size}, type = ${audioBlob.type}`);
                }
                audioChunks = [];
                mediaRecorder.stop();
                mediaRecorder.start();
            }, 3000);

            isRecording = true;
            recordButton.textContent = 'Stop Recording';
            statusDiv.textContent = 'Status: Recording';

            recordButton.classList.replace('bg-blue-500','bg-red-500');
            recordButton.classList.replace('hover:bg-blue-700', 'hover:bg-red-700');

            statusDiv.classList.replace('bg-orange-100', 'bg-green-100');
            statusDiv.classList.replace('text-orange-800', 'text-green-800');

            loadingIndicator.classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error accessing the microphone:', error);
            loadingIndicator.classList.add('hidden');
        });
    };

    function stopRecording() {

        clearInterval(chunkInterval);
        if (mediaRecorder) {
            mediaRecorder.stop();
        }
        console.log("Recording stopped");

        isRecording = false
        recordButton.textContent = 'Start Recording';
        statusDiv.textContent = 'Status: Idle';

        recordButton.classList.replace('bg-red-500', 'bg-blue-500');
        recordButton.classList.replace('hover:bg-red-700', 'hover:bg-blue-700');

        statusDiv.classList.replace('bg-green-100', 'bg-orange-100')
        statusDiv.classList.replace('text-green-800', 'text-orange-800');

        loadingIndicator.classList.add('hidden');

        exportButton.disabled = false;
        exportButton.classList.remove('hidden');
    };

    socket.on('connect', function() {
        console.log('WebSocket connected');
    });

    socket.on('transcription', data => {
        // Update the transcription result on the page
        document.getElementById('transcriptionResult').textContent = data.text;
    });

});
