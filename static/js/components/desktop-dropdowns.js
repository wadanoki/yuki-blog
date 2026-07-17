/**
 * Desktop navigation dropdowns.
 *
 * Visual open/close state is intentionally handled by CSS :hover and
 * :focus-within. JavaScript only manages accessibility state, touch/click
 * toggling for button triggers, home-panel viewport positioning, and the
 * category preview panels. There are no mouse-leave timers.
 */
export function setupDesktopDropdowns() {
    const navigation = document.querySelector("#desktop-navigation");

    if (!navigation) {
        return;
    }

    const groups = Array.from(
        navigation.querySelectorAll(".desktop-nav-group"),
    );

    const closePinnedGroups = (except = null) => {
        groups.forEach((group) => {
            if (group === except) {
                return;
            }

            group.removeAttribute("data-open");

            const trigger = group.querySelector(".desktop-nav-trigger");
            trigger?.setAttribute("aria-expanded", "false");
        });
    };

    groups.forEach((group) => {
        const trigger = group.querySelector(".desktop-nav-trigger");
        const dropdown = group.querySelector(":scope > .desktop-nav-dropdown");

        if (!trigger || !dropdown) {
            return;
        }

        const setExpanded = (expanded) => {
            trigger.setAttribute("aria-expanded", expanded ? "true" : "false");
        };

        group.addEventListener("pointerenter", () => {
            setExpanded(true);
        });

        group.addEventListener("pointerleave", () => {
            if (group.getAttribute("data-open") !== "true") {
                setExpanded(false);
            }
        });

        group.addEventListener("focusin", () => {
            setExpanded(true);
        });

        group.addEventListener("focusout", () => {
            queueMicrotask(() => {
                if (
                    !group.contains(document.activeElement)
                    && group.getAttribute("data-open") !== "true"
                ) {
                    setExpanded(false);
                }
            });
        });

        if (trigger instanceof HTMLButtonElement) {
            trigger.addEventListener("click", (event) => {
                event.stopPropagation();

                const willOpen = group.getAttribute("data-open") !== "true";
                closePinnedGroups(group);

                if (willOpen) {
                    group.setAttribute("data-open", "true");
                    setExpanded(true);
                } else {
                    group.removeAttribute("data-open");
                    setExpanded(false);
                }
            });
        }
    });

    document.addEventListener("pointerdown", (event) => {
        const target = event.target;

        if (!(target instanceof Node) || navigation.contains(target)) {
            return;
        }

        closePinnedGroups();
    });

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") {
            return;
        }

        const openGroup = groups.find(
            (group) => group.getAttribute("data-open") === "true",
        );

        if (!openGroup) {
            return;
        }

        const trigger = openGroup.querySelector(".desktop-nav-trigger");
        closePinnedGroups();
        trigger?.focus();
    });

    setupHomeDropdownPosition(navigation);
    setupPreviewSwitcher({
        navigation,
        groupSelector: "#writing-nav-group",
        itemSelector: ".writing-category-item[data-category-target]",
        itemDataKey: "categoryTarget",
        panelSelector: ".writing-post-panel[data-category-panel]",
        panelDataKey: "categoryPanel",
        defaultKey: "all",
    });
    setupPreviewSwitcher({
        navigation,
        groupSelector: "#notes-nav-group",
        itemSelector: ".notes-collection-item[data-collection-target]",
        itemDataKey: "collectionTarget",
        panelSelector: ".notes-list-panel[data-collection-panel]",
        panelDataKey: "collectionPanel",
        defaultKey: "all",
    });
}

function setupHomeDropdownPosition(navigation) {
    const group = navigation.querySelector("#home-nav-group");
    const dropdown = navigation.querySelector("#home-dropdown");

    if (!group || !dropdown) {
        return;
    }

    const position = () => {
        const viewportPadding = 12;
        const groupRect = group.getBoundingClientRect();
        const dropdownWidth = dropdown.offsetWidth;
        let offset = 0;

        const projectedRight = groupRect.left + dropdownWidth;
        const maximumRight = window.innerWidth - viewportPadding;

        if (projectedRight > maximumRight) {
            offset -= projectedRight - maximumRight;
        }

        const projectedLeft = groupRect.left + offset;

        if (projectedLeft < viewportPadding) {
            offset += viewportPadding - projectedLeft;
        }

        dropdown.style.setProperty("--home-menu-offset-x", `${offset}px`);
    };

    group.addEventListener("pointerenter", position);
    group.addEventListener("focusin", position);
    window.addEventListener("resize", position);
}

function setupPreviewSwitcher({
    navigation,
    groupSelector,
    itemSelector,
    itemDataKey,
    panelSelector,
    panelDataKey,
    defaultKey,
}) {
    const group = navigation.querySelector(groupSelector);

    if (!group) {
        return;
    }

    const items = Array.from(group.querySelectorAll(itemSelector));
    const panels = Array.from(group.querySelectorAll(panelSelector));

    const activate = (key) => {
        items.forEach((item) => {
            const active = item.dataset[itemDataKey] === key;
            item.classList.toggle("bg-neutral-2", active);
            item.classList.toggle("text-neutral-10", active);
            item.setAttribute("aria-current", active ? "true" : "false");
        });

        panels.forEach((panel) => {
            panel.classList.toggle("hidden", panel.dataset[panelDataKey] !== key);
        });
    };

    items.forEach((item) => {
        const key = item.dataset[itemDataKey];

        if (!key) {
            return;
        }

        item.addEventListener("pointerenter", () => activate(key));
        item.addEventListener("focus", () => activate(key));
    });

    group.addEventListener("pointerleave", () => activate(defaultKey));
    activate(defaultKey);
}
