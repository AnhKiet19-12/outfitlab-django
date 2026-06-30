// ====================== CHATBOT + NAVBAR ======================

document.addEventListener('DOMContentLoaded', function() {

    // ==================== NAVBAR SCROLL ====================
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 80) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // ==================== CHATBOT (Chỉ khi đã đăng nhập) ====================
    const bubble = document.getElementById('chatbot-bubble');
    if (!bubble) return; // Không có bubble → không chạy chatbot

    const chatWindow = document.getElementById('chat-window');
    const closeBtn = document.getElementById('close-chat');
    const messagesContainer = document.getElementById('chat-messages');
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');

    bubble.addEventListener('click', async () => {
        chatWindow.style.display = 'flex';
        bubble.style.display = 'none';
        messagesContainer.innerHTML = '';

        try {
            const res = await fetch('/chatbot/', { credentials: 'include' });
            const data = await res.json();
            
            if (data.history && data.history.length > 0) {
                data.history.forEach(item => {
                    const msgText = item.message || '';
                    if (item.is_bot) addBotMessage(msgText);
                    else addUserMessage(msgText);
                });
            } else {
                addBotMessage("Chào bạn! 👋 Mình là Stylist AI. Hôm nay mình giúp bạn gì nào? 💖");
            }
        } catch(e) {
            console.error(e);
            addBotMessage("Chào bạn! Mình có thể hỗ trợ tư vấn phối đồ, size hay đơn hàng.");
        }
    });

    closeBtn.addEventListener('click', () => {
        chatWindow.style.display = 'none';
        bubble.style.display = 'flex';
    });

    function addMessage(text, type) {
        const safeText = (text || '').toString();
        const div = document.createElement('div');
        div.className = `message ${type}`;
        div.innerHTML = safeText.replace(/\n/g, '<br>');
        messagesContainer.appendChild(div);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function addBotMessage(text) { addMessage(text, 'bot'); }
    function addUserMessage(text) { addMessage(text, 'user'); }

    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        addUserMessage(text);
        input.value = '';

        const typingId = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.id = typingId;
        typingDiv.className = 'message bot';
        typingDiv.innerHTML = `<div class="typing-indicator"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>`;
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        try {
            const response = await fetch('/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                credentials: 'include',
                body: `message=${encodeURIComponent(text)}`
            });

            const data = await response.json();
            document.getElementById(typingId).remove();
            addBotMessage(data.response || "Mình chưa hiểu rõ, bạn nói thêm được không?");
        } catch (e) {
            console.error(e);
            document.getElementById(typingId).remove();
            addBotMessage("❌ Có lỗi kết nối. Bạn thử lại nhé!");
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', e => {
        if (e.key === 'Enter') sendMessage();
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

