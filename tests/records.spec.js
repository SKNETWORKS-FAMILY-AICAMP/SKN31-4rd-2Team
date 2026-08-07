// tests/records.spec.js
// TC-REC-01 (일지 CRUD), TC-REC-02 (디데이 및 캘린더)
//
// records/records.html, records.js 확인 완료.
// 일지 작성/수정은 캘린더 날짜 칸을 클릭해 모달을 여는 방식이고, 실제 제출값은
// hidden input(entry-date-input 등)에 JS가 채워주는 구조입니다.
// 삭제(일정/전역일 수정 없음)는 window.confirm()을 사용하므로 자동 수락 처리했습니다.

import { test, expect } from '@playwright/test';
import { loginAsTestUser, autoAcceptDialogs } from './helpers/auth';

test.describe('TC-REC-01: 군 생활 일지 CRUD', () => {
  test('일지를 작성하고, 수정하고, 삭제할 수 있다', async ({ page }) => {
    autoAcceptDialogs(page); // 삭제 시 window.confirm() 자동 수락

    await loginAsTestUser(page);
    await page.goto('/records/?tab=calendar');

    const todayDay = String(new Date().getDate());
    const todayCell = page.locator(`.calendar-day[data-day="${todayDay}"]`);

    // 1) 작성 - 오늘 날짜 칸을 클릭하면 모달이 열림 (records.js: openModal)
    await todayCell.click();
    await expect(page.locator('#journal-modal')).toBeVisible();

    await page.locator('.type-btn[data-value="일반"]').click();
    await page.locator('.mood-btn[data-value="행복"]').click();
    await page.fill('#content-input', 'Playwright 자동 테스트 일지입니다.');
    await page.locator('#journal-form button[value="save"]').click();

    await expect(page).toHaveURL(/tab=calendar/);
    // JournalEntry는 update_or_create라 처음 작성/수정 상관없이 메시지가 동일함
    await expect(page.locator('[data-toast]')).toContainText('일정을 저장했습니다', {
      timeout: 3000,
    });
    await expect(todayCell.locator('.tag-일반')).toBeVisible();

    // 2) 수정 - 같은 날짜를 다시 클릭 (이번엔 삭제 버튼도 노출되어야 함)
    await todayCell.click();
    await expect(page.locator('#modal-delete-btn')).toBeVisible();

    await page.locator('.type-btn[data-value="외출"]').click();
    await page.fill('#content-input', 'Playwright 자동 테스트 - 수정됨');
    await page.locator('#journal-form button[value="save"]').click();

    await expect(page.locator('[data-toast]')).toContainText('일정을 저장했습니다', {
      timeout: 3000,
    });
    await expect(todayCell.locator('.tag-외출')).toBeVisible();

    // 3) 삭제
    await todayCell.click();
    await page.locator('#modal-delete-btn').click(); // window.confirm() 자동 수락됨

    await expect(page.locator('[data-toast]')).toContainText('일정을 삭제했습니다', {
      timeout: 3000,
    });
    await expect(todayCell.locator('.tag-일반, .tag-외출')).toHaveCount(0);
  });
});

test.describe('TC-REC-02: 디데이 및 캘린더', () => {
  test('간부 계정이라면 전역 예정일을 수정하면 D-Day가 갱신된다', async ({ page }) => {
    await loginAsTestUser(page);
    await page.goto('/records/?tab=dday');

    const editBtn = page.locator('#edit-discharge-btn');

    // 전역일 수정 UI는 간부(officer) 계정에서만 렌더링됨 (records/records.html 조건부 렌더링)
    // TEST_USER 계정이 병사라면 해당 사항이 없어 테스트를 건너뜁니다.
    if ((await editBtn.count()) === 0) {
      test.skip(true, 'TEST_USER 계정이 간부가 아니어서 전역일 수정 UI가 노출되지 않음');
    }

    await editBtn.click();
    await expect(page.locator('#discharge-date-form')).toBeVisible();

    const futureDate = new Date();
    futureDate.setMonth(futureDate.getMonth() + 6);
    const dischargeDate = futureDate.toISOString().slice(0, 10);

    await page.fill('#discharge-date-form input[name="discharge_date"]', dischargeDate);
    await page.locator('#discharge-date-form button[type="submit"]').click();

    await expect(page).toHaveURL(/tab=dday/);
    await expect(page.locator('[data-toast]')).toContainText('전역 예정일을 저장했습니다', {
      timeout: 3000,
    });
    await expect(page.getByText(/D-\d+/)).toBeVisible();
  });

  test('캘린더 화면에서 이전/다음 달로 이동할 수 있다', async ({ page }) => {
    await loginAsTestUser(page);

    const response = await page.goto('/records/?tab=calendar');
    expect(response.status()).toBe(200);

    // records/records.html: a.calendar-nav-btn (‹ / ›)
    const nextBtn = page.locator('a.calendar-nav-btn').last();
    await nextBtn.click();
    await expect(page).toHaveURL(/month=/);
  });
});