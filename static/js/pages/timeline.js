export function setupTimelinePage() {
    const todayProgressElement =
        document.querySelector("#today-progress");

    const yearProgressElement =
        document.querySelector("#year-progress");

    if (
        !todayProgressElement
        && !yearProgressElement
    ) {
        return;
    }

    const updateProgress = () => {
        const now = new Date();

        if (todayProgressElement) {
            const todayProgress =
                calculateTodayProgress(now);

            todayProgressElement.textContent =
                `${todayProgress.toFixed(2)}%`;
        }

        if (yearProgressElement) {
            const yearProgress =
                calculateYearProgress(now);

            yearProgressElement.textContent =
                `${yearProgress.toFixed(2)}%`;
        }
    };

    updateProgress();

    /*
     * 每秒更新一次。
     * 今日进度的小数部分会持续变化。
     */
    const timerId = window.setInterval(
        updateProgress,
        1000,
    );

    /*
     * 页面被浏览器缓存恢复时重新计算，
     * 避免返回页面后显示旧时间。
     */
    window.addEventListener(
        "pageshow",
        updateProgress,
    );

    /*
     * 页面隐藏时可以清理定时器。
     */
    window.addEventListener(
        "pagehide",
        () => {
            window.clearInterval(timerId);
        },
        { once: true },
    );
}


function calculateTodayProgress(now) {
    const startOfDay = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        0,
        0,
        0,
        0,
    );

    const startOfNextDay = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate() + 1,
        0,
        0,
        0,
        0,
    );

    const elapsed =
        now.getTime()
        - startOfDay.getTime();

    const total =
        startOfNextDay.getTime()
        - startOfDay.getTime();

    return clamp(
        elapsed / total * 100,
        0,
        100,
    );
}


function calculateYearProgress(now) {
    const startOfYear = new Date(
        now.getFullYear(),
        0,
        1,
        0,
        0,
        0,
        0,
    );

    const startOfNextYear = new Date(
        now.getFullYear() + 1,
        0,
        1,
        0,
        0,
        0,
        0,
    );

    const elapsed =
        now.getTime()
        - startOfYear.getTime();

    const total =
        startOfNextYear.getTime()
        - startOfYear.getTime();

    return clamp(
        elapsed / total * 100,
        0,
        100,
    );
}


function clamp(value, minimum, maximum) {
    return Math.min(
        maximum,
        Math.max(minimum, value),
    );
}