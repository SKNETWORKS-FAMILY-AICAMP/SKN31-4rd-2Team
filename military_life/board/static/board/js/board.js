// Utility function to get CSRF token
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

document.addEventListener('DOMContentLoaded', () => {
    // --- Create Post Ajax ---
    const createForm = document.getElementById('createPostForm');
    if (createForm) {
        createForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            const category = this.querySelector('input[name="category"]:checked')?.value;
            const title = this.querySelector('input[name="title"]').value;
            const content = this.querySelector('textarea[name="content"]').value;

            if (!category) {
                alert('카테고리를 선택해주세요.');
                return;
            }

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ category, title, content })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        window.location.reload();
                    } else {
                        alert(data.message || '오류가 발생했습니다.');
                    }
                })
                .catch(err => {
                    console.error(err);
                    alert('서버와 통신 중 오류가 발생했습니다.');
                });
        });
    }

    // --- Update Post Ajax ---
    const updateForm = document.getElementById('updatePostForm');
    if (updateForm) {
        updateForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            const title = this.querySelector('input[name="title"]').value;
            const content = this.querySelector('textarea[name="content"]').value;

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ title, content })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        window.location.reload();
                    } else {
                        alert(data.message || '오류가 발생했습니다.');
                    }
                })
                .catch(err => {
                    console.error(err);
                    alert('서버와 통신 중 오류가 발생했습니다.');
                });
        });
    }

    // --- Like Toggle Ajax ---
    const likeBtn = document.getElementById('likeBtn');
    if (likeBtn) {
        likeBtn.addEventListener('click', function () {
            const url = this.getAttribute('data-url');

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        const icon = this.querySelector('i');
                        const countSpan = document.getElementById('likeCount');

                        if (data.liked) {
                            this.classList.remove('btn-secondary', 'text-dark');
                            this.classList.add('btn-primary', 'text-white');
                            icon.classList.remove('fa-regular');
                            icon.classList.add('fa-solid');
                        } else {
                            this.classList.remove('btn-primary', 'text-white');
                            this.classList.add('btn-secondary', 'text-dark');
                            icon.classList.remove('fa-solid');
                            icon.classList.add('fa-regular');
                        }
                        countSpan.textContent = data.likes_count;
                    }
                })
                .catch(err => console.error(err));
        });
    }

    // --- Report Post Ajax ---
    const reportForm = document.getElementById('reportForm');
    if (reportForm) {
        reportForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            const reason = this.querySelector('textarea[name="reason"]').value;

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ reason })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('신고가 접수되었습니다.');

                        // 신고 버튼 아이콘 색상 변경
                        const reportBtn = document.getElementById('reportBtn');
                        if (reportBtn) {
                            const icon = reportBtn.querySelector('i');
                            if (icon) {
                                icon.classList.remove('text-secondary');
                                icon.classList.add('text-danger');
                            }
                        }

                        // Close Bootstrap modal
                        const modalEl = document.getElementById('reportModal');
                        const modal = bootstrap.Modal.getInstance(modalEl);
                        if (modal) modal.hide();
                        this.reset();
                    } else {
                        alert(data.message || '오류가 발생했습니다.');
                    }
                })
                .catch(err => {
                    console.error(err);
                    alert('서버와 통신 중 오류가 발생했습니다.');
                });
        });
    }

    // Initialize Board Category Filter
    initBoardCategoryFilter();
});

// 사용자가 뒤로가기 버튼으로 목록에 돌아왔을 때, 캐시된 과거 화면 대신 최신 정보를 보여주도록 강제 새로고침
window.addEventListener('pageshow', function (event) {
    if (event.persisted) {
        window.location.reload();
    }
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
