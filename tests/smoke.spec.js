// tests/smoke.spec.js
import { test, expect } from '@playwright/test';

test.describe('로그인 필요 페이지 → 미로그인 시 리다이렉트 확인', () => {
  const protectedPages = [
    '/records/',
    '/chatbot/',
    '/board/',
    '/account/update/',
    '/account/posts/',
  ];

  for (const url of protectedPages) {
    test(`${url} → 로그인 페이지로 리다이렉트`, async ({ page }) => {
      const response = await page.goto(url);
      expect(response.status()).not.toBe(404);
      expect(response.status()).not.toBe(500);
      await expect(page).toHaveURL(/\/account\/login/);
    });
  }
});