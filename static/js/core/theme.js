export function setupTheme() {
    const button = document.querySelector("#theme-toggle");
    const icon = document.querySelector("#theme-icon");
    if (!button || !icon) return;

    const updateIcon = () => {
        const isDark = document.documentElement.classList.contains("dark");
        icon.textContent = isDark ? "☀" : "◐";
    };

    updateIcon();
    button.addEventListener("click", () => {
        const isDark = document.documentElement.classList.toggle("dark");
        localStorage.setItem("theme", isDark ? "dark" : "light");
        updateIcon();
    });
}
