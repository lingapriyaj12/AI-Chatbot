document.addEventListener('DOMContentLoaded', function() {
    const chatIcon = document.getElementById('chat-icon');
    const chatBox = document.getElementById('chatbox');
    const closeButton = document.getElementById('close-chatbox');
    const messagesContainer = document.getElementById('messages');
    const chatInput = document.getElementById('chat-input');
    const sendMessageButton = document.getElementById('send-message');

    let messageHistory = [];

    chatIcon.addEventListener('click', function() {
        chatBox.style.display = 'block';
        addMessage('bot', "Hi Welcome to CMC, I'm here to guide you. Can you tell me who you are? A student, Job seeker, or Patient.");
        adjustChatboxPosition(); // Adjust chatbox position when opened
    });

    closeButton.addEventListener('click', function() {
        chatBox.style.display = 'none';
    });

    sendMessageButton.addEventListener('click', function() {
        sendMessage();
    });

    chatInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const message = chatInput.value.trim();
        if (message !== '') {
            sendMessageToBackend(message);
            messageHistory.push({ type: 'user', message });
            chatInput.value = '';
        }
    }

    function sendMessageToBackend(message) {
        const data = { message };
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            const botResponse = data.response;
            messageHistory.push({ type: 'bot', message: botResponse });
            displayMessages();
        })
        .catch(error => console.error('Error sending message:', error));
    }

    function displayMessages() {
        messagesContainer.innerHTML = '';
        messageHistory.forEach(item => {
            const messageElement = document.createElement('div');
            messageElement.classList.add(item.type === 'user' ? 'user-message' : 'bot-message');
            messageElement.innerHTML = item.message;
            messagesContainer.appendChild(messageElement);
        });
        scrollToBottom(); // Scroll to bottom when new message is displayed
        adjustChatboxPosition(); // Adjust chatbox position after displaying messages
    }

    function addMessage(type, message) {
        messageHistory.push({ type, message });
        displayMessages();
    }

    function adjustChatboxPosition() {
        const chatboxHeight = chatBox.clientHeight;
        const viewportHeight = window.innerHeight;
        const chatboxBottomPosition = chatBox.getBoundingClientRect().bottom;

        if (chatboxBottomPosition > viewportHeight) {
            chatBox.style.bottom = '0';
        } else {
            chatBox.style.bottom = '';
        }
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
});