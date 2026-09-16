const API_BASE = "https://atslens.onrender.com";

let currentReportId = null;


/* =========================================================
   DOM ELEMENTS
========================================================= */

const serverStatus =
    document.getElementById("serverStatus");

const candidateType =
    document.getElementById("candidateType");

const targetCompany =
    document.getElementById("targetCompany");

const targetField =
    document.getElementById("targetField");

const experienceYears =
    document.getElementById("experienceYears");

const preferredRole =
    document.getElementById("preferredRole");

const resumeInput =
    document.getElementById("resumeInput");

const fileName =
    document.getElementById("fileName");

const jobDescription =
    document.getElementById("jobDescription");

const analyzeBtn =
    document.getElementById("analyzeBtn");

const downloadBtn =
    document.getElementById("downloadBtn");

const shareBtn =
    document.getElementById("shareBtn");


/* =========================================================
   FILE UPLOAD
========================================================= */

resumeInput.addEventListener("change", () => {

    if (resumeInput.files.length > 0) {

        const file = resumeInput.files[0];

        fileName.textContent = file.name;

    } else {

        fileName.textContent =
            "PDF, DOCX, or TXT supported";

    }

});


/* =========================================================
   SERVER STATUS
========================================================= */

async function checkServer() {

    try {

        const response =
            await fetch(`${API_BASE}/health`);


        if (!response.ok) {
            throw new Error("Server unavailable");
        }


        serverStatus.innerHTML = `
            <span class="status-dot"></span>
            <span>Server Online</span>
        `;


        serverStatus.classList.remove("offline");
        serverStatus.classList.add("online");

    } catch (error) {

        serverStatus.innerHTML = `
            <span class="status-dot"></span>
            <span>Server Offline</span>
        `;


        serverStatus.classList.remove("online");
        serverStatus.classList.add("offline");

    }

}


/* =========================================================
   ANALYZE RESUME
========================================================= */

analyzeBtn.addEventListener("click", async (event) => {

    event.preventDefault();


    const file =
        resumeInput.files[0];


    const jd =
        jobDescription.value.trim();


    if (!file) {

        alert("Please upload your resume.");

        return;

    }


    if (!jd) {

        alert(
            "Please paste the job description."
        );

        return;

    }


    const formData =
        new FormData();


    formData.append(
        "file",
        file
    );


    formData.append(
        "job_description",
        jd
    );


    formData.append(
        "candidate_type",
        candidateType.value
    );


    formData.append(
        "target_field",
        targetField.value
    );


    formData.append(
        "experience_years",
        experienceYears.value || "0"
    );


    formData.append(
        "preferred_role",
        preferredRole.value || ""
    );


    formData.append(
        "target_company",
        targetCompany.value
    );


    setLoadingState(true);


    try {

        const response =
            await fetch(
                `${API_BASE}/analyze`,
                {
                    method: "POST",
                    body: formData
                }
            );


        let data;


        try {

            data = await response.json();

        } catch {

            throw new Error(
                "Invalid response received from server."
            );

        }


        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.message ||
                "Resume analysis failed."
            );

        }


        currentReportId =
            data.analysis_id;


        renderResult(data);


        if (currentReportId) {
            downloadBtn.disabled = false;
        }


    } catch (error) {

        console.error(
            "ATSLens Analysis Error:",
            error
        );


        alert(
            `Analysis Error: ${error.message}`
        );

    } finally {

        setLoadingState(false);

    }

});


/* =========================================================
   LOADING STATE
========================================================= */

function setLoadingState(isLoading) {

    analyzeBtn.disabled =
        isLoading;


    if (isLoading) {

        analyzeBtn.innerHTML = `
            <span class="button-icon">
                ✦
            </span>

            <span>
                Analyzing Resume...
            </span>

            <span class="button-arrow">
                •••
            </span>
        `;


        downloadBtn.disabled =
            true;

    } else {

        analyzeBtn.innerHTML = `
            <span class="button-icon">
                ✦
            </span>

            <span>
                Analyze Resume
            </span>

            <span class="button-arrow">
                →
            </span>
        `;


        if (currentReportId) {
            downloadBtn.disabled = false;
        }

    }

}


