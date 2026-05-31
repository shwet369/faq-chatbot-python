const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const statusDiv = document.getElementById('status');

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    messageDiv.innerText = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('bot-message');
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = '<span class="loading"></span> Thinking...';
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTyping() {
    const typing = document.getElementById('typingIndicator');
    if (typing) typing.remove();
}

async function sendQuestion(question) {
    if (!question) {
        question = userInput.value.trim();
        if (!question) return;
        userInput.value = '';
        addMessage(question, 'user');
    } else {
        addMessage(question, 'user');
    }
    
    showTyping();
    statusDiv.textContent = '🤖 Getting answer...';
    
    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });
        
        const data = await response.json();
        hideTyping();
        addMessage(data.answer, 'bot');
        statusDiv.textContent = '✅ Ready to help!';
    } catch (error) {
        hideTyping();
        addMessage('⚠️ Sorry, I\'m having technical difficulties. Please try again later.', 'bot');
        statusDiv.textContent = '❌ Connection error';
        console.error('Error:', error);
    }
}

// Event listeners
sendBtn.addEventListener('click', () => sendQuestion());
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendQuestion();
});

// Quick question buttons
document.querySelectorAll('.quick-btn').forEach(btn => {
    btn.addEventListener('click', () => sendQuestion(btn.dataset.question));
});