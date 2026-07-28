(() => {
  const MOBILE_BREAKPOINT = 880;
  const navInner = document.querySelector(".nav-inner");
  const navLinks = navInner?.querySelector(".nav-links");
  const languageSwitcher = document.querySelector(".language-switcher");
  const language = document.documentElement.lang.toLowerCase();
  const menuLabels = {
    "zh-cn": ["打开导航菜单", "关闭导航菜单"],
    "zh-tw": ["開啟導覽選單", "關閉導覽選單"],
    en: ["Open navigation menu", "Close navigation menu"],
    ja: ["ナビゲーションを開く", "ナビゲーションを閉じる"],
    ko: ["탐색 메뉴 열기", "탐색 메뉴 닫기"],
    de: ["Navigationsmenü öffnen", "Navigationsmenü schließen"],
    fr: ["Ouvrir le menu de navigation", "Fermer le menu de navigation"]
  }[language] || ["Open navigation menu", "Close navigation menu"];

  if (!(navInner instanceof HTMLElement) || !(navLinks instanceof HTMLElement)) {
    return;
  }

  const toggle = document.createElement("button");
  toggle.className = "mobile-menu-toggle";
  toggle.type = "button";
  toggle.setAttribute("aria-label", menuLabels[0]);
  toggle.setAttribute("aria-expanded", "false");
  toggle.setAttribute("aria-controls", "mobile-navigation");
  toggle.innerHTML = '<span class="mobile-menu-icon" aria-hidden="true">☰</span>';
  navLinks.id ||= "mobile-navigation";
  navInner.insertBefore(toggle, navLinks);
  if (languageSwitcher instanceof HTMLElement) {
    languageSwitcher.classList.add("language-switcher--nav");
    navInner.insertBefore(languageSwitcher, toggle);
  }

  const closeMenu = () => {
    navInner.classList.remove("is-menu-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", menuLabels[0]);
    toggle.querySelector(".mobile-menu-icon").textContent = "☰";
    navLinks.setAttribute("aria-hidden", "true");
  };

  toggle.addEventListener("click", () => {
    const isOpen = navInner.classList.toggle("is-menu-open");
    toggle.setAttribute("aria-expanded", String(isOpen));
    toggle.setAttribute("aria-label", isOpen ? menuLabels[1] : menuLabels[0]);
    toggle.querySelector(".mobile-menu-icon").textContent = isOpen ? "×" : "☰";
    navLinks.setAttribute("aria-hidden", String(!isOpen));
  });

  navLinks.addEventListener("click", (event) => {
    if (event.target instanceof HTMLAnchorElement) {
      closeMenu();
    }
  });

  document.addEventListener("click", (event) => {
    if (event.target instanceof Node && !navInner.contains(event.target)) {
      closeMenu();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeMenu();
      toggle.focus();
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > MOBILE_BREAKPOINT) {
      closeMenu();
      navLinks.removeAttribute("aria-hidden");
    }
  });

  if (window.innerWidth <= MOBILE_BREAKPOINT) {
    navLinks.setAttribute("aria-hidden", "true");
  }
})();