/* =========================================================
   DOWNLOAD PDF
========================================================= */

downloadBtn.addEventListener("click", () => {

    if (!currentReportId) {

        alert(
            "Please analyze your resume first."
        );

        return;

    }


    window.open(
        `${API_BASE}/download-report/${currentReportId}`,
        "_blank"
    );

});


/* =========================================================
   SHARE REPORT
========================================================= */

shareBtn.addEventListener("click", async () => {

    const score =
        document
            .getElementById("overallScore")
            .textContent;


    const bestField =
        document
            .getElementById("bestField")
            .textContent;


    const grade =
        document
            .getElementById("finalGrade")
            .textContent;


    const text =
        `ATSLens Resume Analysis

ATS Score: ${score}
Grade: ${grade}
Best Career Match: ${bestField}`;


    if (
        navigator.share &&
        window.isSecureContext
    ) {

        try {

            await navigator.share({
                title:
                    "ATSLens Resume Analysis",
                text: text
            });

            return;

        } catch (error) {

            if (
                error.name ===
                "AbortError"
            ) {

                return;

            }

        }

    }


    try {

        await navigator.clipboard
            .writeText(text);


        alert(
            "Report summary copied to clipboard."
        );

    } catch (error) {

        alert(text);

    }

});


/* =========================================================
   RENDER COMPLETE RESULT
========================================================= */

function renderResult(data) {

    document
        .getElementById("resultSubtitle")
        .textContent =
        "Your resume has been analyzed successfully.";


    setOverallScore(
        data.score,
        data.grade,
        data.verdict,
        data.summary
    );


    const breakdown =
        data.breakdown || {};


    setMetric(
        "structure",
        breakdown.structure,
        20
    );


    setMetric(
        "skills",
        breakdown.skills,
        20
    );


    setMetric(
        "tech",
        breakdown.technologies,
        20
    );


    setMetric(
        "projects",
        breakdown.projects,
        20
    );


    setMetric(
        "experience",
        breakdown.experience,
        20
    );


    setMetric(
        "education",
        breakdown.education,
        10
    );


    setMetric(
        "keywords",
        breakdown.keywords,
        10
    );


    setMetric(
        "formatting",
        breakdown.formatting,
        10
    );


    /* Candidate Snapshot */

    document
        .getElementById("profileName")
        .textContent =
        "ATS Evaluation Report";


    document
        .getElementById("profileRole")
        .textContent =
        `${data.target_field || targetField.value} | ${
            data.candidate_type ||
            candidateType.value
        }`;


    document
        .getElementById("profileMeta")
        .textContent =
        `Resume: ${
            data.filename ||
            resumeInput.files[0]?.name ||
            "Uploaded Resume"
        }`;


    /* MNC Readiness */

    document
        .getElementById("mncChance")
        .textContent =
        `${Number(data.mnc_chance || 0)}%`;


    document
        .getElementById("mncLabel")
        .textContent =
        data.mnc_label ||
        "Readiness Result";


    document
        .getElementById("mncText")
        .textContent =
        data.mnc_message ||
        "Your MNC readiness has been calculated.";


    /* Skills */

    renderList(
        "matchedSkills",
        data.matched_skills
    );


    renderList(
        "missingSkills",
        data.missing_skills
    );


    renderList(
        "keyStrengths",
        data.key_strengths
    );


    /* Career Match */

    renderFieldMatches(
        data.field_matches
    );


    /* Score Table */

    renderTable(data);


    /* Roadmap */

    renderRoadmap(
        data.roadmap
    );


    /* Final Verdict */

    document
        .getElementById("finalVerdict")
        .textContent =
        data.verdict ||
        "Analysis Completed";


    document
        .getElementById("finalAdvice")
        .textContent =
        data.final_advice ||
        data.summary ||
        "Review the report and improve weak sections.";


    document
        .getElementById("finalGrade")
        .textContent =
        data.grade ||
        "--";


    /* Scroll To Results */

    document
        .getElementById("resultPanel")
        .scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

}


/* =========================================================
   OVERALL SCORE
========================================================= */

