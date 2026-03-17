/* ---------- Trend Chart ---------- */
let trendChart = null;
let trendInitialized = false;

function loadTrendChart(days = "30") {
    if (!trendInitialized) {
        trendInitialized = true;
        document.getElementById("trend-filters").addEventListener("click", (e) => {
            if (!e.target.classList.contains("filter-btn")) return;
            document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
            e.target.classList.add("active");
            loadTrendChart(e.target.dataset.days);
        });
    }

    fetch(`/api/analytics/trends?days=${days}`)
        .then((r) => r.json())
        .then((data) => renderTrendChart(data));
}

function renderTrendChart(data) {
    const ctx = document.getElementById("trend-chart");

    if (trendChart) {
        trendChart.destroy();
    }

    if (data.dates.length === 0) {
        ctx.parentElement.innerHTML = '<div class="empty-state" style="padding:4rem 0">No entries yet — log your first mood to see trends!</div>';
        return;
    }

    const labels = data.dates.map((d) => {
        const dt = new Date(d + "T00:00:00");
        return dt.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    });

    trendChart = new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [
                {
                    label: "Mood Rating",
                    data: data.mood_ratings,
                    borderColor: "#3498db",
                    backgroundColor: "rgba(52,152,219,0.1)",
                    fill: true,
                    tension: 0.3,
                    yAxisID: "y",
                    pointRadius: 4,
                    pointHoverRadius: 6,
                },
                {
                    label: "Sentiment Score",
                    data: data.sentiment_scores,
                    borderColor: "#e67e22",
                    backgroundColor: "rgba(230,126,34,0.1)",
                    fill: true,
                    tension: 0.3,
                    yAxisID: "y1",
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    borderDash: [5, 5],
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "index",
                intersect: false,
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        afterBody(context) {
                            const idx = context[0].dataIndex;
                            const note = data.notes[idx];
                            return note ? "\n" + note.substring(0, 80) + (note.length > 80 ? "..." : "") : "";
                        },
                    },
                },
            },
            scales: {
                y: {
                    type: "linear",
                    position: "left",
                    min: 1,
                    max: 5,
                    title: { display: true, text: "Mood Rating" },
                    ticks: { stepSize: 1 },
                },
                y1: {
                    type: "linear",
                    position: "right",
                    min: -1,
                    max: 1,
                    title: { display: true, text: "Sentiment" },
                    grid: { drawOnChartArea: false },
                },
            },
        },
    });
}
