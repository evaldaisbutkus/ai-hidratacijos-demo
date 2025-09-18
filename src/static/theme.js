(() => {
  const KEY = "theme";
  const root = document.documentElement;

  const currentSystem = () =>
    matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";

  const apply = t => root.setAttribute("data-theme", t);

  let theme = localStorage.getItem(KEY) || currentSystem();
  apply(theme);

  window.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("themeToggle");
    if (!btn) return;

    const refresh = () => { btn.textContent = theme === "dark" ? "☀️" : "🌙"; };
    refresh();

    btn.addEventListener("click", () => {
      theme = theme === "dark" ? "light" : "dark";
      localStorage.setItem(KEY, theme);
      apply(theme);
      refresh();
    });
  });
})();