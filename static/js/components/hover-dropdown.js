/**
 * Bind a desktop navigation dropdown so the pointer can safely travel from
 * the trigger to the panel without the panel disappearing in the small gap.
 */
export function bindHoverDropdown({
    group,
    trigger,
    dropdown,
    open,
    close,
    closeDelay = 280,
    toggleOnClick = false,
}) {
    let closeTimer = null;

    const cancelClose = () => {
        window.clearTimeout(closeTimer);
        closeTimer = null;
    };

    const isInteractionInside = () => {
        const focusedElement = document.activeElement;

        return (
            group.matches(":hover")
            || dropdown.matches(":hover")
            || (
                focusedElement instanceof Node
                && group.contains(focusedElement)
            )
        );
    };

    const openNow = () => {
        cancelClose();
        open();
    };

    const closeNow = () => {
        cancelClose();
        close();
    };

    const scheduleClose = () => {
        cancelClose();

        closeTimer = window.setTimeout(() => {
            if (isInteractionInside()) {
                return;
            }

            close();
        }, closeDelay);
    };

    group.addEventListener("pointerenter", openNow);
    group.addEventListener("pointerleave", scheduleClose);

    /*
     * The dropdown is absolutely positioned and may sit outside the visual
     * box of its parent. Listening on the panel itself makes the hover state
     * resilient even when the pointer crosses that boundary slowly.
     */
    dropdown.addEventListener("pointerenter", cancelClose);
    dropdown.addEventListener("pointerleave", scheduleClose);

    group.addEventListener("focusin", openNow);
    group.addEventListener("focusout", scheduleClose);

    if (toggleOnClick) {
        trigger.addEventListener("click", () => {
            const isExpanded = trigger.getAttribute("aria-expanded") === "true";

            if (isExpanded) {
                closeNow();
            } else {
                openNow();
            }
        });
    }

    document.addEventListener("pointerdown", (event) => {
        const target = event.target;

        if (target instanceof Node && !group.contains(target)) {
            closeNow();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (
            event.key !== "Escape"
            || trigger.getAttribute("aria-expanded") !== "true"
        ) {
            return;
        }

        closeNow();
        trigger.focus();
    });

    return {
        cancelClose,
        closeNow,
        openNow,
        scheduleClose,
    };
}
