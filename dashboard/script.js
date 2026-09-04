/* =========================================================
   AI OVERPAYMENT RISK MANAGER
   Dashboard JavaScript
========================================================= */


/* =========================================================
   CONFIGURATION
========================================================= */

const FILES = {
    top20: "../outputs/top20_cases.csv",
    allCases: "../outputs/all_ranked_cases.csv",
    fairness: "../outputs/fairness_report.csv"
};


/* =========================================================
   GLOBAL DATA
========================================================= */

let top20Cases = [];
let allCases = [];
let fairnessData = [];

let riskChart = null;


/* =========================================================
   CSV PARSER
========================================================= */

function parseCSV(text) {

    const rows = [];

    let row = [];
    let value = "";
    let insideQuotes = false;

    for (let i = 0; i < text.length; i++) {

        const char = text[i];
        const next = text[i + 1];

        if (char === '"' && insideQuotes && next === '"') {

            value += '"';

            i++;

        } else if (char === '"') {

            insideQuotes = !insideQuotes;

        } else if (char === "," && !insideQuotes) {

            row.push(value);

            value = "";

        } else if (
            (char === "\n" || char === "\r") &&
            !insideQuotes
        ) {

            if (value !== "" || row.length > 0) {

                row.push(value);

                rows.push(row);

                row = [];

                value = "";
            }

        } else {

            value += char;
        }
    }


    if (value !== "" || row.length > 0) {

        row.push(value);

        rows.push(row);
    }


    if (rows.length === 0) {
        return [];
    }


    const headers = rows[0].map(header =>
        header.trim()
    );


    return rows.slice(1).map(row => {

        const object = {};

        headers.forEach((header, index) => {

            object[header] =
                row[index] !== undefined
                    ? row[index].trim()
                    : "";

        });

        return object;

    });
}


/* =========================================================
   LOAD CSV
========================================================= */

async function loadCSV(path) {

    const response = await fetch(path);

    if (!response.ok) {

        throw new Error(
            `Unable to load ${path}`
        );
    }

    const text = await response.text();

    return parseCSV(text);
}


/* =========================================================
   FIND COLUMN
========================================================= */

function findColumn(object, possibleNames) {

    const keys = Object.keys(object);

    for (const name of possibleNames) {

        const exact = keys.find(
            key => key.toLowerCase() === name.toLowerCase()
        );

        if (exact) {
            return exact;
        }
    }


    for (const name of possibleNames) {

        const partial = keys.find(
            key =>
                key.toLowerCase().includes(
                    name.toLowerCase()
                )
        );

        if (partial) {
            return partial;
        }
    }


    return null;
}


/* =========================================================
   GET VALUE
========================================================= */

function getValue(object, possibleNames, defaultValue = "") {

    const column = findColumn(
        object,
        possibleNames
    );

    if (!column) {
        return defaultValue;
    }

    return object[column];
}


/* =========================================================
   NUMBER
========================================================= */

