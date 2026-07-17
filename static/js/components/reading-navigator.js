export function setupReadingNavigator() {
    const navigator = document.querySelector(
        "#reading-navigator",
    );

    const article = document.querySelector(
        "#article-content",
    );

    if (!navigator || !article) {
        return;
    }

    const track = navigator.querySelector(
        "#reading-track",
    );

    const trackSvg = navigator.querySelector(
        "#reading-track-svg",
    );

    const trackBasePath = navigator.querySelector(
        "#reading-track-base-path",
    );

    const trackReadPath = navigator.querySelector(
        "#reading-track-read-path",
    );

    const trackSummary = navigator.querySelector(
        "#reading-track-summary",
    );

    const summaryTitle = navigator.querySelector(
        "#reading-track-summary-title",
    );

    const summaryProgress = navigator.querySelector(
        "#reading-track-summary-progress",
    );

    const toc = navigator.querySelector(
        "#reading-toc",
    );

    const tocViewport = navigator.querySelector(
        ".reading-toc-viewport",
    );

    const collapsedViewport = navigator.querySelector(
        ".reading-track-viewport",
    );

    const tocLinks = Array.from(
        navigator.querySelectorAll(
            ".reading-toc__link[data-target-id]",
        ),
    );

    const trackPoints = Array.from(
        navigator.querySelectorAll(
            ".reading-track__point[data-target-id]",
        ),
    );

    const progressCircle = navigator.querySelector(
        "#reading-progress-circle",
    );

    const progressText = navigator.querySelector(
        "#reading-progress-text",
    );

    const backToTop = navigator.querySelector(
        "#reading-back-to-top",
    );

    const sections = buildSectionEntries({
        tocLinks,
        trackPoints,
    });

    let geometry = {
        articleTop: 0,
        articleHeight: 1,
        trackHeight: 900,
    };

    let smoothProgress = 0;
    let smoothBendCenter = 0;
    let activeIndex = -1;
    let ticking = false;


    function measure() {
        geometry = measureGeometry({
            article,
            sections,
        });

        placeTrackPoints(sections);

        track?.style.setProperty(
            "--reading-track-height",
            `${geometry.trackHeight}px`,
        );
    }


    function update() {
        const targetProgress =
            calculateReadingProgress({
                articleTop: geometry.articleTop,
                articleHeight: geometry.articleHeight,
            });

        activeIndex = findActiveSectionIndex(
            sections,
        );

        const targetBendCenter =
            sections[activeIndex]?.trackPosition
            ?? (
                targetProgress
                / 100
                * geometry.trackHeight
            );

        smoothProgress +=
            (
                targetProgress
                - smoothProgress
            )
            * 0.16;

        smoothBendCenter +=
            (
                targetBendCenter
                - smoothBendCenter
            )
            * 0.18;

        updateActiveSection({
            sections,
            activeIndex,
        });

        updateMovingTrack({
            sections,
            activeIndex,
            progress: smoothProgress,
            bendCenter: smoothBendCenter,
            track,
            trackSvg,
            trackBasePath,
            trackReadPath,
            trackSummary,
            summaryTitle,
            summaryProgress,
            collapsedViewport,
            trackHeight: geometry.trackHeight,
        });

        updateMovingToc({
            sections,
            activeIndex,
            toc,
            tocViewport,
        });

        updateProgressDisplay({
            progress: smoothProgress,
            progressCircle,
            progressText,
        });

        const stillAnimating =
            Math.abs(
                targetProgress
                - smoothProgress,
            ) > 0.05
            ||
            Math.abs(
                targetBendCenter
                - smoothBendCenter,
            ) > 0.5;

        if (stillAnimating) {
            requestUpdate();
        }
    }


    function requestUpdate() {
        if (ticking) {
            return;
        }

        ticking = true;

        window.requestAnimationFrame(() => {
            update();
            ticking = false;
        });
    }


    setupNavigatorClicks(sections);


    window.addEventListener(
        "scroll",
        requestUpdate,
        { passive: true },
    );

    window.addEventListener(
        "resize",
        () => {
            measure();
            requestUpdate();
        },
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

    navigator.addEventListener(
        "click",
        (event) => {
            const target = event.target;

            if (
                target instanceof Element
                && target.closest(
                    [
                        ".reading-track__point",
                        ".reading-toc__link",
                        ".reading-back-to-top",
                    ].join(","),
                )
            ) {
                return;
            }

            navigator.classList.toggle(
                "is-expanded",
            );
        },
    );

    document.addEventListener(
        "click",
        (event) => {
            const target = event.target;

            if (!(target instanceof Node)) {
                return;
            }

            if (!navigator.contains(target)) {
                navigator.classList.remove(
                    "is-expanded",
                );
            }
        },
    );

    measure();

    const initialProgress =
        calculateReadingProgress({
            articleTop: geometry.articleTop,
            articleHeight: geometry.articleHeight,
        });

    smoothProgress = initialProgress;

    smoothBendCenter =
        sections[0]?.trackPosition
        ?? (
            initialProgress
            / 100
            * geometry.trackHeight
        );

    update();
}


function buildSectionEntries({
    tocLinks,
    trackPoints,
}) {
    return tocLinks
        .map((tocLink, index) => {
            const targetId =
                tocLink.dataset.targetId;

            if (!targetId) {
                return null;
            }

            const heading =
                document.getElementById(targetId);

            if (!heading) {
                return null;
            }

            return {
                heading,
                tocLink,
                trackPoint:
                    trackPoints[index] || null,
                articlePosition: 0,
                trackPosition: 0,
            };
        })
        .filter(Boolean);
}


function measureGeometry({
    article,
    sections,
}) {
    const articleRect =
        article.getBoundingClientRect();

    const articleTop =
        articleRect.top + window.scrollY;

    const articleHeight =
        Math.max(
            1,
            article.offsetHeight,
        );

    const sectionCount =
        Math.max(
            1,
            sections.length,
        );

    const trackHeight =
        Math.max(
            900,
            sectionCount * 92,
        );

    sections.forEach((section) => {
        const headingTop =
            section.heading
                .getBoundingClientRect()
                .top
            + window.scrollY;

        section.articlePosition = clamp(
            (
                headingTop
                - articleTop
            )
            / articleHeight,
            0,
            1,
        );

        section.trackPosition =
            section.articlePosition
            * trackHeight;
    });

    return {
        articleTop,
        articleHeight,
        trackHeight,
    };
}


function placeTrackPoints(sections) {
    sections.forEach((section) => {
        if (!section.trackPoint) {
            return;
        }

        section.trackPoint.style.top =
            `${section.trackPosition}px`;
    });
}


function setupNavigatorClicks(sections) {
    sections.forEach((section) => {
        const navigate = (event) => {
            event.preventDefault();

            section.heading.scrollIntoView({
                behavior: "smooth",
                block: "start",
            });

            history.replaceState(
                null,
                "",
                `#${section.heading.id}`,
            );
        };

        section.tocLink.addEventListener(
            "click",
            navigate,
        );

        section.trackPoint?.addEventListener(
            "click",
            navigate,
        );
    });
}


function calculateReadingProgress({
    articleTop,
    articleHeight,
}) {
    const viewportAnchor =
        window.scrollY
        + window.innerHeight * 0.35;

    return clamp(
        (
            viewportAnchor
            - articleTop
        )
        / articleHeight
        * 100,
        0,
        100,
    );
}


function findActiveSectionIndex(sections) {
    if (sections.length === 0) {
        return -1;
    }

    let currentIndex = 0;

    sections.forEach((section, index) => {
        const top =
            section.heading
                .getBoundingClientRect()
                .top;

        if (top <= 170) {
            currentIndex = index;
        }
    });

    return currentIndex;
}


function updateActiveSection({
    sections,
    activeIndex,
}) {
    sections.forEach((section, index) => {
        const isActive =
            index === activeIndex;

        const isPassed =
            index < activeIndex;

        section.tocLink.classList.toggle(
            "is-active",
            isActive,
        );

        section.tocLink.classList.toggle(
            "is-passed",
            isPassed,
        );

        section.trackPoint?.classList.toggle(
            "is-active",
            isActive,
        );

        section.trackPoint?.classList.toggle(
            "is-passed",
            isPassed,
        );
    });
}


function updateMovingTrack({
    sections,
    activeIndex,
    progress,
    bendCenter,
    track,
    trackSvg,
    trackBasePath,
    trackReadPath,
    trackSummary,
    summaryTitle,
    summaryProgress,
    collapsedViewport,
    trackHeight,
}) {
    if (
        !track
        || !collapsedViewport
    ) {
        return;
    }

    const viewportHeight =
        collapsedViewport.clientHeight;

    const progressPosition =
        progress / 100
        * trackHeight;

    const targetViewportPosition =
        viewportHeight * 0.54;

    const trackOffset = clamp(
        progressPosition
        - targetViewportPosition,
        -viewportHeight * 0.12,
        Math.max(
            0,
            trackHeight
            - viewportHeight * 0.88,
        ),
    );

    track.style.setProperty(
        "--reading-track-offset",
        `${trackOffset}px`,
    );

    updateTrackPaths({
        svg: trackSvg,
        basePath: trackBasePath,
        readPath: trackReadPath,
        trackHeight,
        bendCenter,
        progressPosition,
        progress,
    });

    const activeSection =
        sections[activeIndex];

    if (!activeSection) {
        trackSummary?.classList.remove(
            "is-visible",
        );

        return;
    }

    if (trackSummary) {
        trackSummary.style.top =
            `${activeSection.trackPosition}px`;

        trackSummary.classList.add(
            "is-visible",
        );
    }

    if (summaryTitle) {
        summaryTitle.textContent =
            activeSection.heading
                .textContent
                ?.trim()
            || "";
    }

    if (summaryProgress) {
        summaryProgress.textContent =
            `${Math.round(progress)}%`;
    }
}


function updateTrackPaths({
    svg,
    basePath,
    readPath,
    trackHeight,
    bendCenter,
    progressPosition,
    progress,
}) {
    if (
        !svg
        || !basePath
        || !readPath
    ) {
        return;
    }

    svg.setAttribute(
        "viewBox",
        `0 0 54 ${trackHeight}`,
    );

    const centerX = 27;
    const phase = progress * 0.075;

    const direction =
        Math.sin(phase) >= 0
            ? 1
            : -1;

    const amplitude =
        10
        + Math.sin(phase * 0.7) * 2.5;

    const halfHeight =
        58
        + Math.cos(phase * 0.55) * 8;

    const curveStart = clamp(
        bendCenter - halfHeight,
        0,
        trackHeight,
    );

    const curveEnd = clamp(
        bendCenter + halfHeight,
        0,
        trackHeight,
    );

    const controlX =
        centerX
        + amplitude * direction;

    const fullPath = [
        `M ${centerX} 0`,
        `L ${centerX} ${curveStart}`,

        `C ${centerX} ${
            curveStart
            + halfHeight * 0.28
        },`,

        `${controlX} ${
            bendCenter
            - halfHeight * 0.24
        },`,

        `${controlX} ${bendCenter}`,

        `C ${controlX} ${
            bendCenter
            + halfHeight * 0.24
        },`,

        `${centerX} ${
            curveEnd
            - halfHeight * 0.28
        },`,

        `${centerX} ${curveEnd}`,
        `L ${centerX} ${trackHeight}`,
    ].join(" ");

    basePath.setAttribute(
        "d",
        fullPath,
    );

    readPath.setAttribute(
        "d",
        fullPath,
    );

    let pathLength = 0;

    try {
        pathLength =
            basePath.getTotalLength();
    } catch (error) {
        console.error(
            "计算阅读轨迹长度失败：",
            error,
        );

        return;
    }

    const readRatio = clamp(
        progressPosition / trackHeight,
        0,
        1,
    );

    readPath.style.strokeDasharray =
        `${pathLength} ${pathLength}`;

    readPath.style.strokeDashoffset =
        `${pathLength * (1 - readRatio)}`;
}


function updateMovingToc({
    sections,
    activeIndex,
    toc,
    tocViewport,
}) {
    if (
        !toc
        || !tocViewport
        || activeIndex < 0
    ) {
        return;
    }

    const activeLink =
        sections[activeIndex]?.tocLink;

    if (!activeLink) {
        return;
    }

    const viewportHeight =
        tocViewport.clientHeight;

    const linkCenter =
        activeLink.offsetTop
        + activeLink.offsetHeight / 2;

    const targetCenter =
        viewportHeight * 0.48;

    const maximumOffset =
        Math.max(
            0,
            toc.scrollHeight
            - viewportHeight * 0.82,
        );

    const tocOffset = clamp(
        linkCenter - targetCenter,
        -viewportHeight * 0.1,
        maximumOffset,
    );

    toc.style.setProperty(
        "--reading-toc-offset",
        `${tocOffset}px`,
    );
}


function updateProgressDisplay({
    progress,
    progressCircle,
    progressText,
}) {
    if (progressCircle) {
        progressCircle.style.setProperty(
            "--reading-progress",
            `${progress * 3.6}deg`,
        );
    }

    if (progressText) {
        progressText.textContent =
            `${Math.round(progress)}%`;
    }
}


function clamp(
    value,
    minimum,
    maximum,
) {
    return Math.min(
        maximum,
        Math.max(
            minimum,
            value,
        ),
    );
}