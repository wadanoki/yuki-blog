(() => {
    const roots = document.querySelectorAll(
        ".article-prose",
    );

    if (!roots.length || typeof window.renderMathInElement !== "function") {
        return;
    }

    roots.forEach((root) => {
        window.renderMathInElement(
            root,
            {
                delimiters: [
                    {
                        left: "$$",
                        right: "$$",
                        display: true,
                    },
                    {
                        left: "$",
                        right: "$",
                        display: false,
                    },
                    {
                        left: "\\(",
                        right: "\\)",
                        display: false,
                    },
                    {
                        left: "\\[",
                        right: "\\]",
                        display: true,
                    },
                ],
                throwOnError: false,
            },
        );
    });
})();
