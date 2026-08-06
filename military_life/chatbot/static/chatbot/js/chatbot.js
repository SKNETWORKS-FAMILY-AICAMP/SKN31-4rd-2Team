/* chatbot/static/chatbot/js/chatbot.js */

/* ==========================================
   Django에서 넘겨준 설정값 읽기
   (HTML의 #chatbot-config 스크립트 태그에서 가져옴)
=========================================== */

const CHATBOT_CONFIG = JSON.parse(
  document.getElementById("chatbot-config").textContent
);

const NEW_STREAM_URL = CHATBOT_CONFIG.newStreamUrl;
const STREAM_URL_TEMPLATE = CHATBOT_CONFIG.streamUrlTemplate;
const CONVERSATION_LIST_URL = CHATBOT_CONFIG.conversationListUrl;
const CONVERSATION_MESSAGES_TEMPLATE = CHATBOT_CONFIG.conversationMessagesTemplate;

/*
 * 삭제는 위 conversation-messages URL에 DELETE 요청을 보냅니다.
 * Django 백엔드에서도 같은 URL의 DELETE 메서드를 처리해야 합니다.
 */
const CONVERSATION_DELETE_TEMPLATE = CONVERSATION_MESSAGES_TEMPLATE;

const DUMMY_UUID = "00000000-0000-0000-0000-000000000000";

const BOT_PROFILE_IMAGE = CHATBOT_CONFIG.botProfileImage;

const WELCOME_MESSAGE = JSON.parse(
  document.getElementById("welcome-message-data").textContent
);


/* ==========================================
   기본 변수
=========================================== */

let conversationId = null;

const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("form");
const inputEl = document.getElementById("input");
const submitButtonEl = document.getElementById("submit-button");
const conversationListEl = document.getElementById("conversation-list");
const sidebarTabs = document.querySelectorAll(".sidebar-tab");
const sidebarPanels = document.querySelectorAll(".sidebar-panel");
const chatLayoutEl = document.querySelector(".chat-layout");
const sidebarToggleButton = document.getElementById("sidebar-toggle-button");
const sidebarOverlay = document.getElementById("sidebar-overlay");
const newChatButton = document.getElementById("new-chat-btn");


/* ==========================================
   Django CSRF 쿠키
=========================================== */

function getCookie(name) {
  const cookies = document.cookie ? document.cookie.split(";") : [];

  for (const cookie of cookies) {
    const trimmedCookie = cookie.trim();

    if (trimmedCookie.startsWith(`${name}=`)) {
      return decodeURIComponent(trimmedCookie.slice(name.length + 1));
    }
  }

  return "";
}


/* ==========================================
   현재 시간
=========================================== */

function getCurrentTimeText() {
  const now = new Date();
  const hours = now.getHours();
  const minutes = String(now.getMinutes()).padStart(2, "0");
  const period = hours < 12 ? "오전" : "오후";
  const displayHour = hours % 12 || 12;

  return `${period} ${displayHour}:${minutes}`;
}


/* ==========================================
   프로필 이미지 생성
=========================================== */

function createBotProfileImage(className = "bot-profile") {
  const profileImage = document.createElement("img");

  profileImage.className = className;
  profileImage.src = BOT_PROFILE_IMAGE;
  profileImage.alt = "박병장 프로필";

  profileImage.addEventListener("error", () => {
    profileImage.style.display = "none";
  });

  return profileImage;
}


/* ==========================================
   최초 인사 메시지
=========================================== */

function renderWelcomeMessage() {
  messagesEl.innerHTML = "";
  addAiBubble(WELCOME_MESSAGE, getCurrentTimeText());
}


/* ==========================================
   사용자 메시지 생성
=========================================== */

