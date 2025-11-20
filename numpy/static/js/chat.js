const messagesDiv = document.getElementById('chat-messages');
const input = document.getElementById('message-input');

input.addEventListener('keypress', e => {
    if (e.key === 'Enter') sendMessage();
});

function addMessage(text, type) {
    const div = document.createElement('div');
    div.className = `message ${type}`;
    div.textContent = text;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function sendMessage() {
    const question = input.value.trim();  
    if (!question) return;

    addMessage(question, 'user');
    input.value = ''; 

    const thinking = document.createElement('div');
    thinking.className = 'message bot thinking';
    thinking.textContent = 'Pensando 💭 ';
    messagesDiv.appendChild(thinking);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    const formData = new FormData();
    formData.append('question', question);

    fetch('/chat/process/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
        }
    })
    .then(r => r.json())
    .then(data => {
        thinking.remove();
        addMessage(data.answer || 'Hmm, não sei essa ainda…', 'bot');
    })
    .catch(err => {
        console.error(err);
        thinking.remove();
        addMessage('Ops, deu erro na conexão :(', 'bot');
    });
}