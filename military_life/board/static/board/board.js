// board/static/board/board.js

document.addEventListener("DOMContentLoaded", () => {
    initBoardCategoryFilter();
});

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