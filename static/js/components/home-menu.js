import { bindHoverDropdown } from "./hover-dropdown.js";

export function setupHomeMenu() {
    const group = document.querySelector("#home-nav-group");
    const trigger = document.querySelector("#home-nav-trigger");
    const dropdown = document.querySelector("#home-dropdown");

    if (!group || !trigger || !dropdown) {
        return;
    }

    const positionDropdown = () => {
        dropdown.style.setProperty("--home-menu-offset-x", "0px");

        const rect = dropdown.getBoundingClientRect();
        const viewportPadding = 12;
        const overflowRight = rect.right - (window.innerWidth - viewportPadding);

        if (overflowRight > 0) {
            dropdown.style.setProperty(
                "--home-menu-offset-x",
                `${-overflowRight}px`,
            );
        }
    };

    const openMenu = () => {
        dropdown.classList.add("is-open");
        positionDropdown();
        trigger.classList.add("bg-neutral-2", "text-neutral-10");
        trigger.setAttribute("aria-expanded", "true");
    };

    const closeMenu = () => {
        dropdown.classList.remove("is-open");
        trigger.classList.remove("bg-neutral-2", "text-neutral-10");
        trigger.setAttribute("aria-expanded", "false");
    };

    window.addEventListener("resize", () => {
        if (trigger.getAttribute("aria-expanded") === "true") {
            positionDropdown();
        }
    });

    bindHoverDropdown({
        group,
        trigger,
        dropdown,
        open: openMenu,
        close: closeMenu,
    });
}