function addHumanBubble(text, timeText = getCurrentTimeText()) {
  const row = document.createElement("div");
  row.className = "message-row message-row--human";

  const content = document.createElement("div");
  content.className = "human-content";

  const meta = document.createElement("div");
  meta.className = "message-meta message-meta--human";
  meta.textContent = `나 · ${timeText}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble human";
  bubble.textContent = text;

  content.appendChild(meta);
  content.appendChild(bubble);
  row.appendChild(content);
  messagesEl.appendChild(row);

  scrollToLatestMessage();

  return bubble;
}


/* ==========================================
   AI 답변의 간단한 마크다운 표시
   #, ##, ### 헤딩과 **굵게**를 처리하며 HTML은 실행하지 않음
=========================================== */

function renderSimpleMarkdown(element, text) {
  element.replaceChildren();
  const source = text ?? "";
  const lines = source.split("\n");

  lines.forEach((line) => {
    const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const heading = document.createElement(`h${level}`);
      appendInlineBold(heading, headingMatch[2]);
      element.appendChild(heading);
    } else if (line.trim() === "") {
      element.appendChild(document.createElement("br"));
    } else {
      const p = document.createElement("p");
      appendInlineBold(p, line);
      element.appendChild(p);
    }
  });
}

function appendInlineBold(parent, text) {
  const boldPattern = /\*\*(.+?)\*\*/gs;
  let lastIndex = 0;
  let match;

  while ((match = boldPattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parent.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
    }
    const strong = document.createElement("strong");
    strong.textContent = match[1];
    parent.appendChild(strong);
    lastIndex = boldPattern.lastIndex;
  }

  if (lastIndex < text.length) {
    parent.appendChild(document.createTextNode(text.slice(lastIndex)));
  }
}


/* ==========================================
   AI 메시지 생성
=========================================== */

function addAiBubble(text = "", timeText = getCurrentTimeText()) {
  const row = document.createElement("div");
  row.className = "message-row message-row--ai";

  const profileImage = createBotProfileImage("bot-profile");

  const content = document.createElement("div");
  content.className = "ai-content";

  const meta = document.createElement("div");
  meta.className = "message-meta message-meta--ai";
  meta.textContent = `박병장 · ${timeText}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble ai";
  renderSimpleMarkdown(bubble, text);

  content.appendChild(meta);
  content.appendChild(bubble);
  row.appendChild(profileImage);
  row.appendChild(content);
  messagesEl.appendChild(row);

  scrollToLatestMessage();

  return bubble;
}


/* ==========================================
   검색 상태 표시
=========================================== */

function addStatus(text) {
  const row = document.createElement("div");
  row.className = "status-row";

  const profileImage = createBotProfileImage("status-profile");

  const status = document.createElement("div");
  status.className = "status";

  const spinner = document.createElement("span");
  spinner.className = "status-spinner";

  const statusText = document.createElement("span");
  statusText.textContent = text;

  status.appendChild(spinner);
  status.appendChild(statusText);
  row.appendChild(profileImage);
  row.appendChild(status);
  messagesEl.appendChild(row);

  scrollToLatestMessage();

  return row;
}


/* ==========================================
   최신 메시지로 스크롤
=========================================== */

function scrollToLatestMessage() {
  requestAnimationFrame(() => {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  });
}


/* ==========================================
   현재 대화 선택
=========================================== */

function setActiveConversation(id) {
  conversationId = id;

  document.querySelectorAll(".conversation-item").forEach((item) => {
    item.classList.toggle("active", item.dataset.id === id);
  });
}


/* ==========================================
   사이드바 대화 목록 렌더링
=========================================== */

function renderConversationList(conversations) {
  conversationListEl.innerHTML = "";

  if (!conversations || conversations.length === 0) {
    const emptyItem = document.createElement("li");
    emptyItem.className = "conversation-empty";
    emptyItem.textContent = "아직 저장된 대화가 없습니다.";
    conversationListEl.appendChild(emptyItem);
    return;
  }

  conversations.forEach((conv, index) => {
    const li = document.createElement("li");
    li.className = "conversation-item" + (conv.id === conversationId ? " active" : "");
    li.dataset.id = conv.id;

    const top = document.createElement("div");
    top.className = "conversation-item__top";

    const title = document.createElement("strong");
    title.className = "conversation-title";
    title.textContent = conv.title || "새 대화";

    const actions = document.createElement("div");
    actions.className = "conversation-item__actions";

    const date = document.createElement("span");
    date.className = "conversation-date";
    date.textContent = index === 0 ? "오늘" : "최근";

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "conversation-delete";
    deleteButton.dataset.conversationId = conv.id;
    deleteButton.setAttribute("aria-label", `${conv.title || "새 대화"} 삭제`);
    deleteButton.title = "대화 삭제";
    deleteButton.textContent = "✕";

    const preview = document.createElement("p");
    preview.className = "conversation-preview";
    preview.textContent =
      conv.preview || conv.last_message || "대화 내용을 확인하려면 클릭하세요.";

    actions.appendChild(date);
    actions.appendChild(deleteButton);
    top.appendChild(title);
    top.appendChild(actions);
    li.appendChild(top);
    li.appendChild(preview);

    conversationListEl.appendChild(li);
  });
}


/* ==========================================
   사이드바 목록 갱신
=========================================== */

async function refreshSidebar() {
  try {
    const response = await fetch(CONVERSATION_LIST_URL);

    if (!response.ok) {
      return;
    }

    const data = await response.json();
    renderConversationList(data.conversations || []);
  } catch (error) {
    console.error("대화 목록 불러오기 오류:", error);
  }
}


/* ==========================================
   대화 삭제
=========================================== */

