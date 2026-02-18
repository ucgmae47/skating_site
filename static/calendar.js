let isAdmin = false;

fetch('/is_admin')
    .then(response => response.json())
    .then(data => {
        isAdmin = data.admin;
        renderCalendar();
        updateMonth(currentDate.getMonth(), currentDate.getFullYear());
    });

const monthLabel = document.getElementById("monthLabel");
const calendarGrid = document.getElementById("calendarGrid");

let currentDate = new Date();

function renderCalendar() {
    calendarGrid.innerHTML = "";

    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    monthLabel.textContent = currentDate.toLocaleString("default", {
        month: "long",
        year: "numeric"
    });

    for (let i = 0; i < firstDay; i++) {
        calendarGrid.appendChild(document.createElement("div"));
    }

    for (let day = 1; day <= daysInMonth; day++) {
        const cell = document.createElement("div");
        cell.classList.add("calendar-day");
        cell.textContent = day;

        const d = (firstDay + day - 1) % 7;
        const isWeekday = isNormalPractice(d);

        if (isWeekday) {
            cell.classList.add("selected");
        }

        if (isAdmin) {
            cell.onclick = () => {
                if (isWeekday && cell.classList.contains("selected")) {
                    sendData(day, month, year, true);
                } else if (!isWeekday && !cell.classList.contains("selected")) {
                    sendData(day, month, year, true);
                } else {
                    sendData(day, month, year, false);
                }
                cell.classList.toggle("selected")
            };
        }
        calendarGrid.appendChild(cell);
    }
}

document.getElementById("prevMonth").onclick = () => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    renderCalendar();
    updateMonth(currentDate.getMonth(), currentDate.getFullYear());
};

document.getElementById("nextMonth").onclick = () => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar();
    updateMonth(currentDate.getMonth(), currentDate.getFullYear());
};

function sendData(day, month, year, add) {
    fetch('/update_calendar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
	    day: day,
	    month: month+1,
	    year: year,
	    add: add
	}),
    }).then(response => response.json());
}

function updateMonth(month, year) {
    fetch('/update_month', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            month: month+1,
	    year: year
        }),
    }).then(response => response.json())
    .then(data => {
        highlightDates(data["days"]);     
    });
}

function highlightDates(days) {
    const daySet = new Set(days);
    const dayDivs = document.querySelectorAll("#calendarGrid .calendar-day");

    dayDivs.forEach(div => {
        const dayNumber = parseInt(div.textContent, 10);
        const day = (new Date(currentDate.getFullYear(), currentDate.getMonth(), dayNumber)).getDay();
        if (daySet.has(dayNumber) && isNormalPractice(day)) {
            div.classList.remove("selected");
        } else if (daySet.has(dayNumber) && !isNormalPractice(day)) {
            div.classList.add("selected");
        }
    });
}

function isNormalPractice(d) {
    return d >= 1 && d <= 4;
}