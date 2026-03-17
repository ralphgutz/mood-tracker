/* ---------- State ---------- */
let selectedMood = null;
let editingEntryId = null;
let modalMood = null;

const MOOD_COLORS = { 1: "#E74C3C", 2: "#E67E22", 3: "#F1C40F", 4: "#2ECC71", 5: "#27AE60" };
const MOOD_LABELS = { 1: "Very Bad", 2: "Bad", 3: "Neutral", 4: "Good", 5: "Very Good" };

/* ---------- DOM refs ---------- */
const noteEl = document.getElementById("note");
const charCountEl = document.getElementById("char-count");
const entryDateEl = document.getElementById("entry-date");
const submitBtn = document.getElementById("submit-btn");
const entriesList = document.getElementById("entries-list");
const editModal = document.getElementById("edit-modal");
const modalNoteEl = document.getElementById("modal-note");

/* ---------- Init ---------- */
document.addEventListener("DOMContentLoaded", () => {
    entryDateEl.value = new Date().toISOString().slice(0, 10);
    loadEntries();
    setupNav();
    setupMoodSelector("mood-selector", (m) => { selectedMood = m; updateSubmitBtn(); });
    setupMoodSelector("modal-mood-selector", (m) => { modalMood = m; });
    noteEl.addEventListener("input", () => {
        charCountEl.textContent = noteEl.value.length;
        updateSubmitBtn();
    });
    submitBtn.addEventListener("click", submitEntry);
    document.getElementById("modal-cancel").addEventListener("click", closeModal);
    document.getElementById("modal-save").addEventListener("click", saveEdit);
    document.getElementById("modal-delete").addEventListener("click", deleteEntry);
    editModal.addEventListener("click", (e) => { if (e.target === editModal) closeModal(); });
});

/* ---------- Navigation ---------- */
function setupNav() {
    document.querySelectorAll(".nav-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".nav-btn").forEach((b) => b.classList.remove("active"));
            document.querySelectorAll(".section").forEach((s) => s.classList.remove("active"));
            btn.classList.add("active");
            const section = document.getElementById("section-" + btn.dataset.section);
            section.classList.add("active");

            if (btn.dataset.section === "trends") {
                loadTrendChart();
                setupWordCloud();
                setupSummary();
            } else if (btn.dataset.section === "calendar") {
                initCalendar();
            }
        });
    });
}

/* ---------- Mood Selector ---------- */
function setupMoodSelector(containerId, callback) {
    const container = document.getElementById(containerId);
    container.querySelectorAll(".mood-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            container.querySelectorAll(".mood-btn").forEach((b) => b.classList.remove("selected"));
            btn.classList.add("selected");
            callback(parseInt(btn.dataset.mood));
        });
    });
}

function updateSubmitBtn() {
    submitBtn.disabled = !(selectedMood && noteEl.value.trim().length > 0);
}

/* ---------- Submit Entry ---------- */
async function submitEntry() {
    submitBtn.disabled = true;
    const body = {
        mood: selectedMood,
        note: noteEl.value.trim(),
        date: entryDateEl.value,
    };

    const res = await fetch("/api/entries", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });

    const data = await res.json();
    if (!res.ok) {
        alert(data.error || "Failed to save entry.");
        submitBtn.disabled = false;
        return;
    }

    // Load music for the submitted mood before resetting
    const submittedMood = selectedMood;

    // Reset form
    selectedMood = null;
    noteEl.value = "";
    charCountEl.textContent = "0";
    document.querySelectorAll("#mood-selector .mood-btn").forEach((b) => b.classList.remove("selected"));
    entryDateEl.value = new Date().toISOString().slice(0, 10);
    updateSubmitBtn();
    loadEntries();
    loadMusic(submittedMood);
}

/* ---------- Load Entries ---------- */
async function loadEntries() {
    const res = await fetch("/api/entries?limit=20");
    const entries = await res.json();

    if (entries.length === 0) {
        entriesList.innerHTML = '<div class="empty-state">No entries yet — log your first mood above!</div>';
        return;
    }

    entriesList.innerHTML = entries.map((e) => `
        <div class="entry-item" data-id="${e.id}">
            <div class="entry-mood" style="background:${MOOD_COLORS[e.mood_rating]};${e.mood_rating === 3 ? "color:#2c3e50" : ""}">
                ${e.mood_rating}
            </div>
            <div class="entry-body">
                <div class="entry-date">${formatDate(e.entry_date)}</div>
                <div class="entry-note">${escapeHtml(e.note)}</div>
                <div class="entry-sentiment">
                    <span class="sentiment-badge ${e.sentiment_label}">${e.sentiment_label}</span>
                    <span style="color:var(--text-light)">${e.sentiment_score.toFixed(2)}</span>
                </div>
                <div class="entry-actions">
                    <button onclick="openEdit(${e.id})">Edit</button>
                    <button class="delete-btn" onclick="confirmDelete(${e.id})">Delete</button>
                </div>
            </div>
        </div>
    `).join("");
}

/* ---------- Edit Modal ---------- */
function openEdit(id) {
    fetch(`/api/entries/${id}`)
        .then((r) => r.json())
        .then((entry) => {
            editingEntryId = id;
            modalMood = entry.mood_rating;
            modalNoteEl.value = entry.note;
            document.getElementById("modal-title").textContent = `Edit Entry — ${formatDate(entry.entry_date)}`;

            document.querySelectorAll("#modal-mood-selector .mood-btn").forEach((b) => {
                b.classList.toggle("selected", parseInt(b.dataset.mood) === entry.mood_rating);
            });

            editModal.classList.add("open");
        });
}

