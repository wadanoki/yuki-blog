(() => {
    const clockElement =
        document.querySelector("#dashboard-clock");

    const dateElement =
        document.querySelector("#dashboard-date");

    if (!clockElement && !dateElement) {
        return;
    }

    const formatter = new Intl.DateTimeFormat(
        "zh-CN",
        {
            year: "numeric",
            month: "long",
            day: "numeric",
            weekday: "long",
        },
    );

    const updateClock = () => {
        const now = new Date();

        if (clockElement) {
            clockElement.textContent =
                now.toLocaleTimeString(
                    "zh-CN",
                    {
                        hour12: false,
                    },
                );
        }

        if (dateElement) {
            dateElement.textContent =
                formatter.format(now);
        }
    };

    updateClock();

    window.setInterval(
        updateClock,
        1000,
    );
})();