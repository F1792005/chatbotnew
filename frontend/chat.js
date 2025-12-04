const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const suggestionsContainer = document.getElementById('suggestionsContainer');
const welcomeScreen = document.getElementById('welcomeScreen');

// Load suggestions on startup
async function loadSuggestions() {
    try {
        const response = await fetch('http://localhost:8000/suggestions');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        renderSuggestions(data.questions);
    } catch (error) {
        console.error('Error loading suggestions:', error);
        // Fallback suggestions if API fails
        renderSuggestions([
            "Nguyễn Hồng Phong là ai?",
            "Kinh nghiệm làm việc của Phong?",
            "Liên hệ với Phong như thế nào?",
            "Kỹ năng chính của Phong là gì?"
        ]);
    }
}

function renderSuggestions(questions) {
    suggestionsContainer.innerHTML = '';
    questions.forEach(q => {
        const chip = document.createElement('div');
        chip.className = 'suggestion-chip';
        chip.textContent = q;
        chip.onclick = () => {
            userInput.value = q;
            sendMessage();
        };
        suggestionsContainer.appendChild(chip);
    });
}

// Send message function
async function sendMessage() {
    const question = userInput.value.trim();
    if (!question) return;

    // Hide welcome screen if it's the first message
    if (welcomeScreen) {
        welcomeScreen.style.display = 'none';
    }

    // Add user message
    addMessage(question, 'user');
    userInput.value = '';

    // Show typing indicator
    showTypingIndicator();

    try {
        const response = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });

        // Hide typing indicator before showing response
        hideTypingIndicator();

        const data = await response.json();
        
        // Add bot response with thinking process if available
        addBotMessage(data.answer, data.thinking);

    } catch (error) {
        hideTypingIndicator();
        addMessage('Sorry, something went wrong. Please try again.', 'bot');
        console.error('Error:', error);
    }
}

function showTypingIndicator() {
    const indicatorDiv = document.createElement('div');
    indicatorDiv.className = 'message bot typing-indicator-container';
    indicatorDiv.id = 'typingIndicator';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'typing-indicator';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'typing-dot';
        contentDiv.appendChild(dot);
    }
    
    indicatorDiv.appendChild(contentDiv);
    chatMessages.appendChild(indicatorDiv);
    scrollToBottom();
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function addBotMessage(answer, thinking) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Add thinking process if exists
    if (thinking) {
        const thinkingProcess = document.createElement('div');
        thinkingProcess.className = 'thinking-process';
        
        const toggle = document.createElement('div');
        toggle.className = 'thinking-toggle';
        toggle.innerHTML = '<i class="fas fa-brain"></i> Thinking Process <i class="fas fa-chevron-down"></i>';
        
        const content = document.createElement('div');
        content.className = 'thinking-content';
        content.textContent = thinking;
        
        toggle.onclick = () => {
            content.classList.toggle('show');
            const icon = toggle.querySelector('.fa-chevron-down');
            icon.style.transform = content.classList.contains('show') ? 'rotate(180deg)' : 'rotate(0deg)';
        };
        
        thinkingProcess.appendChild(toggle);
        thinkingProcess.appendChild(content);
        contentDiv.appendChild(thinkingProcess);
    }

    // Add answer container for typewriter effect
    const answerContainer = document.createElement('div');
    contentDiv.appendChild(answerContainer);
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();

    // Typewriter effect for the answer
    typeWriter(answerContainer, answer);
}

function typeWriter(element, text, index = 0) {
    if (index < text.length) {
        element.textContent += text.charAt(index);
        scrollToBottom();
        setTimeout(() => typeWriter(element, text, index + 1), 10); // Adjust speed here
    }
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Initialize
loadSuggestions();
