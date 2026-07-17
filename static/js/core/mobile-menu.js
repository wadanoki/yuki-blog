export function setupMobileMenu() {
    const button = document.querySelector("#mobile-menu-button");
    const menu = document.querySelector("#mobile-menu");
    if (!button || !menu) return;

    button.addEventListener("click", () => {
        const isHidden = menu.classList.toggle("hidden");
        button.setAttribute("aria-expanded", String(!isHidden));
    });

    menu.addEventListener("click", (event) => {
        if (!(event.target instanceof Element)) return;
        if (!event.target.closest("a")) return;

        menu.classList.add("hidden");
        button.setAttribute("aria-expanded", "false");
    });

    document.addEventListener("click", (event) => {
        if (!(event.target instanceof Node)) return;
        if (!menu.contains(event.target) && !button.contains(event.target)) {
            menu.classList.add("hidden");
            button.setAttribute("aria-expanded", "false");
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") return;

        menu.classList.add("hidden");
        button.setAttribute("aria-expanded", "false");
    });
}
