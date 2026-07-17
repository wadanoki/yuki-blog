(() => {
    const selectors = document.querySelectorAll(
        ".yuki-tag-selector",
    );

    if (!selectors.length) {
        return;
    }

    const refreshOption = (input) => {
        const option = input.closest(
            ".yuki-tag-option",
        );

        if (!option) {
            return;
        }

        option.classList.toggle(
            "is-selected",
            input.checked,
        );

        option.setAttribute(
            "aria-pressed",
            input.checked
                ? "true"
                : "false",
        );
    };

    selectors.forEach((selector) => {
        const inputs = selector.querySelectorAll(
            'input[type="checkbox"]',
        );

        inputs.forEach((input) => {
            refreshOption(input);

            input.addEventListener(
                "change",
                () => {
                    refreshOption(input);
                },
            );
        });
    });
})();