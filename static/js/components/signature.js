export function setupSignatureAnimation() {
    const signature = document.querySelector(
        "#post-signature",
    );

    if (!signature) {
        return;
    }

    const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
    ).matches;

    if (reducedMotion) {
        signature.classList.add("is-visible");
        return;
    }

    if (!("IntersectionObserver" in window)) {
        signature.classList.add("is-visible");
        return;
    }

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }

                signature.classList.add(
                    "is-visible",
                );

                observer.unobserve(signature);
            });
        },
        {
            threshold: 0.35,
            rootMargin: "0px 0px -8% 0px",
        },
    );

    observer.observe(signature);
}