function setOverallScore(
    score,
    grade,
    verdict,
    summary
) {

    const safeScore =
        clamp(
            Number(score) || 0,
            0,
            100
        );


    const degree =
        Math.round(
            safeScore * 3.6
        );


    const overallRing =
        document.getElementById(
            "overallRing"
        );


    overallRing.style.background = `
        conic-gradient(
            #5b5cf0 0deg,
            #23c4d8 ${degree}deg,
            #e8edf5 ${degree}deg
        )
    `;


    document
        .getElementById("overallScore")
        .textContent =
        `${safeScore}%`;


    document
        .getElementById("gradeText")
        .textContent =
        `${grade || "--"} • ${
            verdict ||
            "Analysis Completed"
        }`;


    document
        .getElementById("scoreMessage")
        .textContent =
        summary ||
        "Resume analysis completed successfully.";


    /* Hero Score Ring */

    const miniRing =
        document.querySelector(
            ".mini-ring"
        );


    if (miniRing) {

        miniRing.style.background = `
            conic-gradient(
                #7778ff 0deg,
                #23c4d8 ${degree}deg,
                rgba(255,255,255,.13)
                ${degree}deg
            )
        `;


        const miniScore =
            miniRing.querySelector("span");


        if (miniScore) {

            miniScore.textContent =
                `${safeScore}%`;

        }

    }

}


/* =========================================================
   INDIVIDUAL SCORE
========================================================= */

function setMetric(
    prefix,
    value,
    maxScore
) {

    const safeValue =
        clamp(
            Number(value) || 0,
            0,
            maxScore
        );


    const percentage =
        Math.round(
            (
                safeValue /
                maxScore
            ) *
            100
        );


    const degree =
        Math.round(
            percentage * 3.6
        );


    const ring =
        document.getElementById(
            `${prefix}Ring`
        );


    const score =
        document.getElementById(
            `${prefix}Score`
        );


    const status =
        document.getElementById(
            `${prefix}Status`
        );


    if (ring) {

        ring.style.background = `
            conic-gradient(
                #5b5cf0 0deg,
                #2878eb ${degree}deg,
                #e8edf5 ${degree}deg
            )
        `;

    }


    if (score) {

        score.textContent =
            `${safeValue}/${maxScore}`;

    }


    if (status) {

        status.textContent =
            getPerformance(
                percentage
            );

    }

}


/* =========================================================
   LIST RENDERING
========================================================= */

function renderList(
    elementId,
    items
) {

    const list =
        document.getElementById(
            elementId
        );


    if (!list) {
        return;
    }


    list.innerHTML = "";


    if (
        !Array.isArray(items) ||
        items.length === 0
    ) {

        const item =
            document.createElement("li");


        item.textContent =
            "No data available";


        list.appendChild(item);


        return;

    }


    items
        .slice(0, 12)
        .forEach((value) => {

            const item =
                document.createElement("li");


            item.textContent =
                String(value);


            list.appendChild(item);

        });

}


/* =========================================================
   FIELD MATCHES
========================================================= */

function renderFieldMatches(matches) {

    const bestField =
        document.getElementById(
            "bestField"
        );


    const bestFieldPercent =
        document.getElementById(
            "bestFieldPercent"
        );


    const container =
        document.getElementById(
            "fieldMatches"
        );


    container.innerHTML = "";


    if (
        !Array.isArray(matches) ||
        matches.length === 0
    ) {

        bestField.textContent =
            "Not Available";


        bestFieldPercent.textContent =
            "0% Match";


        container.innerHTML = `
            <p>
                Career field match data
                is not available.
            </p>
        `;


        return;

    }


    const sortedMatches =
        [...matches].sort(
            (a, b) =>
                Number(b.match || 0) -
                Number(a.match || 0)
        );


    const best =
        sortedMatches[0];


    bestField.textContent =
        best.field ||
        "Best Match";


    bestFieldPercent.textContent =
        `${Number(best.match || 0)}% Match`;


    sortedMatches
        .slice(0, 5)
        .forEach((item) => {

            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "field-row";


            const name =
                document.createElement(
                    "span"
                );


            name.textContent =
                item.field ||
                "Unknown Field";


            const score =
                document.createElement(
                    "span"
                );


            score.textContent =
                `${Number(
                    item.match || 0
                )}%`;


            row.appendChild(name);
            row.appendChild(score);


            container.appendChild(row);

        });

}


