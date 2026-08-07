// tests/helpers/auth.js
// 여러 spec 파일에서 재사용하는 헬퍼 함수

/**
 * 공용 테스트 계정(TEST_USER_EMAIL / TEST_USER_PASSWORD)으로 로그인합니다.
 * account/login.html의 필드명은 Django 기본 AuthenticationForm 그대로(username, password) 사용합니다.
 */
export async function loginAsTestUser(page) {
  const username = process.env.TEST_USER_EMAIL;
  const password = process.env.TEST_USER_PASSWORD;

  if (!username || !password) {
    throw new Error(
      'TEST_USER_EMAIL / TEST_USER_PASSWORD 환경변수가 설정되어 있지 않습니다. ' +
        'GitHub Actions Secrets 또는 로컬 .env를 확인해주세요.'
    );
  }

  await page.goto('/account/login/');
  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL('/');
}

/**
 * 회원가입/탈퇴 테스트용 "일회용" 계정 정보를 생성합니다.
 * 매 실행(재시도 포함)마다 유니크한 값을 만들어서, 운영 DB에 데이터가 남더라도
 * 서로 충돌하거나 공용 테스트 계정(TEST_USER_EMAIL)을 건드리지 않게 합니다.
 */
export function generateThrowawayUser() {
  const unique = `${Date.now()}_${Math.floor(Math.random() * 10000)}`;
  return {
    username: `pw_test_${unique}`,
    email: `pw_test_${unique}@example.com`,
    password: 'PlaywrightTest!2026',
  };
}

/**
 * 이후 발생하는 모든 브라우저 native dialog(confirm/alert)를 자동으로 수락합니다.
 * 탈퇴, 일정/목표 삭제, 신고 결과 알림 등은 DOM이 아니라 native dialog로 표시되므로 사용합니다.
 */
export function autoAcceptDialogs(page) {
  page.on('dialog', (dialog) => dialog.accept());
}