async function deleteConversation(id) {
  const targetItem = conversationListEl.querySelector(
    `.conversation-item[data-id="${id}"]`
  );

  const title =
    targetItem?.querySelector(".conversation-title")?.textContent?.trim() || "이 대화";

  const shouldDelete = window.confirm(
    `"${title}" 대화를 삭제할까요?\n삭제한 대화는 복구할 수 없습니다.`
  );

  if (!shouldDelete) {
    return;
  }

  try {
    const response = await fetch(CONVERSATION_DELETE_TEMPLATE.replace(DUMMY_UUID, id), {
      method: "DELETE",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    if (!response.ok) {
      let detail = "";

      try {
        const data = await response.json();
        detail = data.message || data.detail || "";
      } catch (error) {
        detail = await response.text();
      }

      throw new Error(detail || `삭제 요청 실패: ${response.status}`);
    }

    if (conversationId === id) {
      conversationId = null;
      renderWelcomeMessage();
    }

    await refreshSidebar();
    inputEl.focus();
  } catch (error) {
    console.error("대화 삭제 오류:", error);

    window.alert(
      `대화를 삭제하지 못했습니다.\n${error.message}\n\n백엔드에서 해당 URL의 DELETE 요청을 처리하는지도 확인해 주세요.`
    );
  }
}


/* ==========================================
   기존 대화 불러오기
=========================================== */

async function loadConversation(id) {
  try {
    const response = await fetch(CONVERSATION_MESSAGES_TEMPLATE.replace(DUMMY_UUID, id));

    if (!response.ok) {
      throw new Error(`대화 불러오기 실패: ${response.status}`);
    }

    const data = await response.json();
    messagesEl.innerHTML = "";

    if (!data.messages || data.messages.length === 0) {
      renderWelcomeMessage();
    } else {
      for (const message of data.messages) {
        const role = message.role || message.type;

        if (role === "human" || role === "user") {
          addHumanBubble(message.content, message.time || getCurrentTimeText());
        } else {
          addAiBubble(message.content, message.time || getCurrentTimeText());
        }
      }
    }

    setActiveConversation(id);
    inputEl.focus();
  } catch (error) {
    console.error(error);
    messagesEl.innerHTML = "";
    addAiBubble(`[오류] ${error.message}`);
  }
}


/* ==========================================
   사이드바 대화 클릭
=========================================== */

conversationListEl.addEventListener("click", (event) => {
  const deleteButton = event.target.closest(".conversation-delete");

  if (deleteButton) {
    event.preventDefault();
    event.stopPropagation();

    const id =
      deleteButton.dataset.conversationId ||
      deleteButton.closest(".conversation-item")?.dataset.id;

    if (id) {
      deleteConversation(id);
    }

    return;
  }

  const item = event.target.closest(".conversation-item");

  if (!item || !item.dataset.id) {
    return;
  }

  loadConversation(item.dataset.id);

  if (window.matchMedia("(max-width: 760px)").matches) {
    setSidebarOpen(false);
  }
});


/* ==========================================
   전송 상태
=========================================== */

function setSubmitting(isSubmitting) {
  inputEl.disabled = isSubmitting;
  submitButtonEl.disabled = isSubmitting;
  submitButtonEl.classList.toggle("is-loading", isSubmitting);

  if (!isSubmitting) {
    inputEl.focus();
  }
}


/* ==========================================
   메시지 전송
=========================================== */

async function sendMessage(message) {
  const trimmedMessage = message.trim();

  if (!trimmedMessage || inputEl.disabled) {
    return;
  }

  inputEl.value = "";
  addHumanBubble(trimmedMessage);

  const aiBubble = addAiBubble("");

  let aiAnswerText = "";
  let statusEl = null;

  /*
   * conversationId가 null인 경우에만 새 대화 생성 URL을 사용합니다.
   * 한 번 생성된 뒤에는 같은 conversationId를 계속 사용하므로
   * 질문마다 최근 목록이 새로 생기지 않습니다.
   */
  const url = conversationId
    ? STREAM_URL_TEMPLATE.replace(DUMMY_UUID, conversationId)
    : NEW_STREAM_URL;

  setSubmitting(true);

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: trimmedMessage }),
    });

    if (!response.ok) {
      throw new Error(`서버 요청 실패: ${response.status}`);
    }

    if (!response.body) {
      throw new Error("서버에서 스트리밍 응답을 받지 못했습니다.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });

      const parts = buffer.split("\n\n");
      buffer = parts.pop() ?? "";

      for (const part of parts) {
        const lines = part.split("\n");

        for (const currentLine of lines) {
          const line = currentLine.trim();

          if (!line.startsWith("data:")) {
            continue;
          }

          let payload;

          try {
            payload = JSON.parse(line.slice(5).trim());
          } catch (error) {
            console.error("SSE JSON 파싱 오류:", error, line);
            continue;
          }

          if (payload.type === "meta") {
            setActiveConversation(payload.conversation_id);
          } else if (payload.type === "token") {
            aiAnswerText += payload.content ?? "";
            renderSimpleMarkdown(aiBubble, aiAnswerText);
          } else if (payload.type === "tool_start") {
            if (statusEl) {
              statusEl.remove();
            }

            statusEl = addStatus(`${payload.tool || "자료"} 검색 중...`);
          } else if (payload.type === "tool_end") {
            if (statusEl) {
              statusEl.remove();
              statusEl = null;
            }
          } else if (payload.type === "error") {
            aiAnswerText += `\n[오류] ${payload.message}`;
            renderSimpleMarkdown(aiBubble, aiAnswerText);
          } else if (payload.type === "done") {
            if (statusEl) {
              statusEl.remove();
              statusEl = null;
            }

            refreshSidebar();
          }

          scrollToLatestMessage();
        }
      }
    }

    if (!aiAnswerText.trim()) {
      aiAnswerText = "답변을 생성하지 못했습니다. 다시 질문해 주세요.";
      renderSimpleMarkdown(aiBubble, aiAnswerText);
    }
  } catch (error) {
    console.error(error);

    if (statusEl) {
      statusEl.remove();
      statusEl = null;
    }

    aiAnswerText = `[오류] ${error.message}`;
    renderSimpleMarkdown(aiBubble, aiAnswerText);
  } finally {
    setSubmitting(false);
    scrollToLatestMessage();
  }
}