function closeModal() {
    editModal.classList.remove("open");
    editingEntryId = null;
}

async function saveEdit() {
    if (!modalMood || !modalNoteEl.value.trim()) {
        alert("Please select a mood and write a note.");
        return;
    }

    const res = await fetch(`/api/entries/${editingEntryId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mood: modalMood, note: modalNoteEl.value.trim() }),
    });

    if (!res.ok) {
        const data = await res.json();
        alert(data.error || "Failed to update.");
        return;
    }

    closeModal();
    loadEntries();
}

async function deleteEntry() {
    if (!confirm("Delete this entry?")) return;
    await fetch(`/api/entries/${editingEntryId}`, { method: "DELETE" });
    closeModal();
    loadEntries();
}

function confirmDelete(id) {
    if (!confirm("Delete this entry?")) return;
    fetch(`/api/entries/${id}`, { method: "DELETE" }).then(() => loadEntries());
}

/* ---------- Word Cloud ---------- */
let wcInitialized = false;
function setupWordCloud() {
    if (wcInitialized) return;
    wcInitialized = true;
    document.getElementById("wc-generate").addEventListener("click", loadWordCloud);
}

async function loadWordCloud() {
    const start = document.getElementById("wc-start").value;
    const end = document.getElementById("wc-end").value;
    const params = new URLSearchParams();
    if (start) params.set("start_date", start);
    if (end) params.set("end_date", end);

    const res = await fetch(`/api/analytics/wordcloud?${params}`);
    const words = await res.json();
    const container = document.getElementById("wordcloud-container");

    if (words.length === 0) {
        container.innerHTML = '<div class="empty-state">No words found for this range.</div>';
        return;
    }

    const maxCount = Math.max(...words.map((w) => w.count));
    const colors = ["#3498db", "#e74c3c", "#2ecc71", "#9b59b6", "#e67e22", "#1abc9c", "#f39c12", "#34495e"];

    container.innerHTML = words.map((w, i) => {
        const size = 0.7 + (w.count / maxCount) * 2.0;
        const color = colors[i % colors.length];
        return `<span class="wc-word" style="font-size:${size}rem;color:${color}" title="${w.count} times">${escapeHtml(w.text)}</span>`;
    }).join("");
}

/* ---------- Weekly Summary ---------- */
let summaryInitialized = false;
function setupSummary() {
    if (summaryInitialized) return;
    summaryInitialized = true;
    document.getElementById("summary-btn").addEventListener("click", loadSummary);
}

async function loadSummary() {
    const res = await fetch("/api/analytics/summary");
    const data = await res.json();
    const container = document.getElementById("summary-content");

    if (!data.has_data) {
        container.innerHTML = '<div class="empty-state" style="margin-top:1rem">No entries in the last 7 days.</div>';
        return;
    }

    const trendIcon = data.trend === "improving" ? "&#9650;" : data.trend === "declining" ? "&#9660;" : "&#9644;";
    const trendColor = data.trend === "improving" ? "var(--mood-5)" : data.trend === "declining" ? "var(--mood-1)" : "var(--mood-3)";

    container.innerHTML = `
        <div class="summary-grid">
            <div class="summary-stat">
                <div class="value">${data.avg_mood}</div>
                <div class="label">Avg Mood</div>
            </div>
            <div class="summary-stat">
                <div class="value">${data.avg_sentiment}</div>
                <div class="label">Avg Sentiment</div>
            </div>
            <div class="summary-stat">
                <div class="value">${data.num_entries}</div>
                <div class="label">Entries</div>
            </div>
            <div class="summary-stat">
                <div class="value" style="color:${trendColor}">${trendIcon}</div>
                <div class="label">Trend: ${data.trend}</div>
            </div>
        </div>
        <p style="margin-top:0.75rem"><strong>Best day:</strong> ${formatDate(data.best_day.date)} (mood ${data.best_day.mood})</p>
        <p><strong>Worst day:</strong> ${formatDate(data.worst_day.date)} (mood ${data.worst_day.mood})</p>
        ${data.top_words.length ? `<p style="margin-top:0.5rem"><strong>Top words:</strong></p><div class="top-words">${data.top_words.map((w) => `<span>${escapeHtml(w)}</span>`).join("")}</div>` : ""}
    `;
}

/* ---------- Helpers ---------- */
function formatDate(dateStr) {
    const d = new Date(dateStr + "T00:00:00");
    return d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", year: "numeric" });
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

/* ---------- Music Recommendations ---------- */
async function loadMusic(mood) {
    const card = document.getElementById("music-card");
    const container = document.getElementById("music-tracks");

    try {
        const res = await fetch(`/api/music?mood=${mood}`);
        if (!res.ok) {
            card.style.display = "none";
            return;
        }
        const tracks = await res.json();
        if (!tracks.length) {
            card.style.display = "none";
            return;
        }

        container.innerHTML = tracks.map((t) => `
            <div class="music-track">
                <img src="${escapeHtml(t.album_image)}" alt="Album art">
                <div class="music-info">
                    <div class="song-name">${escapeHtml(t.name)}</div>
                    <div class="artist">${escapeHtml(t.artist)}</div>
                </div>
            </div>
            <div class="music-embed">
                <iframe src="${escapeHtml(t.embed_url)}" width="100%" height="80" allow="encrypted-media"></iframe>
            </div>
        `).join("");

        card.style.display = "block";
    } catch {
        card.style.display = "none";
    }
}
