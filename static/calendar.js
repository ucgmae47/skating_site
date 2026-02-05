
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

	cell.onclick = () => {
	    cell.classList.toggle("selected")

	    if (cell.classList.contains("selected")) {
		sendData(day, month, year, true);
	    } else {
		sendData(day, month, year, false);
	    }
	};

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

renderCalendar();
updateMonth(currentDate.getMonth(), currentDate.getFullYear());

function sendData(day, month, year, add) {
    fetch('http://127.0.0.1:8000/update_calendar', {
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
    fetch('http://127.0.0.1:8000/update_month', {
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

        if (daySet.has(dayNumber)) {
            div.classList.add("selected");
        } else {
            div.classList.remove("selected");
        }
    });
}
