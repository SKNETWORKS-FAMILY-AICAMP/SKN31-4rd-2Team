// tests/board.spec.js
// TC-BRD-01 ~ TC-BRD-05
//
// board/post_list.html, post_detail.html, board.js 확인 완료.
//
// ⚠️ 신고 결과는 DOM 텍스트가 아니라 native alert()로 표시됩니다 (board.js: reportForm
// submit 핸들러). 그래서 getByText가 아니라 page.on('dialog', ...)로 처리합니다.
//
// ℹ️ 참고: board/views.py의 post_detail은 새로고침 시마다 view_count가 증가하는데,
// 이는 버그가 아니라 팀 확인된 의도된 동작입니다 (testcase.md "확인-001" 참고).

import { test, expect } from '@playwright/test';
import { loginAsTestUser } from './helpers/auth';

/** 게시판에 새 글을 하나 작성하고, 목록에 노출되는 것까지 확인하는 공용 헬퍼 */
async function createBoardPost(page, title) {
  await page.goto('/board/');

  await page.getByRole('button', { name: '글쓰기' }).click();
  await expect(page.locator('#createModal')).toBeVisible();

  // 카테고리는 Bootstrap btn-check 패턴(라디오가 숨겨져 있어 label을 클릭해야 함)
  await page.locator('label[for="cat_병영생활"]').click();
  await page.fill('#title', title);
  await page.fill('#content', 'Playwright 자동 테스트 내용입니다.');

  // 성공 시 board.js가 window.location.reload()를 호출함
  await page.locator('#createPostForm button[type="submit"]').click();

  await expect(page.getByText(title)).toBeVisible();
}

test.describe('TC-BRD-01: 게시글 목록 필터링/정렬', () => {
  test('카테고리 필터가 적용된다', async ({ page }) => {
    await loginAsTestUser(page);

    const response = await page.goto('/board/?category=휴가');
    expect(response.status()).toBe(200);

    // post_list.html: 각 게시글 카드의 카테고리는 .badge로 표시됨
    const categoryBadges = page.locator('.card .badge');
    const count = await categoryBadges.count();
    for (let i = 0; i < count; i++) {
      await expect(categoryBadges.nth(i)).toHaveText('휴가');
    }
  });

  test('인기순 정렬이 적용된다', async ({ page }) => {
    await loginAsTestUser(page);

    const response = await page.goto('/board/?sort=popular');
    expect(response.status()).toBe(200);
    await expect(page).toHaveURL(/sort=popular/);
    await expect(page.getByRole('button', { name: /인기순/ })).toBeVisible();
  });
});

test.describe('TC-BRD-02: 새 글 작성 및 익명성 보장', () => {
  test('글을 작성하면 목록/상세에 정상 등록되고 작성자 정보는 노출되지 않는다', async ({
    page,
  }) => {
    await loginAsTestUser(page);

    const uniqueTitle = `Playwright 테스트 게시글 ${Date.now()}`;
    await createBoardPost(page, uniqueTitle);

    await page.getByText(uniqueTitle).click();

    // post_detail.html: 작성자는 항상 "익명"으로만 표시됨
    // ⚠️ body 전체를 검사하면 navbar에 항상 떠 있는 로그인 사용자 아이디(base.html:
    // {{ user.username }})까지 걸려서 무조건 실패함 -> 본문 영역(main.page)으로 스코프를 좁힘
    const email = process.env.TEST_USER_EMAIL;
    await expect(page.locator('main.page')).not.toContainText(email);
    await expect(page.getByText('익명').first()).toBeVisible();
  });
});

test.describe('TC-BRD-03: 게시글 상세 및 상호작용', () => {
  test('조회수가 표시되고, 댓글 작성 및 좋아요가 동작한다', async ({ page }) => {
    await loginAsTestUser(page);

    const uniqueTitle = `Playwright 상호작용 테스트 ${Date.now()}`;
    await createBoardPost(page, uniqueTitle);
    await page.getByText(uniqueTitle).click();

    // 조회수 표시 (post_detail.html: bi-eye 아이콘 옆 숫자)
    await expect(page.locator('.bi-eye')).toBeVisible();

    // 댓글 작성 (post_detail.html: 일반 form POST, PRG 패턴 - Ajax 아님)
    const commentText = `Playwright 댓글 ${Date.now()}`;
    await page.fill('textarea[name="content"]', commentText);
    await page.locator('button[title="등록"]').click();

    await expect(page.getByText(commentText)).toBeVisible();

    // 좋아요 토글 (board.js: #likeBtn, #likeCount)
    const likeCountBefore = await page.locator('#likeCount').textContent();
    await page.locator('#likeBtn').click();
    await expect(page.locator('#likeCount')).not.toHaveText(likeCountBefore ?? '');

    // 다시 누르면 취소되어 원래 숫자로 돌아옴
    await page.locator('#likeBtn').click();
    await expect(page.locator('#likeCount')).toHaveText(likeCountBefore ?? '');
  });
});

test.describe('TC-BRD-04: 키워드 검색 기능', () => {
  test('검색어가 포함된 게시글만 조회된다', async ({ page }) => {
    await loginAsTestUser(page);

    const uniqueKeyword = `PWKeyword${Date.now()}`;
    await createBoardPost(page, `${uniqueKeyword} 검색 테스트 제목`);

    const response = await page.goto(`/board/?q=${uniqueKeyword}`);
    expect(response.status()).toBe(200);

    const titles = page.locator('.card-title');
    const count = await titles.count();
    expect(count).toBeGreaterThan(0);
    for (let i = 0; i < count; i++) {
      await expect(titles.nth(i)).toContainText(uniqueKeyword);
    }
  });
});

test.describe('TC-BRD-05: 부적절 게시글 신고', () => {
  test('신고 사유를 입력해 신고할 수 있고, 중복 신고는 차단된다', async ({ page }) => {
    await loginAsTestUser(page);

    const uniqueTitle = `Playwright 신고 테스트 ${Date.now()}`;
    await createBoardPost(page, uniqueTitle);
    await page.getByText(uniqueTitle).click();

    // ⚠️ 신고 결과는 DOM 텍스트가 아니라 native alert()로 표시됨
    let dialogMessage = '';
    page.once('dialog', async (dialog) => {
      dialogMessage = dialog.message();
      await dialog.accept();
    });

    await page.locator('#reportBtn').click();
    await expect(page.locator('#reportModal')).toBeVisible();
    await page.fill('#reason', 'Playwright 자동 테스트 신고 사유');
    await page.locator('#reportForm button[type="submit"]').click();

    await expect.poll(() => dialogMessage, { timeout: 5000 }).toContain('신고가 접수되었습니다');

    // 중복 신고 시도 -> 차단되어야 함 (board/views.py: 이미 신고한 경우 400 + 에러 메시지)
    // 성공 시 모달은 닫히지만 페이지가 새로고침되지는 않으므로 다시 열어 재시도
    page.once('dialog', async (dialog) => {
      dialogMessage = dialog.message();
      await dialog.accept();
    });

    await page.locator('#reportBtn').click();
    await page.fill('#reason', '중복 신고 테스트');
    await page.locator('#reportForm button[type="submit"]').click();

    await expect.poll(() => dialogMessage, { timeout: 5000 }).toContain('이미 신고한 게시글입니다');
  });
});