import { bindHoverDropdown } from "./hover-dropdown.js";

export function setupTimelineMenu() {
    const group = document.querySelector("#timeline-nav-group");
    const trigger = document.querySelector("#timeline-nav-trigger");
    const dropdown = document.querySelector("#timeline-dropdown");

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
        trigger.classList.add("bg-neutral-2", "text-neutral-10");
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
        trigger.classList.remove("bg-neutral-2", "text-neutral-10");
        trigger.setAttribute("aria-expanded", "false");
    };

    bindHoverDropdown({
        group,
        trigger,
        dropdown,
        open: openMenu,
        close: closeMenu,
    });
}
