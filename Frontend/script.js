const API_BASE = "http://127.0.0.1:8000";

let currentReportId = null;

const serverStatus = document.getElementById("serverStatus");
const candidateType = document.getElementById("candidateType");
const targetCompany = document.getElementById("targetCompany");
const targetField = document.getElementById("targetField");
const experienceYears = document.getElementById("experienceYears");
const preferredRole = document.getElementById("preferredRole");
const resumeInput = document.getElementById("resumeInput");
const fileName = document.getElementById("fileName");
const jobDescription = document.getElementById("jobDescription");
const analyzeBtn = document.getElementById("analyzeBtn");
const downloadBtn = document.getElementById("downloadBtn");
const shareBtn = document.getElementById("shareBtn");

resumeInput.addEventListener("change", () => {
    if (resumeInput.files.length > 0) {
        fileName.textContent = resumeInput.files[0].name;
    } else {
        fileName.textContent = "PDF, DOCX, or TXT supported";
    }
});

async function checkServer() {
    try {
        const response = await fetch(`${API_BASE}/health`);

        if (!response.ok) {
            throw new Error("Offline");
        }

        serverStatus.textContent = "Server Online";
        serverStatus.classList.remove("offline");
        serverStatus.classList.add("online");

    } catch {
        serverStatus.textContent = "Server Offline";
        serverStatus.classList.remove("online");
        serverStatus.classList.add("offline");
    }
}