formEl.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage(inputEl.value);
});


/* ==========================================
   새 채팅
=========================================== */

function startNewChat() {
  conversationId = null;

  document.querySelectorAll(".conversation-item").forEach((item) => {
    item.classList.remove("active");
  });

  renderWelcomeMessage();
  inputEl.value = "";
  inputEl.focus();

  /*
   * 빈 대화는 서버에 미리 만들지 않습니다.
   * 새 채팅에서 첫 메시지를 보낼 때 NEW_STREAM_URL을 호출해
   * 최근 목록에 한 번만 생성합니다.
   */
  if (window.matchMedia("(max-width: 760px)").matches) {
    setSidebarOpen(false);
  }
}

newChatButton.addEventListener("click", startNewChat);


/* ==========================================
   사이드바 열기 / 닫기
=========================================== */

function setSidebarOpen(isOpen) {
  chatLayoutEl.classList.toggle("sidebar-collapsed", !isOpen);

  sidebarToggleButton.setAttribute("aria-expanded", String(isOpen));
  sidebarToggleButton.setAttribute("aria-label", isOpen ? "사이드바 닫기" : "사이드바 열기");

  sidebarOverlay.classList.toggle("active", isOpen);
  sidebarOverlay.tabIndex = isOpen ? 0 : -1;
}

sidebarToggleButton.addEventListener("click", () => {
  const isCurrentlyOpen = !chatLayoutEl.classList.contains("sidebar-collapsed");
  setSidebarOpen(!isCurrentlyOpen);
});

sidebarOverlay.addEventListener("click", () => {
  setSidebarOpen(false);
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !chatLayoutEl.classList.contains("sidebar-collapsed")) {
    setSidebarOpen(false);
  }
});


/* ==========================================
   사이드바 탭 전환
=========================================== */

sidebarTabs.forEach((tabButton) => {
  tabButton.addEventListener("click", () => {
    const targetTab = tabButton.dataset.tab;

    sidebarTabs.forEach((button) => {
      button.classList.toggle("active", button === tabButton);
    });

    sidebarPanels.forEach((panel) => {
      panel.classList.toggle("active", panel.dataset.panel === targetTab);
    });
  });
});


/* ==========================================
   카테고리 펼치기 / 접기
=========================================== */

document.querySelectorAll(".category-title").forEach((titleButton) => {
  titleButton.addEventListener("click", () => {
    const group = titleButton.closest(".category-group");
    const isOpen = group.classList.toggle("open");
    titleButton.setAttribute("aria-expanded", String(isOpen));
  });
});


/* ==========================================
   카테고리 질문 클릭 시 바로 전송
=========================================== */

document.querySelectorAll(".category-question").forEach((questionButton) => {
  questionButton.addEventListener("click", () => {
    document.querySelectorAll(".category-question").forEach((button) => {
      button.classList.remove("active");
    });

    questionButton.classList.add("active");
    sendMessage(questionButton.textContent);
  });
});


/* ==========================================
   페이지 최초 실행
=========================================== */

renderWelcomeMessage();

setSidebarOpen(!window.matchMedia("(max-width: 760px)").matches);

inputEl.focus();