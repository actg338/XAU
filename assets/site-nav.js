"use strict";

const SITE_LANGUAGES = {
  "zh-CN": {prefix:"", labels:["首页","市场工具","新闻","EA 回测","免费 EA","安装教程"], language:"语言"},
  "zh-TW": {prefix:"zh-tw", labels:["首頁","市場工具","新聞","EA 回測","免費 EA","安裝教學"], language:"語言"},
  "en": {prefix:"en", labels:["Home","Market tools","News","Backtests","Free EA","Install"], language:"Language"},
  "ja": {prefix:"ja", labels:["ホーム","市場ツール","ニュース","バックテスト","無料 EA","導入方法"], language:"言語"},
  "ko": {prefix:"ko", labels:["홈","시장 도구","뉴스","백테스트","무료 EA","설치"], language:"언어"},
  "de": {prefix:"de", labels:["Start","Markttools","News","Backtests","Kostenlose EA","Installation"], language:"Sprache"},
  "fr": {prefix:"fr", labels:["Accueil","Outils marché","Actualités","Backtests","EA gratuit","Installation"], language:"Langue"}
};
const SITE_PAGES = ["","market-tools.html","news.html","huice.html","free-ea.html","ea-install.html"];

function currentLanguage() {
  const value = document.documentElement.lang;
  return SITE_LANGUAGES[value] || SITE_LANGUAGES.en;
}

function pageUrl(prefix, page) {
  const directory = prefix ? `/${prefix}/` : "/";
  return page ? `${directory}${page}` : directory;
}

function currentPage() {
  const name = location.pathname.split("/").filter(Boolean).pop() || "";
  return name === "index.html" ? "" : name;
}

function linkNode(label, href, selected) {
  const link = document.createElement("a");
  link.className = "site-core-nav__link";
  link.href = href;
  link.textContent = label;
  if (selected) link.setAttribute("aria-current", "page");
  return link;
}

function languageNode(page, currentPrefix, label) {
  const select = document.createElement("select");
  select.className = "site-core-nav__language";
  select.setAttribute("aria-label", label);
  Object.entries(SITE_LANGUAGES).forEach(([name, item]) => {
    const option = document.createElement("option");
    option.value = pageUrl(item.prefix, page);
    option.textContent = name;
    option.selected = item.prefix === currentPrefix;
    select.append(option);
  });
  select.addEventListener("change", () => location.assign(select.value));
  return select;
}

function isCoreLink(node) {
  if (node.tagName !== "A") return false;
  const href = node.getAttribute("href");
  if (!href || href.startsWith("#")) return false;
  const target = new URL(href, location.origin);
  if (target.hash) return false;
  const name = target.pathname.split("/").filter(Boolean).pop() || "";
  const page = name === "index.html" ? "" : name;
  return SITE_PAGES.includes(page);
}

function contextualNodes() {
  const container = document.querySelector(".nav-links, .mt-links, main > .top-links");
  if (!container) return [];
  return [...container.children].filter((node) => {
    return (node.tagName === "A" || node.tagName === "BUTTON") && !isCoreLink(node);
  });
}

function buildNavigation() {
  const language = currentLanguage();
  const page = currentPage();
  const contextual = contextualNodes();
  const nav = document.createElement("nav");
  const inner = document.createElement("div");
  const brand = linkNode("XAU QUANT", pageUrl(language.prefix, ""), false);
  const links = document.createElement("div");
  nav.className = "site-core-nav";
  nav.setAttribute("aria-label", "Primary");
  inner.className = "site-core-nav__inner";
  brand.className = "site-core-nav__brand";
  links.className = "site-core-nav__links";
  SITE_PAGES.forEach((item, index) => links.append(linkNode(language.labels[index], pageUrl(language.prefix, item), page === item)));
  contextual.forEach((node) => {
    node.classList.add("site-core-nav__link");
    links.append(node);
  });
  links.append(languageNode(page, language.prefix, language.language));
  inner.append(brand, links);
  nav.append(inner);
  document.body.prepend(nav);
  document.body.classList.add("site-nav-ready");
}

buildNavigation();
