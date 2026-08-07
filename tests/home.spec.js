// tests/home.spec.js
// TC-HOME-01: 메인 대시보드 렌더링
//
// home/index.html 확인 완료.
//
// ℹ️ 참고: testcase.md의 TC-HOME-01 기대 결과에는 원래 "최근 작성한 개인기록 요약"과
// "커뮤니티 인기 게시글 랭킹"이 언급되어 있었지만, 실제 home/index.html에는 이 두 섹션이
// 존재하지 않습니다. 팀 확인 결과 기획상 없는 것이 맞아 testcase.md도 함께 수정했습니다
// (testcase.md "확인-004" 참고). 아래 테스트는 실제 화면에 존재하는 요소들만 검증합니다.

import { test, expect } from '@playwright/test';
import { loginAsTestUser } from './helpers/auth';

test.describe('TC-HOME-01: 홈 대시보드', () => {
  test('로그인 후 홈에 D-Day 카드, 챗봇 바로가기, 서비스 안내 카드가 표시된다', async ({
    page,
  }) => {
    await loginAsTestUser(page);

    const response = await page.goto('/');
    expect(response.status()).toBe(200);

    // 챗봇 상담 CTA 버튼 (home/index.html: hero__cta)
    await expect(page.getByRole('link', { name: '박병장에게 물어보기' })).toBeVisible();

    // D-Day 카드: enlist_date/discharge_date가 모두 있으면 D-Day 뱃지, 없으면 "전역일 미계산"
    const ddayBadge = page.locator('.hero__dday-badge');
    if ((await ddayBadge.count()) > 0) {
      await expect(ddayBadge).toHaveText(/D-\d+|D\+\d+/);
    } else {
      await expect(page.getByText('전역일 미계산')).toBeVisible();
    }

    // 서비스 안내 카드 3개 (챗봇 / 개인기록 / 게시판 바로가기)
    await expect(page.getByText('AI 챗봇 상담')).toBeVisible();
    await expect(page.getByText('개인 기록')).toBeVisible();
    await expect(page.getByText('익명 게시판')).toBeVisible();

    // 긴급 신고(국방헬프콜) 배너
    await expect(page.getByRole('link', { name: /1303/ })).toBeVisible();
  });

  test('비로그인 상태에서는 D-47 고정값이 표시된다', async ({ page }) => {
    // home/views.py: 비로그인 시 ddays=47, progress_percent=91 고정값 사용
    const response = await page.goto('/');
    expect(response.status()).toBe(200);
    await expect(page.locator('.hero__dday-badge')).toHaveText('D-47');
  });
});