/* =========================================================
   SCORE TABLE
========================================================= */

function renderTable(data) {

    const breakdown =
        data.breakdown || {};


    const rows = [

        [
            "Resume Structure",
            breakdown.structure,
            20
        ],

        [
            "Skills",
            breakdown.skills,
            20
        ],

        [
            "Technologies",
            breakdown.technologies,
            20
        ],

        [
            "Projects",
            breakdown.projects,
            20
        ],

        [
            "Experience",
            breakdown.experience,
            20
        ],

        [
            "Education",
            breakdown.education,
            10
        ],

        [
            "Keywords",
            breakdown.keywords,
            10
        ],

        [
            "Formatting & Readability",
            breakdown.formatting,
            10
        ]

    ];


    const tbody =
        document.getElementById(
            "scoreTable"
        );


    tbody.innerHTML = "";


    rows.forEach(
        ([section, value, max]) => {

            const score =
                Number(value) || 0;


            const percentage =
                Math.round(
                    (
                        score /
                        max
                    ) *
                    100
                );


            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `
                <td>
                    ${escapeHtml(section)}
                </td>

                <td>
                    ${score}
                </td>

                <td>
                    ${max}
                </td>

                <td>
                    ${percentage}%
                </td>

                <td>
                    ${escapeHtml(
                        getPerformance(
                            percentage
                        )
                    )}
                </td>
            `;


            tbody.appendChild(row);

        }
    );


    /* Total Row */

    const totalObtained =
        Number(
            data.total_obtained
        ) || 0;


    const totalMarks =
        Number(
            data.total_marks
        ) || 130;


    const totalRow =
        document.createElement("tr");


    totalRow.innerHTML = `

        <td>
            <strong>
                Total
            </strong>
        </td>

        <td>
            <strong>
                ${totalObtained}
            </strong>
        </td>

        <td>
            <strong>
                ${totalMarks}
            </strong>
        </td>

        <td>
            <strong>
                ${Number(data.score || 0)}%
            </strong>
        </td>

        <td>
            <strong>
                ${escapeHtml(
                    data.verdict ||
                    "Completed"
                )}
            </strong>
        </td>

    `;


    tbody.appendChild(totalRow);

}


/* =========================================================
   ROADMAP
========================================================= */

function renderRoadmap(roadmap) {

    const list =
        document.getElementById(
            "roadmapList"
        );


    list.innerHTML = "";


    if (
        !Array.isArray(roadmap) ||
        roadmap.length === 0
    ) {

        const item =
            document.createElement("li");


        item.textContent =
            "No improvement roadmap available.";


        list.appendChild(item);


        return;

    }


    roadmap.forEach((step) => {

        const item =
            document.createElement("li");


        item.textContent =
            String(step);


        list.appendChild(item);

    });

}


/* =========================================================
   PERFORMANCE LABEL
========================================================= */

function getPerformance(percentage) {

    if (percentage >= 90) {
        return "Excellent";
    }


    if (percentage >= 80) {
        return "Very Good";
    }


    if (percentage >= 70) {
        return "Good";
    }


    if (percentage >= 55) {
        return "Average";
    }


    return "Needs Work";

}


/* =========================================================
   CLAMP NUMBER
========================================================= */

function clamp(
    number,
    min,
    max
) {

    return Math.min(
        Math.max(
            number,
            min
        ),
        max
    );

}


/* =========================================================
   SAFE HTML
========================================================= */

function escapeHtml(value) {

    return String(
        value ?? ""
    )

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );

}


/* =========================================================
   ACTIVE SIDEBAR NAVIGATION
========================================================= */

const navLinks =
    document.querySelectorAll(
        ".nav-link"
    );


navLinks.forEach((link) => {

    link.addEventListener(
        "click",
        () => {

            navLinks.forEach(
                (item) => {
                    item.classList.remove(
                        "active"
                    );
                }
            );


            link.classList.add(
                "active"
            );

        }
    );

});


/* =========================================================
   INITIALIZE
========================================================= */

checkServer();


setInterval(
    checkServer,
    5000
);