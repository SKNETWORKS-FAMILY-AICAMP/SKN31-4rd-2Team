/* ==========================================================
   진격의 박병장 - 공통 JS
   static/js/common.js (settings.STATICFILES_DIRS)
   ========================================================== */

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initModal();
    initProfileMenu();
    initToast();
});

/* ---------- 공통 탭 전환(개인기록 D-day/일지/목표, 챗봇 사이드바 최근/저장/카테고리) ---------- */
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

/* ---------- 공통 모달(게시판 글쓰기 등) ---------- */
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

/* ---------- 알림 토스트(닫기 버튼 + 자동 소멸) ---------- */
function initToast() {
    const dismiss = (toast) => {
        if (!toast || toast.classList.contains("app-toast--hide")) return;
        toast.classList.add("app-toast--hide");
        toast.addEventListener("animationend", () => toast.remove(), { once: true });
    };

    document.querySelectorAll("[data-toast]").forEach((toast) => {
        const closeBtn = toast.querySelector("[data-toast-close]");
        if (closeBtn) closeBtn.addEventListener("click", () => dismiss(toast));

        setTimeout(() => dismiss(toast), 4000);
    });
}

/* ---------- 네비게이션 프로필 드롭다운 ---------- */
function initProfileMenu() {
    const toggleBtn = document.getElementById("profile-menu-toggle");
    const dropdown = document.getElementById("profile-dropdown");
    if (!toggleBtn || !dropdown) return;

    toggleBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const isOpen = dropdown.style.display === "block";
        dropdown.style.display = isOpen ? "none" : "block";
    });

    // 드롭다운 내부 클릭은 닫히지 않도록
    dropdown.addEventListener("click", (e) => e.stopPropagation());

    // 바깥 클릭 시 닫기
    document.addEventListener("click", () => {
        dropdown.style.display = "none";
    });

    // ESC 키로 닫기
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") dropdown.style.display = "none";
    });
}