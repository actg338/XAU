(function () {
  const modal = document.querySelector("[data-image-modal]");
  const modalImage = document.querySelector("[data-modal-image]");
  const closeButton = document.querySelector("[data-modal-close]");

  function openImage(src, alt) {
    if (!modal || !modalImage) return;
    modalImage.src = src;
    modalImage.alt = alt || "";
    modal.classList.add("is-open");
    document.body.style.overflow = "hidden";
  }

  function closeImage() {
    if (!modal || !modalImage) return;
    modal.classList.remove("is-open");
    modalImage.removeAttribute("src");
    document.body.style.overflow = "";
  }

  document.addEventListener("click", function (event) {
    const trigger = event.target.closest("[data-full-image]");
    if (trigger) {
      openImage(trigger.getAttribute("data-full-image"), trigger.getAttribute("data-image-alt"));
    }

    if (event.target === modal) {
      closeImage();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeImage();
  });

  if (closeButton) {
    closeButton.addEventListener("click", closeImage);
  }
})();
