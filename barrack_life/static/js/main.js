/* ==========================================================
   국방 도우미 - 공통 JS
   각 담당자는 TODO 부분에 실제 fetch/axios 통신 로직을 채워주세요.
   ========================================================== */

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initModal();
    initChatForm();
    initBoardCategoryFilter();
});

/* ---------- 공통 탭 전환 (개인기록 D-day/일지/목표, 챗봇 사이드바 최근/저장/카테고리) ---------- */
function initTabs() {
    document.querySelectorAll("[data-tabs]").forEach((tabGroup) => {
        const buttons = tabGroup.querySelectorAll(".tabs__item");
        const panelWrapId = tabGroup.dataset.tabs; // ex) data-tabs="records"

        buttons.forEach((btn) => {
            btn.addEventListener("click", () => {
                buttons.forEach((b) => b.classList.remove("active"));
                btn.classList.add("active");

                const target = btn.dataset.tabTarget;
                document
                    .querySelectorAll(`[data-tab-panel="${panelWrapId}"]`)
                    .forEach((panel) => {
                        panel.classList.toggle("active", panel.dataset.panelName === target);
                    });
            });
        });
    });
}

/* ---------- 공통 모달 (게시판 글쓰기 등) ---------- */
function initModal() {
    document.querySelectorAll("[data-modal-open]").forEach((openBtn) => {
        openBtn.addEventListener("click", () => {
            const modal = document.querySelector(openBtn.dataset.modalOpen);
            if (modal) modal.classList.add("active");
        });
    });

    document.querySelectorAll("[data-modal-close]").forEach((closeBtn) => {
        closeBtn.addEventListener("click", () => {
            const modal = closeBtn.closest(".modal-overlay");
            if (modal) modal.classList.remove("active");
        });
    });
}

/* ---------- 게시판 카테고리 필터 (휴가/징계/급여/전역/병영생활) ---------- */
function initBoardCategoryFilter() {
    const filterWrap = document.querySelector(".category-filter");
    if (!filterWrap) return;

    filterWrap.querySelectorAll(".category-filter__item").forEach((item) => {
        item.addEventListener("click", () => {
            filterWrap
                .querySelectorAll(".category-filter__item")
                .forEach((i) => i.classList.remove("active"));
            item.classList.add("active");

            // TODO(board팀): item.dataset.category 값으로 실제 게시글 필터링/API 요청
            console.log("선택된 카테고리:", item.dataset.category);
        });
    });
}

/* ---------- 챗봇 입력 폼 (박병장) ---------- */
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
        // fetch("/chatbot/api/message/", { method: "POST", ... })
        //     .then(res => res.json())
        //     .then(data => appendChatBubble(data.reply, "bot"));

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