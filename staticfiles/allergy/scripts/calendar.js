document.addEventListener("DOMContentLoaded", function () {

    const monthYearEl = document.getElementById("monthYear");
    const calendarDaysEl = document.getElementById("calendarDays");
    const prevMonthBtn = document.getElementById("prevMonth");
    const nextMonthBtn = document.getElementById("nextMonth");

    let currentDate = new Date();
    let currentMonth = currentDate.getMonth();
    let currentYear = currentDate.getFullYear();
    let selectedDate = null;
    let initialSelectedDate = null;

    const monthNames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];

    function renderCalendar() {
        calendarDaysEl.innerHTML = '';

        const firstDay = new Date(currentYear, currentMonth, 1).getDay();
        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
        const startOffset = firstDay === 0 ? 6 : firstDay - 1;

        monthYearEl.textContent = `${monthNames[currentMonth]} ${currentYear}`;

        for (let i = 0; i < startOffset; i++) {
            calendarDaysEl.appendChild(document.createElement("div"));
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const dayCell = createDayCell(day);

            if (
                initialSelectedDate &&
                initialSelectedDate.year === currentYear &&
                initialSelectedDate.month === currentMonth &&
                initialSelectedDate.day === day
            ) {
                setSelectedDate(dayCell);
                triggerDateSelectedEvent(dayCell);
            }

            calendarDaysEl.appendChild(dayCell);
        }

        if (window.htmx) {
            htmx.process(calendarDaysEl);
        }
    }

    function createDayCell(day) {
        const dayCell = document.createElement("button");
        dayCell.textContent = day;
        dayCell.classList.add("py-1", "cursor-pointer", "hover:bg-gray-200", "rounded");

        const formattedDate = `${currentYear}/${String(currentMonth + 1).padStart(2, "0")}/${String(day).padStart(2, "0")}`;
        dayCell.setAttribute("hx-get", `/calendar/${formattedDate}/`);
        dayCell.setAttribute("hx-target", "#date-info");
        dayCell.setAttribute("hx-swap", "innerHTML");

        if (
            !initialSelectedDate &&
            currentDate.getDate() === day &&
            currentDate.getMonth() === currentMonth &&
            currentDate.getFullYear() === currentYear
        ) {
            setSelectedDate(dayCell);
            triggerDateSelectedEvent(dayCell);
        }

        dayCell.addEventListener('click', function () {
            handleDayCellClick(dayCell, day);
        });

        return dayCell;
    }

    function setSelectedDate(dayCell) {
        if (selectedDate) {
            selectedDate.classList.remove(
                "bg-blue-500",
                "text-white",
                "rounded-full",
                "w-6",
                "h-6",
                "flex",
                "items-center",
                "justify-center",
                "mx-auto"
            );
            selectedDate.classList.add("text-gray-700");
        }

        selectedDate = dayCell;
        selectedDate.classList.add(
            "bg-blue-500",
            "text-white",
            "rounded-full",
            "w-6",
            "h-6",
            "flex",
            "items-center",
            "justify-center",
            "mx-auto"
        );
    }

    function handleDayCellClick(dayCell, day) {
        triggerDateSelectedEvent(dayCell);

        initialSelectedDate = {
            year: currentYear,
            month: currentMonth,
            day: day
        };

        setSelectedDate(dayCell);
    }

    function triggerDateSelectedEvent(dayCell) {
        const day = parseInt(dayCell.textContent);
        const date = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

        document.dispatchEvent(new CustomEvent('dateSelected', {
            detail: {
                dayCell: dayCell,
                date: date
            }
        }));
    }

    function changeMonth(increment) {
        currentMonth += increment;

        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        } else if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        }

        renderCalendar();
    }

    prevMonthBtn.addEventListener("click", () => changeMonth(-1));
    nextMonthBtn.addEventListener("click", () => changeMonth(1));

    renderCalendar();
});
