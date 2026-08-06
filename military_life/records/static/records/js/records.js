/* records/static/records/js/records.js */

document.addEventListener('DOMContentLoaded', function () {

    /* ---------- 탭 전환 (D-day / 캘린더 / 목표) ---------- */
    const tabButtons = document.querySelectorAll('.tab-btn');
    const panels = {
        dday: document.getElementById('panel-dday'),
        calendar: document.getElementById('panel-calendar'),
        goals: document.getElementById('panel-goals'),
    };

    function activateTab(tabName) {
        tabButtons.forEach(function (btn) {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        Object.keys(panels).forEach(function (key) {
            if (panels[key]) {
                panels[key].hidden = (key !== tabName);
            }
        });

        // 새로고침해도 같은 탭을 볼 수 있도록 주소창에 기록
        const url = new URL(window.location);
        url.searchParams.set('tab', tabName);
        window.history.replaceState({}, '', url);
    }

    tabButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            activateTab(btn.dataset.tab);
        });
    });

    /* ---------- 일정 기록 모달 ---------- */
    const modal = document.getElementById('journal-modal');
    const modalDate = document.getElementById('modal-date');
    const entryDateInput = document.getElementById('entry-date-input');
    const entryTypeInput = document.getElementById('entry-type-input');
    const moodInput = document.getElementById('mood-input');
    const contentInput = document.getElementById('content-input');
    const deleteBtn = document.getElementById('modal-delete-btn');

    const typeButtons = document.querySelectorAll('.type-btn');
    const moodButtons = document.querySelectorAll('.mood-btn');

    function setActiveButton(buttons, value) {
        buttons.forEach(function (btn) {
            btn.classList.toggle('active', btn.dataset.value === value);
        });
    }

    function openModal(dayCell) {
        const year = dayCell.dataset.year;
        const month = String(dayCell.dataset.month).padStart(2, '0');
        const day = String(dayCell.dataset.day).padStart(2, '0');
        const dateStr = year + '-' + month + '-' + day;

        const type = dayCell.dataset.type || '일반';
        const mood = dayCell.dataset.mood || '행복';

        modalDate.textContent = dateStr;
        entryDateInput.value = dateStr;
        entryTypeInput.value = type;
        moodInput.value = mood;
        contentInput.value = dayCell.dataset.content || '';

        setActiveButton(typeButtons, type);
        setActiveButton(moodButtons, mood);

        // 이미 저장된 기록이 있는 날짜에만 삭제 버튼 표시
        deleteBtn.hidden = dayCell.dataset.hasEntry !== 'true';

        modal.hidden = false;
    }

    function closeModal() {
        modal.hidden = true;
    }

    document.querySelectorAll('.calendar-day').forEach(function (dayCell) {
        dayCell.addEventListener('click', function () {
            openModal(dayCell);
        });
    });

    typeButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            setActiveButton(typeButtons, btn.dataset.value);
            entryTypeInput.value = btn.dataset.value;
        });
    });

    moodButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            setActiveButton(moodButtons, btn.dataset.value);
            moodInput.value = btn.dataset.value;
        });
    });

    document.getElementById('modal-close-btn').addEventListener('click', closeModal);
    modal.addEventListener('click', function (event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    deleteBtn.addEventListener('click', function (event) {
        if (!window.confirm('이 날짜의 기록을 삭제하시겠습니까?')) {
            event.preventDefault();
        }
    });

    /* ---------- 새 목표 추가 / 수정 모달 ---------- */
    const addGoalBtn = document.getElementById('add-goal-btn');
    const goalModal = document.getElementById('goal-modal');
    const goalModalCloseBtn = document.getElementById('goal-modal-close-btn');
    const goalModalTitle = document.getElementById('goal-modal-title');
    const goalIdInput = document.getElementById('goal-id-input');
    const goalDeleteBtn = document.getElementById('goal-delete-btn');
    const goalCategoryInput = document.getElementById('id_category');
    const goalTitleInput = document.getElementById('id_title');
    const goalTargetDateInput = document.getElementById('id_target_date');

    function openGoalModal() {
        goalModal.hidden = false;
    }

    function closeGoalModal() {
        goalModal.hidden = true;
    }

    function resetGoalForm() {
        goalModalTitle.textContent = '새 목표 추가';
        goalIdInput.value = '';
        goalCategoryInput.value = '';
        goalTitleInput.value = '';
        goalTargetDateInput.value = '';
        goalDeleteBtn.hidden = true;
    }

    function openGoalModalForEdit(card) {
        goalModalTitle.textContent = '목표 수정';
        goalIdInput.value = card.dataset.goalId;
        goalCategoryInput.value = card.dataset.category || '';
        goalTitleInput.value = card.dataset.title || '';
        goalTargetDateInput.value = card.dataset.targetDate || '';
        goalDeleteBtn.hidden = false;
        openGoalModal();
    }

    if (addGoalBtn && goalModal) {
        addGoalBtn.addEventListener('click', function () {
            resetGoalForm();
            openGoalModal();
        });
    }
    if (goalModalCloseBtn) {
        goalModalCloseBtn.addEventListener('click', closeGoalModal);
    }
    if (goalModal) {
        goalModal.addEventListener('click', function (event) {
            if (event.target === goalModal) {
                closeGoalModal();
            }
        });
    }
    if (goalDeleteBtn) {
        goalDeleteBtn.addEventListener('click', function (event) {
            if (!window.confirm('이 목표를 삭제하시겠습니까?')) {
                event.preventDefault();
            }
        });
    }

    document.querySelectorAll('.goal-card').forEach(function (card) {
        card.addEventListener('click', function () {
            openGoalModalForEdit(card);
        });
    });

    /* ---------- (간부) 전역 예정일 수정 토글 ---------- */
    const editDischargeBtn = document.getElementById('edit-discharge-btn');
    const dischargeDisplay = document.getElementById('discharge-display');
    const dischargeForm = document.getElementById('discharge-date-form');

    if (editDischargeBtn && dischargeForm) {
        editDischargeBtn.addEventListener('click', function () {
            dischargeForm.hidden = false;
            if (dischargeDisplay) {
                dischargeDisplay.hidden = true;
            }
        });
    }
});