analyzeBtn.addEventListener("click", async (event) => {
    event.preventDefault();

    const file = resumeInput.files[0];
    const jd = jobDescription.value.trim();

    if (!file) {
        alert("Please upload your resume.");
        return;
    }

    if (!jd) {
        alert("Please paste the job description.");
        return;
    }

    const formData = new FormData();

    formData.append("file", file);
    formData.append("job_description", jd);
    formData.append("candidate_type", candidateType.value);
    formData.append("target_field", targetField.value);
    formData.append("experience_years", experienceYears.value || "0");
    formData.append("preferred_role", preferredRole.value || "");
    formData.append("target_company", targetCompany.value);

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Scanning Resume...";
    downloadBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/analyze`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Analysis failed.");
        }

        currentReportId = data.analysis_id;

        renderResult(data);

        downloadBtn.disabled = false;

    } catch (error) {
        console.error(error);
        alert("Error: " + error.message);

    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analyze Resume";
    }
});

downloadBtn.addEventListener("click", () => {
    if (!currentReportId) {
        alert("Please run analysis first.");
        return;
    }

    window.open(`${API_BASE}/download-report/${currentReportId}`, "_blank");
});

shareBtn.addEventListener("click", async () => {
    const score = document.getElementById("overallScore").textContent;
    const field = document.getElementById("bestField").textContent;

    const text = `My ATSLens resume analysis score is ${score}. Best fit field: ${field}.`;

    try {
        await navigator.clipboard.writeText(text);
        alert("Report summary copied to clipboard.");

    } catch {
        alert(text);
    }
});

function renderResult(data) {

    document.getElementById("resultSubtitle").textContent =
        "Your resume has been analyzed successfully.";

    setOverallScore(
        data.score,
        data.grade,
        data.verdict,
        data.summary
    );

    setMetric("structure", data.breakdown.structure, 20);
    setMetric("skills", data.breakdown.skills, 20);
    setMetric("tech", data.breakdown.technologies, 20);
    setMetric("projects", data.breakdown.projects, 20);
    setMetric("experience", data.breakdown.experience, 20);
    setMetric("education", data.breakdown.education, 10);
    setMetric("keywords", data.breakdown.keywords, 10);
    setMetric("formatting", data.breakdown.formatting, 10);

    document.getElementById("profileName").textContent =
        "ATS Evaluation Report";

    document.getElementById("profileRole").textContent =
        `${data.target_field} | ${data.candidate_type}`;

    document.getElementById("profileMeta").textContent =
        `Resume: ${data.filename}`;

    document.getElementById("mncChance").textContent =
        `${data.mnc_chance}%`;

    document.getElementById("mncLabel").textContent =
        data.mnc_label;

    document.getElementById("mncText").textContent =
        data.mnc_message;

    renderList("matchedSkills", data.matched_skills);
    renderList("missingSkills", data.missing_skills);
    renderList("keyStrengths", data.key_strengths);

    renderFieldMatches(data.field_matches);
    renderTable(data);
    renderRoadmap(data.roadmap);

    document.getElementById("finalVerdict").textContent =
        data.verdict;

    document.getElementById("finalAdvice").textContent =
        data.final_advice;

    document.getElementById("finalGrade").textContent =
        data.grade;

    document.getElementById("resultPanel")
        .scrollIntoView({ behavior: "smooth" });
}

function setOverallScore(score, grade, verdict, summary) {

    const degree = Math.round((score / 100) * 360);

    document.getElementById("overallRing").style.background =
        `conic-gradient(#22c55e 0deg, #2563eb ${degree}deg, #e8eef9 ${degree}deg)`;

    document.getElementById("overallScore").textContent =
        `${score}%`;

    document.getElementById("gradeText").textContent =
        `${grade} • ${verdict}`;

    document.getElementById("scoreMessage").textContent =
        summary;

    document.querySelector(".mini-ring").style.background =
        `conic-gradient(#22c55e ${degree}deg, rgba(255,255,255,0.25) ${degree}deg)`;

    document.querySelector(".mini-ring span").textContent =
        `${score}%`;
}

function setMetric(prefix, value, max) {

    const degree = Math.round((value / max) * 360);
    const percentage = Math.round((value / max) * 100);

    document.getElementById(`${prefix}Ring`).style.background =
        `conic-gradient(#2563eb ${degree}deg, #e8eef9 ${degree}deg)`;

    document.getElementById(`${prefix}Score`).textContent =
        `${value}/${max}`;

    let status = "Needs Work";

    if (percentage >= 85) {
        status = "Excellent";
    } else if (percentage >= 70) {
        status = "Great";
    } else if (percentage >= 55) {
        status = "Good";
    }

    document.getElementById(`${prefix}Status`).textContent =
        status;
}

function renderList(id, items) {

    const ul = document.getElementById(id);

    ul.innerHTML = "";

    if (!items || items.length === 0) {

        const li = document.createElement("li");
        li.textContent = "No data found";
        ul.appendChild(li);

        return;
    }

    items.slice(0, 10).forEach(item => {

        const li = document.createElement("li");
        li.textContent = item;

        ul.appendChild(li);
    });
}

function renderFieldMatches(matches) {

    const bestField = document.getElementById("bestField");
    const bestFieldPercent = document.getElementById("bestFieldPercent");
    const fieldMatches = document.getElementById("fieldMatches");

    fieldMatches.innerHTML = "";

    if (!matches || matches.length === 0) {

        bestField.textContent = "Not Analyzed";
        bestFieldPercent.textContent = "0% Match";

        return;
    }

    bestField.textContent = matches[0].field;

    bestFieldPercent.textContent =
        `${matches[0].match}% Match`;

    matches.slice(0, 4).forEach(item => {

        const row = document.createElement("div");

        row.className = "field-row";

        row.innerHTML = `
            <span>${item.field}</span>
            <span>${item.match}%</span>
        `;

        fieldMatches.appendChild(row);
    });
}

function renderTable(data) {

    const rows = [
        ["Resume Structure", data.breakdown.structure, 20],
        ["Skills", data.breakdown.skills, 20],
        ["Technologies", data.breakdown.technologies, 20],
        ["Projects", data.breakdown.projects, 20],
        ["Experience", data.breakdown.experience, 20],
        ["Education", data.breakdown.education, 10],
        ["Keywords", data.breakdown.keywords, 10],
        ["Formatting & Readability", data.breakdown.formatting, 10]
    ];

    const tbody = document.getElementById("scoreTable");

    tbody.innerHTML = "";

    rows.forEach(row => {

        const percentage =
            Math.round((row[1] / row[2]) * 100);

        const performance =
            getPerformance(percentage);

        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${row[0]}</td>
            <td>${row[1]}</td>
            <td>${row[2]}</td>
            <td>${percentage}%</td>
            <td>${performance}</td>
        `;

        tbody.appendChild(tr);
    });

    const totalRow = document.createElement("tr");

    totalRow.innerHTML = `
        <td><b>Total</b></td>
        <td><b>${data.total_obtained}</b></td>
        <td><b>${data.total_marks}</b></td>
        <td><b>${data.score}%</b></td>
        <td><b>${data.verdict}</b></td>
    `;

    tbody.appendChild(totalRow);
}

function renderRoadmap(roadmap) {

    const ol = document.getElementById("roadmapList");

    ol.innerHTML = "";

    if (!roadmap || roadmap.length === 0) {

        const li = document.createElement("li");
        li.textContent = "No roadmap available.";

        ol.appendChild(li);

        return;
    }

    roadmap.forEach(item => {

        const li = document.createElement("li");

        li.textContent = item;

        ol.appendChild(li);
    });
}

function getPerformance(percentage) {

    if (percentage >= 85) {
        return "Excellent";
    }

    if (percentage >= 70) {
        return "Very Good";
    }

    if (percentage >= 55) {
        return "Good";
    }

    return "Needs Work";
}

checkServer();

setInterval(checkServer, 5000);