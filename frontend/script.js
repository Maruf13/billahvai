const API_BASE_URL = "http://localhost:8000";

async function searchPDFs() {
    const keyword = document.getElementById("keyword").value;
    if (!keyword) {
        alert("Please enter a keyword!");
        return;
    }

    const response = await fetch(`${API_BASE_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keyword }),
    });

    const data = await response.json();
    displayResults(data.results);
}

async function highlightPDFs() {
    const keyword = document.getElementById("keyword").value;
    if (!keyword) {
        alert("Please enter a keyword!");
        return;
    }

    const response = await fetch(`${API_BASE_URL}/highlight`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keyword }),
    });

    const data = await response.json();
    displayResults(data.annotated_files, true);
}

function displayResults(files, isHighlight = false) {
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "";

    if (!files.length) {
        resultsDiv.innerHTML = "<p>No matches found.</p>";
        return;
    }

    files.forEach((file) => {
        const div = document.createElement("div");
        div.className = "result-item";

        // Make files clickable (open in browser or download)
        div.innerHTML = `<a href="${API_BASE_URL}${file}" target="_blank">${file}</a>`;

        resultsDiv.appendChild(div);
    });
}
