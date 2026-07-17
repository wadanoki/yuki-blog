export function markActiveNavigation() {
    const currentPath = window.location.pathname;
    document.querySelectorAll(".js-nav-link[data-path]").forEach((link) => {
        const targetPath = link.dataset.path;
        if (!targetPath) return;
        const active = targetPath === "/"
            ? currentPath === "/"
            : currentPath.startsWith(targetPath);
        if (active) {
            link.classList.add("bg-neutral-2", "text-neutral-10", "ring-1", "ring-border", "shadow-sm");
        }
    });
}
