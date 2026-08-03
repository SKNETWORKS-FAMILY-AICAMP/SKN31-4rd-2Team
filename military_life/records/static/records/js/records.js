/* records/static/records/records.js */

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
    document.getElementById('modal-cancel-btn').addEventListener('click', closeModal);
    modal.addEventListener('click', function (event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    /* ---------- 새 목표 추가 폼 열기/닫기 ---------- */
    const addGoalBtn = document.getElementById('add-goal-btn');
    const goalForm = document.getElementById('goal-form');
    const cancelGoalBtn = document.getElementById('cancel-goal-btn');

    if (addGoalBtn && goalForm) {
        addGoalBtn.addEventListener('click', function () {
            goalForm.hidden = false;
            addGoalBtn.hidden = true;
        });
    }
    if (cancelGoalBtn && goalForm) {
        cancelGoalBtn.addEventListener('click', function () {
            goalForm.hidden = true;
            addGoalBtn.hidden = false;
        });
    }
});