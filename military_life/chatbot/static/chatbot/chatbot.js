/* chatbot/static/chatbot/chatbot.js */

document.addEventListener("DOMContentLoaded", () => {
    initChatForm();
});

/* ---------- 챗봇 입력 폼 ---------- */
function initChatForm() {
    const form = document.getElementById("chat-form");
    if (!form) return;

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const input = document.getElementById("chat-input");
        const message = input.value.trim();
        if (!message) return;

        appendChatBubble(message, "user");
        input.value = "";

        // TODO(chatbot팀): 아래를 실제 백엔드 API 호출로 교체
ß
        appendChatBubble("(AI 응답 자리 - 실제 로직 연결 필요)", "bot");
    });
}

function appendChatBubble(text, type) {
    const messagesWrap = document.querySelector(".chat-messages");
    if (!messagesWrap) return;

    const bubble = document.createElement("div");
    bubble.className = `chat-bubble chat-bubble--${type}`;
    bubble.textContent = text;
    messagesWrap.appendChild(bubble);
    messagesWrap.scrollTop = messagesWrap.scrollHeight;
}