import { bindHoverDropdown } from "./hover-dropdown.js";

export function setupWritingMenu() {
    const group = document.querySelector("#writing-nav-group");
    const trigger = document.querySelector("#writing-nav-trigger");
    const dropdown = document.querySelector("#writing-dropdown");

    if (!group || !trigger || !dropdown) {
        return;
    }

    const categoryItems = group.querySelectorAll(
        ".writing-category-item[data-category-target]",
    );
    const panels = group.querySelectorAll(
        ".writing-post-panel[data-category-panel]",
    );

    const activateCategory = (name) => {
        categoryItems.forEach((item) => {
            const active = item.dataset.categoryTarget === name;
            item.classList.toggle("bg-neutral-2", active);
            item.classList.toggle("text-neutral-10", active);
        });

        panels.forEach((panel) => {
            panel.classList.toggle(
                "hidden",
                panel.dataset.categoryPanel !== name,
            );
        });
    };

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
        activateCategory("all");
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
        activateCategory("all");
    };

    bindHoverDropdown({
        group,
        trigger,
        dropdown,
        open: openMenu,
        close: closeMenu,
    });

    categoryItems.forEach((item) => {
        const name = item.dataset.categoryTarget;

        if (!name) {
            return;
        }

        item.addEventListener("pointerenter", () => activateCategory(name));
        item.addEventListener("focus", () => activateCategory(name));
    });

    activateCategory("all");
}
