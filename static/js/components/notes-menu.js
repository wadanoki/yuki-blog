import { bindHoverDropdown } from "./hover-dropdown.js";

export function setupNotesMenu() {
    const group = document.querySelector("#notes-nav-group");
    const trigger = document.querySelector("#notes-nav-trigger");
    const dropdown = document.querySelector("#notes-dropdown");

    if (!group || !trigger || !dropdown) {
        return;
    }

    const collectionItems = Array.from(
        group.querySelectorAll(
            ".notes-collection-item[data-collection-target]",
        ),
    );
    const panels = Array.from(
        group.querySelectorAll(
            ".notes-list-panel[data-collection-panel]",
        ),
    );

    const activateCollection = (collectionName) => {
        collectionItems.forEach((item) => {
            const isActive = item.dataset.collectionTarget === collectionName;
            item.classList.toggle("bg-neutral-2", isActive);
            item.classList.toggle("text-neutral-10", isActive);
        });

        panels.forEach((panel) => {
            panel.classList.toggle(
                "hidden",
                panel.dataset.collectionPanel !== collectionName,
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
        activateCollection("all");
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
        activateCollection("all");
    };

    bindHoverDropdown({
        group,
        trigger,
        dropdown,
        open: openMenu,
        close: closeMenu,
    });

    collectionItems.forEach((item) => {
        const collectionName = item.dataset.collectionTarget;

        if (!collectionName) {
            return;
        }

        item.addEventListener(
            "pointerenter",
            () => activateCollection(collectionName),
        );
        item.addEventListener(
            "focus",
            () => activateCollection(collectionName),
        );
    });

    activateCollection("all");
}
