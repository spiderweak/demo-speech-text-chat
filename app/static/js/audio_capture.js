document.addEventListener('DOMContentLoaded', () => {
    const recordButton = document.getElementById('recordButton');
    const sendButton = document.getElementById('sendButton')
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    const socket = io.connect(`${window.location.protocol}//${window.location.hostname}:${window.location.port}`);

    const chatInput = document.getElementById('chatInput');

    // Send button click event
    sendButton.addEventListener('click', sendMessage);

    // Enter key press event in the input field
    chatInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent the default action to stop from submitting the form
            sendMessage();
        }
    });

    chatInput.addEventListener('input', function() {
        adjustTextareaHeight(this);
    });

    recordButton.addEventListener('click', () => {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            console.log("Record button clicked");
            if (!isRecording) {
                startRecording();
            } else {
                stopRecording()
            }
        } else {
            console.error('MediaDevices API not available');
            displayErrorMessage('The MediaDevices API is not available in your browser.');
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
            recordButton.textContent = 'Stop';

            recordButton.classList.replace('bg-blue-500','bg-red-500');
            recordButton.classList.replace('hover:bg-blue-700', 'hover:bg-red-700');

        })
        .catch(error => {
            console.error('Error accessing the microphone:', error);
            displayErrorMessage('Error accessing the microphone');
        });
    };

    function stopRecording() {

        clearInterval(chunkInterval);
        if (mediaRecorder) {
            mediaRecorder.stop();
        }

        // Process and send any remaining audio chunks
        if (audioChunks.length > 0) {
            const finalAudioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            socket.emit('audio_chunk', finalAudioBlob);
            console.log(`Final audio blob emitted: size = ${finalAudioBlob.size}, type = ${finalAudioBlob.type}`);
        }
        // Clear the audioChunks array
        audioChunks = [];

        console.log("Recording stopped");

        isRecording = false
        recordButton.textContent = '🎙️';

        recordButton.classList.replace('bg-red-500', 'bg-blue-500');
        recordButton.classList.replace('hover:bg-red-700', 'hover:bg-blue-700');

        // Stop the media recorder
        if (mediaRecorder) {
            mediaRecorder.stop();
        }
    };

    function displayMessage(messageText, messageType) {
        var chatMessages = document.getElementById('chatMessages');
        var newMessageDiv = document.createElement('div');

        newMessageDiv.textContent = messageText;

        var baseClasses = ['p-2', 'my-2', 'rounded-lg', 'mr-auto'];
        var typeClasses = {
            'user': ['bg-blue-200', 'rounded-bl-lg', 'rounded-tl-lg', 'rounded-tr-lg', 'rounded-br-none', 'text-right'],
            'error': ['bg-red-200', 'rounded-lg', 'text-red-600'],
            'bot': ['bg-gray-200', 'rounded-tl-lg', 'rounded-tr-lg', 'rounded-br-lg', 'rounded-bl-none', 'text-black', 'rounded-br-lg', 'text-black']
        };

        newMessageDiv.classList.add(...baseClasses, ...typeClasses[messageType]);


        chatMessages.appendChild(newMessageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

    }

    function displayUserMessage(messageText) {
        displayMessage(messageText, 'user')
    }

    function displayErrorMessage(messageText) {
        displayMessage(messageText, 'error')
    }

    function displayBotMessage(messageText) {
        displayMessage(messageText, 'bot')
    }

    function sendMessage() {
        var message = chatInput.value.trim();
        if (message) {
            // Append the message to chatMessages div
            displayUserMessage(message)

            // Reset the input field
            chatInput.value = '';

            // Scroll to the bottom of the chat

            socket.emit('user_message', message);
        }
    }

    function adjustTextareaHeight(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }

    socket.on('connect', function() {
        console.log('WebSocket connected');
    });

    socket.on('transcription', data => {
        // Update the transcription result on the page
        chatInput.value = data.text;
        adjustTextareaHeight(chatInput)
        console.log(data.text)
    });

    socket.on('bot_message', data => {
        // Update the transcription result on the page
        displayBotMessage(data)
    });

});

