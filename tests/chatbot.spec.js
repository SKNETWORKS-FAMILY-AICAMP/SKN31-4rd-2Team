// tests/chatbot.spec.js
// TC-CHAT-01 ~ TC-CHAT-04
//
// chat.html, chatbot.js 확인 완료.
//
// ⚠️ 주의: 이 테스트들은 실제 배포 서버의 챗봇(OpenAI API, Neo4j, Qdrant)을 그대로 호출합니다.
// 실행할 때마다 실제 API 비용이 발생하고 응답 시간도 깁니다 (수 초 ~ 수십 초).
// 매 push/PR마다 자동으로 돌리기보다는, 별도 워크플로우(workflow_dispatch)로 분리해서
// 필요할 때만 수동 실행하는 걸 권장합니다.
//
// ℹ️ 참고 (testcase.md "확인-002", "확인-003" 참고, 둘 다 버그 아님으로 팀 확인됨):
// - 출처는 별도 UI가 아니라 시스템 프롬프트 지시에 따라 답변 본문 끝에 포함됩니다.
// - FAQ 버튼도 일반 채팅과 동일하게 AI 스트리밍을 호출하는 게 의도된 설계입니다(즉답 아님).

import { test, expect } from '@playwright/test';
import { loginAsTestUser } from './helpers/auth';

test.describe('TC-CHAT-01: 자연어 질의응답 (SSE 스트리밍)', () => {
  test('질문을 입력하면 스트리밍으로 답변이 화면에 표시된다', async ({ page }) => {
    test.setTimeout(60_000);

    await loginAsTestUser(page);
    await page.goto('/chatbot/');

    await page.fill('#input', '연가는 1년에 며칠 나오나요?');

    const streamResponsePromise = page.waitForResponse(
      (res) => res.url().includes('/messages/stream/') && res.status() === 200,
      { timeout: 30_000 }
    );
    await page.click('#submit-button');
    await streamResponsePromise;

    // chatbot.js: AI 답변은 .bubble.ai 안에 마크다운으로 렌더링됨
    await expect(page.locator('.bubble.ai').last()).not.toBeEmpty({ timeout: 30_000 });
  });
});

test.describe('TC-CHAT-02: 출처 및 근거 노출', () => {
  test('답변 본문 안에 출처(법령/규정)가 함께 포함되어 표시된다', async ({ page }) => {
    test.setTimeout(60_000);

    await loginAsTestUser(page);
    await page.goto('/chatbot/');

    await page.fill('#input', '휴가 관련 규정 알려줘');
    const streamResponsePromise = page.waitForResponse(
      (res) => res.url().includes('/messages/stream/') && res.status() === 200,
      { timeout: 30_000 }
    );
    await page.click('#submit-button');
    await streamResponsePromise;

    const answerBubble = page.locator('.bubble.ai').last();
    await expect(answerBubble).not.toBeEmpty({ timeout: 30_000 });

    // 별도 출처 UI는 없고, 시스템 프롬프트 지시에 따라 답변 본문 끝에 출처가 포함됨.
    // 정확한 표기 형식은 AI가 생성하는 자유 텍스트라 완전히 고정돼 있지 않으므로,
    // 법령/조항을 가리키는 일반적인 패턴으로 포함 여부만 느슨하게 확인합니다.
    // ⚠️ LLM이 매번 조금씩 다르게 표현할 수 있어 이 검증은 가끔 flaky할 수 있습니다.
    // 재시도(retries)에서 통과하는 정도는 정상 범위로 보되, 계속 실패하면 시스템 프롬프트의
    // 실제 출처 표기 형식을 확인해서 정규식을 더 정확하게 좁혀주세요.
    const answerText = await answerBubble.innerText();
    expect(answerText).toMatch(/제\s?\d+\s?조|「.+법」|「.+령」|규정|훈령|예규|출처|근거/);
  });
});

test.describe('TC-CHAT-03: 대화 내역 저장 및 조회', () => {
  test('이전 대화가 사이드바 목록에 남고, 클릭하면 내용을 다시 불러온다', async ({ page }) => {
    test.setTimeout(60_000);

    await loginAsTestUser(page);
    await page.goto('/chatbot/');

    const uniqueQuestion = `테스트 질문 ${Date.now()}`;
    await page.fill('#input', uniqueQuestion);

    // ⚠️ waitForResponse로 잡는 스트리밍 POST 응답은 헤더가 도착한 시점(스트림 시작)일 뿐,
    // SSE 'done' 이벤트(스트림 완료 후 chatbot.js가 refreshSidebar()를 호출하는 시점)보다 훨씬 이름.
    // 그 사이에 새 채팅 버튼을 누르면 사이드바가 아직 갱신 전이라 새 대화를 못 찾음.
    // 그래서 refreshSidebar()가 실제로 호출하는 conversation-list GET 요청을 기다림.
    const sidebarRefreshPromise = page.waitForResponse(
      (res) =>
        res.request().method() === 'GET' &&
        new URL(res.url()).pathname === '/chatbot/conversations/' &&
        res.status() === 200
    );
    await page.click('#submit-button');
    await sidebarRefreshPromise;

    // 새 채팅으로 전환 후, 방금 만든 대화가 사이드바 목록에 있는지 확인
    // (chatbot.js: startNewChat -> refreshSidebar)
    await page.click('#new-chat-btn');

    const conversationItem = page.locator('.conversation-item').first();
    await expect(conversationItem).toBeVisible();

    await conversationItem.click();

    // 대화 내용(사용자 메시지)이 다시 로드되는지 확인 (chatbot.js: loadConversation)
    await expect(
      page.locator('.bubble.human').filter({ hasText: uniqueQuestion })
    ).toBeVisible();
  });
});

test.describe('TC-CHAT-04: FAQ 기능', () => {
  test('FAQ 버튼을 클릭하면 질문이 자동 전송되어 AI 답변이 스트리밍된다', async ({ page }) => {
    test.setTimeout(60_000);

    await loginAsTestUser(page);
    await page.goto('/chatbot/');

    // FAQ 질문은 사이드바의 "카테고리" 탭 안에 있음 (chat.html: .sidebar-tab[data-tab="category"])
    await page.locator('.sidebar-tab[data-tab="category"]').click();

    // 첫 번째 카테고리(휴가)는 기본적으로 펼쳐져 있어 바로 클릭 가능
    const faqButton = page.locator('.category-question').first();
    const questionText = (await faqButton.textContent())?.trim() ?? '';

    const streamResponsePromise = page.waitForResponse(
      (res) => res.url().includes('/messages/stream/') && res.status() === 200,
      { timeout: 30_000 }
    );
    await faqButton.click();
    await streamResponsePromise;

    // FAQ 질문 텍스트가 그대로 사용자 메시지로 전송되었는지 확인
    await expect(
      page.locator('.bubble.human').filter({ hasText: questionText })
    ).toBeVisible();

    // 일반 채팅과 동일하게 AI 스트리밍 답변이 표시됨 (즉답 UI는 없음 - 의도된 설계)
    await expect(page.locator('.bubble.ai').last()).not.toBeEmpty({ timeout: 30_000 });
  });
});