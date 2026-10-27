(function () {
  var ICON_OUT =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 13H5v-2h14v2z"/></svg>';
  var ICON_IN =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>';
  var ICON_FULL =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>';
  var ICON_EXIT =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/></svg>';

  function init() {
    document.querySelectorAll("pre.mermaid, div.mermaid").forEach(function (el) {
      if (el.closest(".mermaid-wrap")) return;

      var wrap = document.createElement("div");
      wrap.className = "mermaid-wrap";

      var tools = document.createElement("div");
      tools.className = "mermaid-tools";

      function button(icon, label) {
        var b = document.createElement("button");
        b.type = "button";
        b.title = label;
        b.setAttribute("aria-label", label);
        b.innerHTML = icon;
        tools.appendChild(b);
        return b;
      }

      var outButton = button(ICON_OUT, "Zoom out");
      var inButton = button(ICON_IN, "Zoom in");
      var fullButton = button(ICON_FULL, "Fullscreen");

      var stage = document.createElement("div");
      stage.className = "mermaid-stage";

      var inner = document.createElement("div");
      inner.className = "mermaid-zoom";

      el.parentNode.insertBefore(wrap, el);
      wrap.appendChild(tools);
      wrap.appendChild(stage);
      stage.appendChild(inner);
      inner.appendChild(el);

      var scale = 1;

      function clamp(value) {
        return Math.max(0.5, Math.min(2.5, value));
      }

      function setScale(value) {
        scale = clamp(Math.round(value * 100) / 100);
        inner.style.transformOrigin = "top left";
        inner.style.transform = scale === 1 ? "" : "scale(" + scale + ")";
      }

      function center() {
        stage.scrollLeft = (stage.scrollWidth - stage.clientWidth) / 2;
        stage.scrollTop = (stage.scrollHeight - stage.clientHeight) / 2;
      }

      function fit() {
        if (document.fullscreenElement !== wrap) return;
        inner.style.transform = "";
        var naturalWidth = inner.offsetWidth;
        var naturalHeight = inner.offsetHeight;
        if (!naturalWidth || !naturalHeight) return;
        setScale(
          Math.min(
            stage.clientWidth / naturalWidth,
            stage.clientHeight / naturalHeight
          )
        );
        requestAnimationFrame(center);
      }

      outButton.addEventListener("click", function () {
        setScale(scale - 0.2);
      });

      inButton.addEventListener("click", function () {
        setScale(scale + 0.2);
      });

      fullButton.addEventListener("click", function () {
        if (!document.fullscreenElement && wrap.requestFullscreen) {
          wrap.requestFullscreen();
        } else if (document.exitFullscreen) {
          document.exitFullscreen();
        }
      });

      document.addEventListener("fullscreenchange", function () {
        var isFullscreen = document.fullscreenElement === wrap;
        fullButton.innerHTML = isFullscreen ? ICON_EXIT : ICON_FULL;
        fullButton.title = isFullscreen ? "Exit fullscreen" : "Fullscreen";
        fullButton.setAttribute("aria-label", fullButton.title);

        if (isFullscreen) {
          setTimeout(fit, 50);
        } else {
          setScale(1);
          stage.scrollLeft = 0;
          stage.scrollTop = 0;
        }
      });

      var dragging = false;
      var startX = 0;
      var startY = 0;
      var startLeft = 0;
      var startTop = 0;

      stage.addEventListener("pointerdown", function (event) {
        if (document.fullscreenElement !== wrap) return;
        dragging = true;
        startX = event.clientX;
        startY = event.clientY;
        startLeft = stage.scrollLeft;
        startTop = stage.scrollTop;
        stage.classList.add("is-panning");
        if (stage.setPointerCapture) stage.setPointerCapture(event.pointerId);
        event.preventDefault();
      });

      stage.addEventListener("pointermove", function (event) {
        if (!dragging) return;
        stage.scrollLeft = startLeft - (event.clientX - startX);
        stage.scrollTop = startTop - (event.clientY - startY);
      });

      function endDrag() {
        dragging = false;
        stage.classList.remove("is-panning");
      }

      stage.addEventListener("pointerup", endDrag);
      stage.addEventListener("pointercancel", endDrag);
      stage.addEventListener("pointerleave", endDrag);
    });
  }

  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(init);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
