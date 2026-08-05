/* ==========================================================
   진격의 박병장 - 공통 JS
   static/js/common.js (settings.STATICFILES_DIRS)
   ========================================================== */

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initModal();
    initProfileMenu();
    initToasts();
});

/* ---------- 토스트 알림 자동 사라짐 + 닫기 버튼 ---------- */
function initToasts() {
    document.querySelectorAll("[data-toast]").forEach((toast) => {
        toast.style.transition = "opacity .4s ease";

        const dismiss = () => {
            toast.style.opacity = "0";
            setTimeout(() => toast.remove(), 400);
        };

        // 자동 사라짐 (3초 후)
        const timer = setTimeout(dismiss, 2000);

        // 닫기 버튼 클릭 시 즉시 사라짐
        const closeBtn = toast.querySelector("[data-toast-close]");
        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                clearTimeout(timer);
                dismiss();
            });
        }
    });
}

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