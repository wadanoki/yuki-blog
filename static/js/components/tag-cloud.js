export function setupTagCloudDialog() {
    const dialog = document.querySelector("#tag-cloud-dialog");
    const openButton = document.querySelector("#open-tag-cloud");
    const closeButton = document.querySelector("#close-tag-cloud");
    const backdrop = document.querySelector("#tag-cloud-backdrop");
    if (!dialog || !openButton || !closeButton || !backdrop) return;

    let previousActiveElement = null;
    const openDialog = () => {
        previousActiveElement = document.activeElement;
        dialog.classList.remove("hidden");
        document.documentElement.classList.add("overflow-hidden");
        requestAnimationFrame(() => closeButton.focus());
    };
    const closeDialog = () => {
        dialog.classList.add("hidden");
        document.documentElement.classList.remove("overflow-hidden");
        if (previousActiveElement instanceof HTMLElement) previousActiveElement.focus();
    };

    openButton.addEventListener("click", openDialog);
    closeButton.addEventListener("click", closeDialog);
    backdrop.addEventListener("click", closeDialog);
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !dialog.classList.contains("hidden")) closeDialog();
    });
}
