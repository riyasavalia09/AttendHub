/* Shared dashboard UI helpers
   - Theme toggle (localStorage)
   - Toast system
   - Sidebar toggle
*/

(function () {
  const THEME_KEY = "attendhub:theme";

  function toToastType(variant) {
    const v = String(variant || "info").toLowerCase();
    if (v === "danger") return "error";
    if (v === "success" || v === "warning" || v === "error") return v;
    return "success";
  }

  function notify(title, message, opts) {
    if (typeof window.showToast === "function") {
      const options = opts || {};
      window.showToast({
        type: toToastType(options.variant || options.type),
        title: title || undefined,
        message: message || "",
        durationMs: Number.isFinite(options.timeoutMs) ? options.timeoutMs : undefined,
      });
      return;
    }
    // Silent fallback (no native alerts)
    console.log(title || "Notice", message || "");
  }

  function getPreferredTheme() {
    const stored = localStorage.getItem(THEME_KEY);
    if (stored === "light" || stored === "dark") return stored;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches
      ? "light"
      : "dark";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);

    const toggleBtn = document.getElementById("themeToggle");
    if (toggleBtn) {
      const isLight = theme === "light";
      toggleBtn.setAttribute("aria-pressed", String(isLight));
      toggleBtn.setAttribute("title", isLight ? "Switch to dark theme" : "Switch to light theme");
      const icon = toggleBtn.querySelector("i");
      if (icon) {
        icon.className = isLight ? "fas fa-moon" : "fas fa-sun";
      }
    }
  }

  function wireThemeToggle() {
    const btn = document.getElementById("themeToggle");
    if (!btn) return;

    btn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "dark";
      const next = current === "light" ? "dark" : "light";
      applyTheme(next);
      notify("Theme", next === "light" ? "Light theme enabled." : "Dark theme enabled.", { variant: "info" });
    });
  }

  function wireSidebarToggle() {
    const wrapper = document.getElementById("wrapper");
    const toggle = document.getElementById("menu-toggle");
    if (!wrapper || !toggle) return;

    toggle.addEventListener("click", () => {
      wrapper.classList.toggle("toggled");
    });
  }

  function initPageFade() {
    const main = document.getElementById("page-content-wrapper");
    if (main) main.classList.add("page-fade");
  }

  // Expose a tiny API for existing scripts if they want it
  window.AttendHubUI = {
    toast: notify,
    applyTheme,
    getPreferredTheme,
  };

  document.addEventListener("DOMContentLoaded", () => {
    applyTheme(getPreferredTheme());
    wireThemeToggle();
    wireSidebarToggle();
    initPageFade();
  });
})();
