// Load configuration
const config = MERCURY_CONFIG;

let ws;
let wsReconnectTimer;

async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    if (!message) return;

    addMessage('user', message);
    input.value = '';

    const thinkingId = addMessage('assistant', 'Thinking...');

    try {
        const response = await fetch(`${config.PI_MIDDLEWARE_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        const data = await response.json();
        const replyElement = document.getElementById(thinkingId);
        if (replyElement) {
            replyElement.innerHTML = data.reply;
        }
    } catch (error) {
        const replyElement = document.getElementById(thinkingId);
        if (replyElement) {
            replyElement.textContent = 'Error: ' + error;
        }
    }
}

function addMessage(role, content) {
    const chatbox = document.getElementById('chatbox');
    const msgDiv = document.createElement('div');
    msgDiv.className = role;
    if (role === 'user') {
        msgDiv.textContent = content;
    } else {
        msgDiv.innerHTML = content;
    }
    if (role === 'assistant' && content === 'Thinking...') {
        msgDiv.id = 'msg-' + Date.now();
    }
    chatbox.appendChild(msgDiv);
    chatbox.scrollTop = chatbox.scrollHeight;
    return msgDiv.id || null;
}

function connectWebSocket() {
    ws = new WebSocket(config.REALTIME_WS_URL);

    ws.onopen = () => {
        console.log('Connected to real-time updates');
        if (wsReconnectTimer) {
            clearTimeout(wsReconnectTimer);
            wsReconnectTimer = null;
        }
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const alerts = document.getElementById('alerts');
        alerts.innerHTML += `<p><strong>Live Update:</strong> ${data.headlines.join(', ')}</p>`;
        alerts.scrollTop = alerts.scrollHeight;
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected, attempting reconnection...');
        wsReconnectTimer = setTimeout(connectWebSocket, 5000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        ws.close();
    };
}

// Initialize WebSocket connection
connectWebSocket();
