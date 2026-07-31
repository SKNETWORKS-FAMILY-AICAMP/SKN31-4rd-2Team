/* ==========================================================
   진격의 박병장 - 공통 JS
   static/js/common.js (settings.STATICFILES_DIRS)
   ========================================================== */

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initModal();
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