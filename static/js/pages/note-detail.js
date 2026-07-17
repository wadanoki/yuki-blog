export function setupNoteDetail() {
    const article = document.querySelector(
        "#note-article-content",
    );

    const sidebar = document.querySelector(
        "#note-reading-sidebar",
    );

    if (!article || !sidebar) {
        return;
    }

    const tocLinks = Array.from(
        sidebar.querySelectorAll(
            ".note-toc__link[data-note-target-id]",
        ),
    );

    const entries = tocLinks
        .map((link) => {
            const targetId =
                link.dataset.noteTargetId;

            if (!targetId) {
                return null;
            }

            const heading =
                document.getElementById(targetId);

            if (!heading) {
                return null;
            }

            return {
                link,
                heading,
            };
        })
        .filter(Boolean);

    const progressCircle =
        document.querySelector(
            "#note-progress-circle",
        );

    const progressText =
        document.querySelector(
            "#note-progress-text",
        );

    const backToTop =
        document.querySelector(
            "#note-back-to-top",
        );


    entries.forEach(({ link, heading }) => {
        link.addEventListener(
            "click",
            (event) => {
                event.preventDefault();

                heading.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                });

                history.replaceState(
                    null,
                    "",
                    `#${heading.id}`,
                );
            },
        );
    });


    const update = () => {
        updateActiveHeading(entries);

        updateProgress({
            article,
            progressCircle,
            progressText,
        });
    };


    let ticking = false;

    const requestUpdate = () => {
        if (ticking) {
            return;
        }

        ticking = true;

        window.requestAnimationFrame(() => {
            update();
            ticking = false;
        });
    };


    window.addEventListener(
        "scroll",
        requestUpdate,
        { passive: true },
    );

    window.addEventListener(
        "resize",
        requestUpdate,
    );


    backToTop?.addEventListener(
        "click",
        () => {
            window.scrollTo({
                top: 0,
                behavior: "smooth",
            });
        },
    );


    update();
}


function updateActiveHeading(entries) {
    if (entries.length === 0) {
        return;
    }

    let activeIndex = 0;

    entries.forEach(
        ({ heading }, index) => {
            if (
                heading
                    .getBoundingClientRect()
                    .top
                <= 160
            ) {
                activeIndex = index;
            }
        },
    );

    entries.forEach(({ link }, index) => {
        link.classList.toggle(
            "is-active",
            index === activeIndex,
        );
    });
}


function updateProgress({
    article,
    progressCircle,
    progressText,
}) {
    const rect =
        article.getBoundingClientRect();

    const articleTop =
        rect.top + window.scrollY;

    const articleHeight =
        Math.max(
            1,
            article.offsetHeight,
        );

    const anchor =
        window.scrollY
        + window.innerHeight * 0.35;

    const progress = clamp(
        (
            anchor
            - articleTop
        )
        / articleHeight
        * 100,
        0,
        100,
    );

    progressCircle?.style.setProperty(
        "--note-reading-progress",
        `${progress * 3.6}deg`,
    );

    if (progressText) {
        progressText.textContent =
            `${Math.round(progress)}%`;
    }
}


function clamp(value, minimum, maximum) {
    return Math.min(
        maximum,
        Math.max(minimum, value),
    );
}