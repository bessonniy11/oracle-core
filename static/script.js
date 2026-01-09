// static/script.js

/**
 * Отправляет сообщение пользователя на бэкенд и обновляет UI с ответом ассистента.
 */
async function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();

    if (message === '') return; // Игнорируем пустые сообщения

    addMessageToChat(message, 'user'); // Добавляем сообщение пользователя в чат
    userInput.value = ''; // Очищаем поле ввода

    showTypingIndicator(); // Показываем индикатор набора текста

    try {
        // Отправляем сообщение на бэкенд
        const response = await fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Произошла ошибка на сервере');
        }

        const data = await response.json();
        addMessageToChat(data.response, 'assistant'); // Добавляем ответ ассистента в чат

    } catch (error) {
        console.error('Ошибка при отправке сообщения:', error);
        addMessageToChat(`Ошибка: ${error.message}`, 'assistant error'); // Отображаем ошибку в чате
    } finally {
        removeTypingIndicator(); // Скрываем индикатор набора текста
    }
}

/**
 * Добавляет новое сообщение в область чата.
 * @param {string} text - Текст сообщения.
 * @param {string} sender - Отправитель сообщения ('user' или 'assistant').
 */
function addMessageToChat(text, sender) {
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);

    const bubbleElement = document.createElement('div');
    bubbleElement.classList.add('message-bubble');
    bubbleElement.textContent = text;

    messageElement.appendChild(bubbleElement);
    chatMessages.appendChild(messageElement);

    // Прокручиваем чат вниз, чтобы видеть новые сообщения
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Показывает индикатор набора текста (три мигающие точки) в чате.
 */
function showTypingIndicator() {
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicatorElement = document.createElement('div');
    typingIndicatorElement.classList.add('message', 'assistant', 'typing-indicator');
    typingIndicatorElement.innerHTML = `
        <div class="message-bubble">
            <span>.</span><span>.</span><span>.</span>
        </div>
    `;
    chatMessages.appendChild(typingIndicatorElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Удаляет индикатор набора текста из чата.
 */
function removeTypingIndicator() {
    const typingIndicatorElement = document.querySelector('.typing-indicator');
    if (typingIndicatorElement) {
        typingIndicatorElement.remove();
    }
}

// Обработчик события для кнопки отправки
document.getElementById('send-button').addEventListener('click', sendMessage);

// Обработчик события для нажатия Enter в поле ввода
document.getElementById('user-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
