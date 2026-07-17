import { bindHoverDropdown } from "./hover-dropdown.js";

export function setupMoreMenu() {
    const group = document.querySelector("#more-nav-group");
    const trigger = document.querySelector("#more-nav-trigger");
    const dropdown = document.querySelector("#more-dropdown");

    if (!group || !trigger || !dropdown) {
        return;
    }

    const openMenu = () => {
        dropdown.classList.remove(
            "invisible",
            "pointer-events-none",
            "opacity-0",
        );
        dropdown.classList.add(
            "visible",
            "pointer-events-auto",
            "opacity-100",
        );
        trigger.setAttribute("aria-expanded", "true");
    };

    const closeMenu = () => {
        dropdown.classList.remove(
            "visible",
            "pointer-events-auto",
            "opacity-100",
        );
        dropdown.classList.add(
            "invisible",
            "pointer-events-none",
            "opacity-0",
        );
        trigger.setAttribute("aria-expanded", "false");
    };

    bindHoverDropdown({
        group,
        trigger,
        dropdown,
        open: openMenu,
        close: closeMenu,
        toggleOnClick: true,
    });
}
