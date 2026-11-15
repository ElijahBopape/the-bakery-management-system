// The Bakery — video cards + lightbox
// Shared by index.html and baker.html, so both pages use one implementation.
//
// How it works:
//  - A video card is a <button class="video-card" data-video="videos/....mp4">
//    that only shows a poster image. The video file is NOT downloaded until the
//    lightbox opens (that is when we set the <video> src).
//  - The lightbox is a <dialog>. showModal() makes the rest of the page inert,
//    so keyboard focus stays trapped inside it while it is open.
//  - Close with the ✕ button, the Escape key, or a click on the dark background.
//    Closing pauses and unloads the video, then puts focus back on the card.
//  - Anything with data-lightbox-image (the weekly special poster) opens its
//    picture full size in the same lightbox.
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var canHover = window.matchMedia("(hover: hover) and (pointer: fine)"); // mouse, not touch

  // ---- 1. Build the lightbox once ----
  var lightbox = document.createElement("dialog");
  lightbox.className = "lightbox";
  lightbox.innerHTML =
    '<button type="button" class="lightbox-close" aria-label="Close">' +
      '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>' +
    "</button>" +
    '<figure class="lightbox-figure">' +
      '<video class="lightbox-media" controls playsinline preload="metadata"></video>' +
      '<img class="lightbox-media" alt="" />' +
      '<figcaption class="lightbox-caption"></figcaption>' +
    "</figure>";
  document.body.appendChild(lightbox);

  var closeBtn = lightbox.querySelector(".lightbox-close");
  var figure = lightbox.querySelector(".lightbox-figure");
  var video = lightbox.querySelector("video");
  var image = lightbox.querySelector("img");
  var caption = lightbox.querySelector(".lightbox-caption");
  var lastTrigger = null; // the card that opened the lightbox, so focus can return to it

  function openLightbox(trigger) {
    var thumb = trigger.querySelector("img");
    var thumbSrc = thumb ? thumb.currentSrc || thumb.src : ""; // currentSrc = the file the browser chose (e.g. .webp)
    var captionEl = trigger.querySelector(".video-caption");
    var text = trigger.dataset.caption || (captionEl ? captionEl.textContent : "");

    stopPreview(trigger);
    lastTrigger = trigger;
    caption.textContent = text;
    lightbox.setAttribute("aria-label", text || "Media viewer");

    if (trigger.dataset.video) {
      image.hidden = true;
      video.hidden = false;
      video.poster = thumbSrc;
      video.src = trigger.dataset.video; // only now does the video start downloading
    } else {
      video.hidden = true;
      image.hidden = false;
      image.src = thumbSrc;
      image.alt = thumb ? thumb.alt : "";
    }

    document.documentElement.classList.add("lightbox-open");
    lightbox.showModal();
    closeBtn.focus();

    if (!video.hidden) {
      // The visitor pressed "play", so starting playback here is expected.
      var playing = video.play();
      if (playing && playing.catch) playing.catch(function () {}); // if blocked, the controls are still there
    }
  }

  function closeLightbox() {
    if (lightbox.open) lightbox.close();
  }

  // Runs however the lightbox was closed (✕ button, Escape key or background click)
  lightbox.addEventListener("close", function () {
    video.pause();
    video.removeAttribute("src"); // stops the download and resets the video to the start
    video.load();
    image.removeAttribute("src");
    document.documentElement.classList.remove("lightbox-open");
    if (lastTrigger) lastTrigger.focus();
  });

  closeBtn.addEventListener("click", closeLightbox);
  lightbox.addEventListener("click", function (e) {
    // A click on the dark background (not on the video or picture) closes it
    if (e.target === lightbox || e.target === figure) closeLightbox();
  });

  // ---- 2. Optional hover preview (desktop only) ----
  // A muted, looping clip plays over the poster while the mouse is on a card.
  // Skipped on touch screens and for visitors who prefer reduced motion.
  function startPreview(card) {
    if (!canHover.matches || reduceMotion.matches || card.querySelector(".video-preview")) return;
    var thumb = card.querySelector("img");
    var preview = document.createElement("video");
    preview.className = "video-preview";
    preview.muted = true; // previews never play sound
    preview.loop = true;
    preview.playsInline = true;
    preview.preload = "metadata";
    preview.setAttribute("muted", "");
    preview.setAttribute("playsinline", "");
    preview.setAttribute("aria-hidden", "true");
    if (thumb) preview.poster = thumb.currentSrc || thumb.src;
    preview.addEventListener("playing", function () { preview.classList.add("is-playing"); }); // fade in once frames arrive
    preview.src = card.dataset.video;
    card.querySelector(".video-thumb").appendChild(preview);
    var playing = preview.play();
    if (playing && playing.catch) playing.catch(function () {});
  }

  function stopPreview(card) {
    var preview = card.querySelector(".video-preview");
    if (!preview) return;
    preview.pause();
    preview.removeAttribute("src");
    preview.load();
    preview.remove();
  }

  // ---- 3. Wire up every card on the page ----
  document.querySelectorAll(".video-card, [data-lightbox-image]").forEach(function (trigger) {
    trigger.addEventListener("click", function () { openLightbox(trigger); });

    if (trigger.dataset.video) {
      trigger.addEventListener("mouseenter", function () { startPreview(trigger); });
      trigger.addEventListener("mouseleave", function () { stopPreview(trigger); });
    }
  });
})();
