export function setupPostDetail() {
    const article = document.querySelector(
        "#article-content",
    );

    if (!article) {
        return;
    }


    const backToTop = document.querySelector(
        "#back-to-top",
    );

    const copyLinkButton = document.querySelector(
        "#copy-post-link",
    );

    backToTop?.addEventListener("click", () => {
        window.scrollTo({
            top: 0,
            behavior: "smooth",
        });
    });


    copyLinkButton?.addEventListener(
        "click",
        () => copyCurrentLink(copyLinkButton),
    );

}


async function copyCurrentLink(button) {
    try {
        await navigator.clipboard.writeText(
            window.location.href,
        );

        const originalText =
            button.textContent;

        button.textContent = "✓";

        window.setTimeout(() => {
            button.textContent =
                originalText || "↗";
        }, 1200);
    } catch (error) {
        console.error(
            "复制链接失败：",
            error,
        );
    }
}