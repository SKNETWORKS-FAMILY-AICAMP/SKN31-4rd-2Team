// tests/auth.spec.js
import { test, expect } from '@playwright/test';

const TEST_USER_EMAIL = process.env.TEST_USER_EMAIL;
const TEST_USER_PASSWORD = process.env.TEST_USER_PASSWORD;

test.describe('로그인 플로우', () => {
  test('로그인 성공 시 홈으로 이동', async ({ page }) => {
    await page.goto('/account/login/');

    await page.fill('input[name="username"]', TEST_USER_EMAIL);
    await page.fill('input[name="password"]', TEST_USER_PASSWORD);
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/');
  });

  test('잘못된 비밀번호로 로그인 실패', async ({ page }) => {
    await page.goto('/account/login/');

    await page.fill('input[name="username"]', TEST_USER_EMAIL);
    await page.fill('input[name="password"]', 'wrong-password-123');
    await page.click('button[type="submit"]');

    // 로그인 실패 시 로그인 페이지에 그대로 남아있어야 함
    await expect(page).toHaveURL(/\/account\/login/);
  });
});