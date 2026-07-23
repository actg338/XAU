(() => {
  const MOBILE_BREAKPOINT = 880;
  const navInner = document.querySelector(".nav-inner");
  const navLinks = navInner?.querySelector(".nav-links");

  if (!(navInner instanceof HTMLElement) || !(navLinks instanceof HTMLElement)) {
    return;
  }

  const toggle = document.createElement("button");
  toggle.className = "mobile-menu-toggle";
  toggle.type = "button";
  toggle.setAttribute("aria-label", "打开导航菜单");
  toggle.setAttribute("aria-expanded", "false");
  toggle.setAttribute("aria-controls", "mobile-navigation");
  navLinks.id ||= "mobile-navigation";
  navInner.insertBefore(toggle, navLinks);

  const closeMenu = () => {
    navInner.classList.remove("is-menu-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "打开导航菜单");
  };

  toggle.addEventListener("click", () => {
    const isOpen = navInner.classList.toggle("is-menu-open");
    toggle.setAttribute("aria-expanded", String(isOpen));
    toggle.setAttribute("aria-label", isOpen ? "关闭导航菜单" : "打开导航菜单");
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

  window.addEventListener("resize", () => {
    if (window.innerWidth > MOBILE_BREAKPOINT) {
      closeMenu();
    }
  });
})();
