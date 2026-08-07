// tests/account.spec.js
// TC-ACC-01 (회원가입), TC-ACC-02 일부(로그아웃), TC-ACC-03 (정보수정/탈퇴), TC-ACC-04 (내가 쓴 글)
//
// account/signup.html, update.html, login.html, detail.html, base.html 확인 완료.
// TC-ACC-02의 "로그인" 부분은 tests/auth.spec.js에서 이미 검증하므로 여기서는 다루지 않습니다.

import { test, expect } from '@playwright/test';
import { loginAsTestUser, generateThrowawayUser, autoAcceptDialogs } from './helpers/auth';

test.describe('TC-ACC-01 / TC-ACC-03: 회원가입 → 정보 수정 → 탈퇴', () => {
  // 공용 로그인 테스트 계정(TEST_USER_EMAIL)은 다른 spec에서 계속 재사용해야 하므로,
  // 여기서는 매번 새로 만드는 "일회용 계정"으로 가입 → 수정 → 탈퇴까지 한 번에 검증합니다.
  test('회원가입 → 정보 수정(병사→간부) → 탈퇴까지 정상 동작한다', async ({ page }) => {
    // 탈퇴는 delete-form의 onsubmit에서 window.confirm()을 띄우므로 자동 수락 설정
    autoAcceptDialogs(page);

    const user = generateThrowawayUser();

    // 1) 회원가입 (TC-ACC-01) - account/signup.html 실제 필드 기준
    await page.goto('/account/signup/');

    await page.fill('input[name="username"]', user.username);
    await page.fill('input[name="email"]', user.email);
    await page.fill('input[name="password1"]', user.password);
    await page.fill('input[name="password2"]', user.password);
    await page.fill('input[name="enlist_date"]', '2025-01-01');

    // 신분/계급은 네이티브 radio가 커스텀 스타일로 숨겨져 있을 수 있어
    // 래핑된 label(.identity-option / .rank-option)을 직접 클릭합니다.
    await page.locator('.identity-option[data-identity="병사"]').click();
    await page.locator('.rank-option:has-text("이병")').click();

    await page.click('button[type="submit"]');

    // 가입 성공 시 자동 로그인되어 홈으로 이동 (account/views.py: signup_view)
    await expect(page).toHaveURL('/');

    // 2) 정보 수정 (TC-ACC-03) - account/update.html 기준, 병사 -> 간부로 변경해본다
    await page.goto('/account/update/');

    await page.locator('.identity-option[data-identity="간부"]').click();
    // officer_rank는 그룹화된 라디오라 정확한 계급명은 몰라도 첫 번째 옵션을 선택
    await page.locator('[data-rank-panel="간부"] .rank-option').first().click();

    await page.click('button[form="update-form"]');

    // 성공 토스트는 2초 후 자동으로 사라지므로(common.js) 지체 없이 확인
    await expect(page.locator('[data-toast]')).toContainText('회원 정보가 수정되었습니다', {
      timeout: 3000,
    });

    // 3) 탈퇴 (TC-ACC-03) - 별도 delete-form 제출, confirm()은 자동 수락됨
    await page.goto('/account/update/');
    await page.click('button[form="delete-form"]');

    // 탈퇴 후 홈으로 리다이렉트 (account/views.py: delete_account_view)
    await expect(page).toHaveURL('/');
    await expect(page.locator('[data-toast]')).toContainText('탈퇴가 완료되었습니다', {
      timeout: 3000,
    });
  });
});

test.describe('TC-ACC-02: 로그아웃', () => {
  test('로그인 후 로그아웃하면 세션이 파기되고 홈으로 이동한다', async ({ page }) => {
    await loginAsTestUser(page);

    // base.html: 로그아웃은 프로필 드롭다운이 아니라 navbar에 바로 노출된 링크
    await page.getByRole('link', { name: '로그아웃' }).click();

    await expect(page).toHaveURL('/');

    // 로그아웃 후 보호된 페이지 접근 시 로그인 페이지로 리다이렉트되는지 재확인
    await page.goto('/records/');
    await expect(page).toHaveURL(/\/account\/login/);
  });
});

test.describe('TC-ACC-04: 내가 쓴 글 조회', () => {
  test('마이페이지에서 내가 작성한 게시글 목록이 보인다', async ({ page }) => {
    await loginAsTestUser(page);

    const response = await page.goto('/account/posts/');
    expect(response.status()).toBe(200);

    // account/detail.html: 게시글 없으면 .empty-state, 있으면 .my-post-card 목록
    const postCount = await page.locator('.my-post-card').count();
    if (postCount === 0) {
      await expect(page.getByText('아직 작성한 게시글이 없습니다')).toBeVisible();
    } else {
      await expect(page.locator('.my-post-card').first()).toBeVisible();
    }
  });
});