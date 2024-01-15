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

    function displayMessage(messageType, messageText, messageId = '0') {
        var chatMessages = document.getElementById('chatMessages');
        var newMessageDiv = document.createElement('div');

        newMessageDiv.setAttribute('data-message-id', messageId);

        newMessageDiv.textContent = messageText;

        var baseClasses = ['p-2', 'my-2', 'rounded-lg', 'mr-auto'];
        var typeClasses = {
            'user': ['bg-blue-200', 'rounded-bl-lg', 'rounded-tl-lg', 'rounded-tr-lg', 'rounded-br-none', 'text-right'],
            'error': ['bg-red-200', 'rounded-lg', 'text-red-600'],
            'debug': ['bg-green-200', 'rounded-lg', 'text-green-600'],
            'system': ['bg-gray-200', 'rounded-tl-lg', 'rounded-tr-lg', 'rounded-br-lg', 'rounded-bl-none', 'text-black', 'rounded-br-lg', 'text-black']
        };

        newMessageDiv.classList.add(...baseClasses, ...typeClasses[messageType]);

        // Make error messages clickable and dismissible
    if (messageType === 'error' || messageType === 'debug') {
        newMessageDiv.classList.add('clickable');
        newMessageDiv.addEventListener('click', function() {
            this.remove();  // Remove the message element when clicked
        });
    }

        chatMessages.appendChild(newMessageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

    }

    function appendMessage(messageType, messageText, messageId) {
        var existingMessage = chatMessages.querySelector(`[data-message-id="${messageId}"]`);

        if (existingMessage) {
            // If the message with this ID already exists, append new text
            existingMessage.textContent += messageText;
        } else {
            // If it does not exist, create a new message
            displayMessage(messageType, messageText, messageId);
        }

    }

    function sendMessage() {
        var message = chatInput.value.trim();
        if (message) {
            // Append the message to chatMessages div
            displayMessage("user", message)

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

    socket.on('message', data => {
        console.log(data)
        displayMessage(data.sender, data.content, data.message_id)
    });

    socket.on('stream_message', data => {
        // Handle the streamed chunk of data
        console.log('Received streamed chunk:', data);
        appendMessage(data.sender, data.content, data.message_id)
    });

});

