document.addEventListener("DOMContentLoaded", function() {

    const monthYearEl = document.getElementById("monthYear");
    const calendarDaysEl = document.getElementById("calendarDays");
    const prevMonthBtn = document.getElementById("prevMonth");
    const nextMonthBtn = document.getElementById("nextMonth");

    let currentDate = new Date();
    let currentMonth = currentDate.getMonth();
    let currentYear = currentDate.getFullYear();

    function renderCalendar() {
        calendarDaysEl.innerHTML = '';

        const firstDay = new Date(currentYear, currentMonth, 1).getDay();
        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
        const startOffset = firstDay === 0 ? 6 : firstDay - 1;

        const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        monthYearEl.textContent = `${monthNames[currentMonth]} ${currentYear}`;

        for (let i = 0; i < startOffset; i++) {
            const emptyCell = document.createElement("div");
            calendarDaysEl.appendChild(emptyCell);
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const dayCell = document.createElement("button");
            dayCell.textContent = day;
            dayCell.classList.add("py-1", "cursor-pointer", "hover:bg-gray-200", "rounded");

            const today = new Date();
            if (day === today.getDate() && currentMonth === today.getMonth() && currentYear === today.getFullYear()) {
                dayCell.classList.add("bg-blue-500", "text-white", "rounded-full", "w-6", "h-6", "flex", "items-center", "justify-center", "mx-auto");
            } else {
                dayCell.classList.add("text-gray-700");
            }

            const formattedDate = `${currentYear}/${String(currentMonth + 1).padStart(2, "0")}/${String(day).padStart(2, "0")}`;
            dayCell.setAttribute("hx-get", `/calendar/${formattedDate}`);
            dayCell.setAttribute("hx-target", "#date-info");
            dayCell.setAttribute("hx-swap", "innerHTML");

            calendarDaysEl.appendChild(dayCell);
        }

        if (window.htmx) {
            htmx.process(calendarDaysEl);
        }
    }

    prevMonthBtn.addEventListener("click", function() {
        currentMonth--;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        }
        renderCalendar();
    });

    nextMonthBtn.addEventListener("click", function() {
        currentMonth++;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        renderCalendar();
    });

    renderCalendar();

    const today = new Date();
    if (today.getMonth() === currentMonth && today.getFullYear() === currentYear) {
        const dayButtons = calendarDaysEl.querySelectorAll("button");
        dayButtons.forEach(button => {
            if (parseInt(button.textContent, 10) === today.getDate()) {
                button.click();
            }
        });
    }
});