function numberValue(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return 0;
    }

    const number = parseFloat(
        String(value).replace(/[^0-9.-]/g, "")
    );

    return Number.isFinite(number)
        ? number
        : 0;
}


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHTML(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/* =========================================================
   RISK CATEGORY
========================================================= */

function getRiskCategory(score) {

    if (score >= 75) {
        return "critical";
    }

    if (score >= 50) {
        return "high";
    }

    if (score >= 25) {
        return "medium";
    }

    return "low";
}


/* =========================================================
   RISK BADGE
========================================================= */

function createRiskBadge(score) {

    const category =
        getRiskCategory(score);

    return `
        <span class="risk-badge risk-${category}">
            ${score.toFixed(2)}
        </span>
    `;
}


/* =========================================================
   CREATE REVIEW REASON
========================================================= */

function createReason(caseData) {

    const reasons = [];


    const avgRatio = numberValue(
        getValue(caseData, [
            "average_payment_to_award_ratio",
            "avg_payment_to_award_ratio"
        ])
    );


    const maxRatio = numberValue(
        getValue(caseData, [
            "maximum_payment_to_award_ratio",
            "max_payment_to_award_ratio"
        ])
    );


    const highMonths = numberValue(
        getValue(caseData, [
            "high_payment_months"
        ])
    );


    const aboveAward = numberValue(
        getValue(caseData, [
            "months_above_award"
        ])
    );


    const variability = numberValue(
        getValue(caseData, [
            "payment_variability"
        ])
    );


    if (maxRatio >= 1.5) {

        reasons.push(
            `maximum payment is ${maxRatio.toFixed(2)}× the monthly award`
        );

    } else if (maxRatio > 1) {

        reasons.push(
            `maximum payment exceeds the monthly award`
        );
    }


    if (avgRatio >= 1.15) {

        reasons.push(
            `average payment is ${avgRatio.toFixed(2)}× the award`
        );
    }


    if (highMonths >= 2) {

        reasons.push(
            `${Math.round(highMonths)} high-payment months`
        );
    }


    if (aboveAward >= 2) {

        reasons.push(
            `${Math.round(aboveAward)} months above expected award`
        );
    }


    if (
        variability > 0 &&
        reasons.length < 2
    ) {

        reasons.push(
            "unusual payment variability"
        );
    }


    if (reasons.length === 0) {

        return "Multiple payment patterns contributed to the risk score.";
    }


    return reasons.join("; ") + ".";
}


/* =========================================================
   ADMINISTRATIVE CONTEXT
========================================================= */

function getAdminContext(caseData) {

    const adjustments = numberValue(
        getValue(caseData, [
            "payment_adjustments"
        ])
    );


    const contacts = numberValue(
        getValue(caseData, [
            "contact_attempts"
        ])
    );


    if (adjustments > 0 || contacts >= 4) {

        const details = [];

        if (adjustments > 0) {

            details.push(
                `${Math.round(adjustments)} adjustment(s)`
            );
        }

        if (contacts >= 4) {

            details.push(
                `${Math.round(contacts)} contact attempts`
            );
        }


        return `
            <span class="admin-warning">
                ⚠ ${details.join(", ")}
            </span>
        `;
    }


    return `
        <span class="no-warning">
            None
        </span>
    `;
}


/* =========================================================
   RENDER WORKLIST
========================================================= */

function renderWorklist(data) {

    const body =
        document.getElementById(
            "worklistBody"
        );


    if (!data || data.length === 0) {

        body.innerHTML = `
            <tr>
                <td colspan="8" class="loading">
                    No cases found.
                </td>
            </tr>
        `;

        return;
    }


    body.innerHTML = data.map((caseData, index) => {

        const rank =
            numberValue(
                getValue(caseData, ["rank"])
            ) || index + 1;


        const caseId =
            getValue(caseData, [
                "case_id"
            ], "Unknown");


        const score =
            numberValue(
                getValue(caseData, [
                    "final_risk_score",
                    "risk_score"
                ])
            );


        const avgRatio =
            numberValue(
                getValue(caseData, [
                    "average_payment_to_award_ratio",
                    "avg_payment_to_award_ratio"
                ])
            );


        const maxRatio =
            numberValue(
                getValue(caseData, [
                    "maximum_payment_to_award_ratio",
                    "max_payment_to_award_ratio"
                ])
            );


        const highMonths =
            numberValue(
                getValue(caseData, [
                    "high_payment_months"
                ])
            );


        const reason =
            createReason(caseData);


        return `
            <tr>

                <td>
                    <span class="rank">
                        #${Math.round(rank)}
                    </span>
                </td>


                <td>
                    <span class="case-id">
                        ${escapeHTML(caseId)}
                    </span>
                </td>


                <td>
                    ${createRiskBadge(score)}
                </td>


                <td>
                    ${avgRatio.toFixed(2)}×
                </td>


                <td>
                    ${maxRatio.toFixed(2)}×
                </td>


                <td>
                    ${Math.round(highMonths)}
                </td>


                <td>
                    ${getAdminContext(caseData)}
                </td>


                <td>
                    <div class="reason">
                        ${escapeHTML(reason)}
                    </div>
                </td>

            </tr>
        `;

    }).join("");
}


/* =========================================================
   UPDATE KPI
========================================================= */

function updateKPI() {

    const total =
        allCases.length;


    const scores =
        allCases.map(caseData =>
            numberValue(
                getValue(caseData, [
                    "final_risk_score",
                    "risk_score"
                ])
            )
        );


    const highest =
        scores.length
            ? Math.max(...scores)
            : 0;


    const average =
        scores.length
            ? scores.reduce(
                (sum, value) => sum + value,
                0
            ) / scores.length
            : 0;


    document.getElementById(
        "totalCases"
    ).textContent =
        total.toLocaleString();


    document.getElementById(
        "highestRisk"
    ).textContent =
        highest.toFixed(2);


    document.getElementById(
        "averageRisk"
    ).textContent =
        average.toFixed(2);


    document.getElementById(
        "reviewCases"
    ).textContent =
        Math.min(20, total);
}


/* =========================================================
   RISK DISTRIBUTION
========================================================= */

function updateRiskDistribution() {

    const counts = {

        low: 0,

        medium: 0,

        high: 0,

        critical: 0
    };


    allCases.forEach(caseData => {

        const score =
            numberValue(
                getValue(caseData, [
                    "final_risk_score",
                    "risk_score"
                ])
            );


        counts[
            getRiskCategory(score)
        ]++;
    });


    const total =
        allCases.length || 1;


    updateDistributionItem(
        "low",
        counts.low,
        total
    );


    updateDistributionItem(
        "medium",
        counts.medium,
        total
    );


    updateDistributionItem(
        "high",
        counts.high,
        total
    );


    updateDistributionItem(
        "critical",
        counts.critical,
        total
    );
}


/* =========================================================
   DISTRIBUTION ITEM
========================================================= */

function updateDistributionItem(
    category,
    count,
    total
) {

    const percentage =
        (count / total) * 100;


    document.getElementById(
        `${category}RiskCount`
    ).textContent =
        count.toLocaleString();


    document.getElementById(
        `${category}RiskBar`
    ).style.width =
        `${percentage}%`;
}


/* =========================================================
   RISK CHART
========================================================= */

function renderRiskChart() {

    const canvas =
        document.getElementById(
            "riskChart"
        );


    if (riskChart) {

        riskChart.destroy();
    }


    const labels =
        top20Cases.map(caseData =>
            getValue(
                caseData,
                ["case_id"],
                "Unknown"
            )
        );


    const scores =
        top20Cases.map(caseData =>
            numberValue(
                getValue(caseData, [
                    "final_risk_score",
                    "risk_score"
                ])
            )
        );


    riskChart = new Chart(
        canvas,
        {

            type: "bar",

            data: {

                labels,

                datasets: [

                    {
                        label: "Risk Score",

                        data: scores,

                        borderWidth: 0,

                        borderRadius: 5
                    }

                ]
            },


            options: {

                responsive: true,

                maintainAspectRatio: false,

                indexAxis: "y",

                plugins: {

                    legend: {
                        display: false
                    },

                    tooltip: {

                        callbacks: {

                            label: function(context) {

                                return ` Risk Score: ${context.raw.toFixed(2)}`;
                            }
                        }
                    }
                },


                scales: {

                    x: {

                        beginAtZero: true,

                        max: 100,

                        title: {

                            display: true,

                            text: "Risk Score"
                        }
                    },

                    y: {

                        ticks: {

                            font: {
                                size: 10
                            }
                        }
                    }
                }
            }
        }
    );
}


/* =========================================================
   FAIRNESS
========================================================= */

function renderFairnessGroup(
    elementId,
    dimension
) {

    const element =
        document.getElementById(
            elementId
        );


    const data =
        fairnessData.filter(
            item =>
                String(
                    getValue(item, [
                        "dimension",
                        "group_type",
                        "attribute"
                    ])
                ).toLowerCase() ===
                dimension.toLowerCase()
        );


    if (data.length === 0) {

        element.innerHTML =
            `<div class="loading">No fairness data found.</div>`;

        return;
    }


    element.innerHTML =
        data.map(item => {

            const group =
                getValue(item, [
                    "group",
                    "group_name",
                    "value"
                ], "Unknown");


            const population =
                numberValue(
                    getValue(item, [
                        "population",
                        "population_count"
                    ])
                );


            const top20 =
                numberValue(
                    getValue(item, [
                        "top20",
                        "top_20",
                        "selected",
                        "selection_count"
                    ])
                );


            const selectionRate =
                numberValue(
                    getValue(item, [
                        "selection_rate"
                    ])
                );


            const ratio =
                numberValue(
                    getValue(item, [
                        "ratio",
                        "selection_rate_ratio"
                    ])
                );


            let percentage =
                selectionRate;


            if (percentage <= 1) {
                percentage *= 100;
            }


            percentage =
                Math.min(
                    100,
                    Math.max(
                        0,
                        percentage
                    )
                );


            return `
                <div class="fairness-item">

                    <div class="fairness-item-header">

                        <span>
                            ${escapeHTML(group)}
                        </span>

                        <strong>
                            ${ratio.toFixed(2)}×
                        </strong>

                    </div>


                    <div class="fairness-progress">

                        <div
                            style="width:${percentage}%">
                        </div>

                    </div>


                    <div class="fairness-meta">

                        <span>
                            Population:
                            ${population.toLocaleString()}
                        </span>

                        <span>
                            Top 20:
                            ${top20}
                        </span>

                        <span>
                            ${percentage.toFixed(2)}%
                        </span>

                    </div>

                </div>
            `;

        }).join("");
}


/* =========================================================
   DETECT FAIRNESS DIMENSION
========================================================= */

function getFairnessDimension(item) {

    return getValue(item, [
        "dimension",
        "group_type",
        "attribute"
    ], "");
}


/* =========================================================
   FLEXIBLE FAIRNESS RENDERING
========================================================= */

function renderAllFairness() {

    const dimensions = {

        age: [],

        language: [],

        district: [],

        tenure: []
    };


    fairnessData.forEach(item => {

        const dimension =
            getFairnessDimension(item)
                .toLowerCase();


        if (
            dimension.includes("age")
        ) {

            dimensions.age.push(item);

        } else if (
            dimension.includes("language")
        ) {

            dimensions.language.push(item);

        } else if (
            dimension.includes("district")
        ) {

            dimensions.district.push(item);

        } else if (
            dimension.includes("tenure")
        ) {

            dimensions.tenure.push(item);
        }

    });


    renderFairnessData(
        "ageFairness",
        dimensions.age
    );


    renderFairnessData(
        "languageFairness",
        dimensions.language
    );


    renderFairnessData(
        "districtFairness",
        dimensions.district
    );


    renderFairnessData(
        "tenureFairness",
        dimensions.tenure
    );
}


/* =========================================================
   RENDER FAIRNESS DATA
========================================================= */

function renderFairnessData(
    elementId,
    data
) {

    const element =
        document.getElementById(
            elementId
        );


    if (!data.length) {

        element.innerHTML =
            `<div class="loading">No fairness data found.</div>`;

        return;
    }


    element.innerHTML =
        data.map(item => {

            const group =
                getValue(item, [
                    "group",
                    "group_name",
                    "value"
                ], "Unknown");


            const population =
                numberValue(
                    getValue(item, [
                        "population",
                        "population_count"
                    ])
                );


            const selected =
                numberValue(
                    getValue(item, [
                        "top20",
                        "top_20",
                        "selected",
                        "selection_count"
                    ])
                );


            let selectionRate =
                numberValue(
                    getValue(item, [
                        "selection_rate"
                    ])
                );


            if (selectionRate <= 1) {

                selectionRate *= 100;
            }


            const ratio =
                numberValue(
                    getValue(item, [
                        "ratio",
                        "selection_rate_ratio"
                    ])
                );


            const width =
                Math.min(
                    100,
                    Math.max(
                        0,
                        selectionRate
                    )
                );


            return `

                <div class="fairness-item">

                    <div class="fairness-item-header">

                        <span>
                            ${escapeHTML(group)}
                        </span>

                        <strong>
                            ${ratio.toFixed(2)}×
                        </strong>

                    </div>


                    <div class="fairness-progress">

                        <div
                            style="width:${width}%">
                        </div>

                    </div>


                    <div class="fairness-meta">

                        <span>
                            Population:
                            ${population.toLocaleString()}
                        </span>

                        <span>
                            Top 20:
                            ${selected}
                        </span>

                        <span>
                            ${selectionRate.toFixed(2)}%
                        </span>

                    </div>

                </div>

            `;

        }).join("");
}


/* =========================================================
   SEARCH
========================================================= */

function setupSearch() {

    const input =
        document.getElementById(
            "searchInput"
        );


    input.addEventListener(
        "input",
        function() {

            const search =
                this.value
                    .trim()
                    .toLowerCase();


            if (!search) {

                renderWorklist(
                    top20Cases
                );

                return;
            }


            const filtered =
                top20Cases.filter(
                    caseData => {

                        const caseId =
                            getValue(
                                caseData,
                                ["case_id"],
                                ""
                            ).toLowerCase();


                        return caseId.includes(
                            search
                        );
                    }
                );


            renderWorklist(
                filtered
            );

        }
    );
}


/* =========================================================
   REFRESH
========================================================= */

async function loadDashboard() {

    try {

        const [
            top20,
            all,
            fairness
        ] = await Promise.all([

            loadCSV(
                FILES.top20
            ),

            loadCSV(
                FILES.allCases
            ),

            loadCSV(
                FILES.fairness
            )

        ]);


        top20Cases =
            top20.sort(
                (a, b) =>
                    numberValue(
                        getValue(a, ["rank"])
                    ) -
                    numberValue(
                        getValue(b, ["rank"])
                    )
            );


        allCases = all;


        fairnessData =
            fairness;


        updateKPI();

        updateRiskDistribution();

        renderWorklist(
            top20Cases
        );

        renderRiskChart();

        renderAllFairness();


        console.log(
            "Dashboard loaded successfully."
        );


        console.log(
            "Top 20:",
            top20Cases
        );


        console.log(
            "All cases:",
            allCases
        );


        console.log(
            "Fairness:",
            fairnessData
        );


    } catch (error) {

        console.error(
            "Dashboard loading error:",
            error
        );


        document.getElementById(
            "worklistBody"
        ).innerHTML = `

            <tr>

                <td
                    colspan="8"
                    class="loading"
                >

                    Unable to load dashboard data.

                    <br><br>

                    Make sure the project is running
                    through a local HTTP server.

                    <br><br>

                    Example:

                    <strong>
                        python -m http.server 8000
                    </strong>

                </td>

            </tr>

        `;
    }
}


/* =========================================================
   REFRESH BUTTON
========================================================= */

document
    .getElementById("refreshButton")
    .addEventListener(
        "click",
        loadDashboard
    );


/* =========================================================
   INITIALIZE
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function() {

        setupSearch();

        loadDashboard();

    }
);