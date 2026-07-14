"use strict";

const state = {
  site: null,
  index: null,
  selectedDate: null,
  selectedCategory: "전체",
  query: "",
  dailyData: null,
};

const $ = (selector) => document.querySelector(selector);
const ACCESS_HASH = "158a323a7ba44870f23d96f1516dd70aa48e9a72db4ebb026b0a89e212a208ab";
const ACCESS_SESSION_KEY = "brickbot-faq-access";

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

async function sha256(value) {
  const data = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function unlockSite() {
  document.body.classList.remove("access-locked");
  $("#access-gate").hidden = true;
  $("#site-shell").hidden = false;
}

async function checkAccess(event) {
  event?.preventDefault();
  const input = $("#access-code");
  const error = $("#access-error");
  const hash = await sha256(input.value.trim());
  if (hash !== ACCESS_HASH) {
    error.textContent = "접속 코드가 올바르지 않습니다.";
    input.select();
    return;
  }
  sessionStorage.setItem(ACCESS_SESSION_KEY, "granted");
  error.textContent = "";
  unlockSite();
  init();
  $("#search").focus();
}

function appendLinkedText(container, text) {
  const urlPattern = /(https?:\/\/[^\s]+)/g;
  let cursor = 0;
  for (const match of text.matchAll(urlPattern)) {
    const start = match.index;
    if (start > cursor) container.append(document.createTextNode(text.slice(cursor, start)));
    const rawUrl = match[0];
    const trailing = rawUrl.match(/[),.;!?]+$/)?.[0] || "";
    const url = trailing ? rawUrl.slice(0, -trailing.length) : rawUrl;
    const link = el("a", "faq-link", url);
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    container.append(link);
    if (trailing) container.append(document.createTextNode(trailing));
    cursor = start + rawUrl.length;
  }
  if (cursor < text.length) container.append(document.createTextNode(text.slice(cursor)));
}

async function loadJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) throw new Error(`데이터를 불러오지 못했습니다: ${path}`);
  return response.json();
}

