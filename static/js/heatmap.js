/* ---------- Calendar Heatmap ---------- */
const MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
];
const DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MOOD_COLORS_CAL = { 1: "mood-1", 2: "mood-2", 3: "mood-3", 4: "mood-4", 5: "mood-5" };

let calYear, calMonth;
let calInitialized = false;

function initCalendar() {
    if (!calInitialized) {
        calInitialized = true;
        const now = new Date();
        calYear = now.getFullYear();
        calMonth = now.getMonth() + 1;

        document.getElementById("cal-prev").addEventListener("click", () => {
            calMonth--;
            if (calMonth < 1) { calMonth = 12; calYear--; }
            renderCalendar();
        });
        document.getElementById("cal-next").addEventListener("click", () => {
            calMonth++;
            if (calMonth > 12) { calMonth = 1; calYear++; }
            renderCalendar();
        });
    }
    renderCalendar();
}

async function renderCalendar() {
    document.getElementById("cal-title").textContent = `${MONTH_NAMES[calMonth - 1]} ${calYear}`;

    const res = await fetch(`/api/analytics/heatmap?year=${calYear}&month=${calMonth}`);
    const data = await res.json();

    const grid = document.getElementById("calendar-grid");
    let html = DAY_NAMES.map((d) => `<div class="calendar-header">${d}</div>`).join("");

    const firstDay = new Date(calYear, calMonth - 1, 1).getDay();
    const daysInMonth = new Date(calYear, calMonth, 0).getDate();

    // Empty cells before first day
    for (let i = 0; i < firstDay; i++) {
        html += '<div class="calendar-day empty"></div>';
    }

    for (let d = 1; d <= daysInMonth; d++) {
        const dateStr = `${calYear}-${String(calMonth).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
        const mood = data[dateStr];

        if (mood) {
            html += `<div class="calendar-day has-entry ${MOOD_COLORS_CAL[mood]}" data-date="${dateStr}" title="Mood: ${mood}">${d}</div>`;
        } else {
            html += `<div class="calendar-day no-entry" data-date="${dateStr}">${d}</div>`;
        }
    }

    grid.innerHTML = html;

    // Click handler for days with entries
    grid.querySelectorAll(".calendar-day.has-entry").forEach((el) => {
        el.addEventListener("click", () => {
            const dateStr = el.dataset.date;
            // Fetch entry for that date and open edit modal
            fetch(`/api/entries?start_date=${dateStr}&end_date=${dateStr}&limit=1`)
                .then((r) => r.json())
                .then((entries) => {
                    if (entries.length > 0) {
                        openEdit(entries[0].id);
                    }
                });
        });
    });
}
