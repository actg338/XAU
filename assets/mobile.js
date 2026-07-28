(() => {
  const navInner = document.querySelector(".nav-inner");
  const navLinks = navInner?.querySelector(".nav-links");
  const languageSwitcher = document.querySelector(".language-switcher");

  if (!(navInner instanceof HTMLElement) || !(navLinks instanceof HTMLElement)) {
    return;
  }

  navInner.classList.add("mobile-nav-ready");
  navLinks.removeAttribute("aria-hidden");

  if (languageSwitcher instanceof HTMLElement) {
    languageSwitcher.classList.add("language-switcher--nav");
    navLinks.insertBefore(languageSwitcher, navLinks.firstChild);
  }

  navLinks.addEventListener("wheel", event => {
    if (window.innerWidth > 880 || Math.abs(event.deltaX) >= Math.abs(event.deltaY)) {
      return;
    }
    navLinks.scrollLeft += event.deltaY;
    event.preventDefault();
  }, { passive: false });
})();