function routeDate() {
  const match = location.hash.match(/^#\/daily\/(\d{4}-\d{2}-\d{2})$/);
  return match ? match[1] : null;
}

function renderGuides() {
  const list = $("#guide-list");
  list.replaceChildren();
  state.site.guides.forEach((guide, index) => {
    const card = el("article", "guide-card");
    card.append(el("span", "guide-number", String(index + 1).padStart(2, "0")));
    card.append(el("h3", "", guide.title));
    card.append(el("p", "", guide.description));
    const badge = el("span", "meta-badge", guide.category);
    card.append(badge);
    list.append(card);
  });
}

function renderFilters() {
  const list = $("#filters");
  list.replaceChildren();
  state.site.categories.forEach((category) => {
    const button = el("button", "filter-button", category);
    button.type = "button";
    button.setAttribute("aria-pressed", String(category === state.selectedCategory));
    button.addEventListener("click", () => {
      state.selectedCategory = category;
      renderFilters();
      renderFaqs();
    });
    list.append(button);
  });
}

function filterFaqs(faqs) {
  const query = state.query.trim().toLocaleLowerCase("ko-KR");
  return faqs.filter((faq) => {
    const categoryMatch = state.selectedCategory === "전체" || faq.category === state.selectedCategory;
    const text = [faq.question, faq.answer, faq.category, ...(faq.tags || [])].join(" ").toLocaleLowerCase("ko-KR");
    return categoryMatch && (!query || text.includes(query));
  });
}

function renderDailySummary() {
  const box = $("#daily-summary");
  if (!state.dailyData) {
    box.hidden = true;
    box.replaceChildren();
    return;
  }
  box.hidden = false;
  box.replaceChildren();
  box.append(el("h3", "", `${state.dailyData.date} FAQ 요약본`));
  box.append(el("p", "", `집계: ${state.dailyData.period_start} ~ ${state.dailyData.period_end} KST`));
  box.append(el("p", "", state.dailyData.summary));
  const stats = el("div", "summary-stats");
  stats.append(el("span", "summary-stat", `FAQ ${state.dailyData.faqs.length}건`));
  stats.append(el("span", "summary-stat", `변경 ${state.dailyData.stats?.changes || 0}건`));
  stats.append(el("span", "summary-stat", `공개 제외 ${state.dailyData.stats?.excluded || 0}건`));
  box.append(stats);
}

function renderFaqs() {
  const list = $("#faq-list");
  const empty = $("#empty-state");
  list.replaceChildren();
  const allFaqs = state.dailyData?.faqs || [];
  const faqs = filterFaqs(allFaqs);
  $("#result-count").textContent = state.dailyData ? `검색 결과 ${faqs.length}건 · 전체 ${allFaqs.length}건` : "발행 대기 중";

  if (!state.dailyData || faqs.length === 0) {
    empty.hidden = false;
    empty.querySelector("h3").textContent = state.dailyData ? "조건에 맞는 FAQ가 없습니다." : "아직 발행된 FAQ가 없습니다.";
    empty.querySelector("p").textContent = state.dailyData ? "검색어나 카테고리를 바꿔보세요." : "첫 24시간 FAQ는 다음 정오에 업데이트됩니다.";
    return;
  }

  empty.hidden = true;
  faqs.forEach((faq, index) => {
    const card = el("details", "faq-card");
    const summary = el("summary");
    summary.append(el("span", "faq-index", `Q${String(index + 1).padStart(2, "0")}`));
    summary.append(el("span", "", faq.question));
    summary.append(el("span", "faq-toggle", "+"));
    card.append(summary);

    const answer = el("div", "faq-answer");
    const answerText = el("p");
    appendLinkedText(answerText, faq.answer);
    answer.append(answerText);
    const meta = el("div", "faq-meta");
    meta.append(el("span", "meta-badge", faq.category));
    meta.append(el("span", `meta-badge${faq.status === "검수 필요" ? " review" : ""}`, faq.status));
    meta.append(el("span", "meta-badge", `관련 대화 ${faq.source_count}건`));
    answer.append(meta);
    card.append(answer);
    list.append(card);
  });
}

function renderArchive() {
  const list = $("#archive-list");
  list.replaceChildren();
  if (!state.index.daily.length) {
    list.append(el("p", "", "첫 발행을 기다리고 있습니다."));
    return;
  }
  state.index.daily.forEach((day) => {
    const link = el("a", "archive-link");
    link.href = `#/daily/${day.date}`;
    link.append(el("span", "", `${day.date} FAQ 요약본`));
    link.append(el("span", "", `${day.faq_count}건 · ${day.period_start.slice(5)} ~ ${day.period_end.slice(5)}`));
    list.append(link);
  });
}

async function selectDay(date) {
  const target = date || state.index.daily[0]?.date || null;
  state.selectedDate = target;
  state.dailyData = target ? await loadJson(`./data/daily/${target}.json`) : null;
  state.query = "";
  state.selectedCategory = "전체";
  $("#search").value = "";
  renderFilters();
  renderDailySummary();
  renderFaqs();
  document.title = target ? `${target} FAQ 요약본 · 중등 강사진 FAQ` : "중등 강사진 FAQ";
}

async function handleRoute() {
  try {
    await selectDay(routeDate());
    if (routeDate()) $("#daily-section").scrollIntoView({ block: "start" });
  } catch (error) {
    console.error(error);
    state.dailyData = null;
    renderDailySummary();
    renderFaqs();
  }
}

async function init() {
  try {
    [state.site, state.index] = await Promise.all([
      loadJson("./data/site.json"),
      loadJson("./data/index.json"),
    ]);
    $("#subtitle").textContent = state.site.subtitle;
    $("#notice").textContent = state.site.notice;
    $("#schedule").textContent = state.site.schedule;
    renderGuides();
    renderArchive();
    renderFilters();
    await handleRoute();
  } catch (error) {
    console.error(error);
    $("#result-count").textContent = "데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.";
    $("#empty-state").hidden = false;
  }
}

$("#search").addEventListener("input", (event) => {
  state.query = event.target.value;
  renderFaqs();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "/" && document.activeElement !== $("#search")) {
    event.preventDefault();
    $("#search").focus();
  }
});

window.addEventListener("hashchange", handleRoute);
$("#access-form").addEventListener("submit", checkAccess);
if (sessionStorage.getItem(ACCESS_SESSION_KEY) === "granted") {
  unlockSite();
  init();
} else {
  $("#access-code").focus();
}
