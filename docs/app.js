const companyData = {
  DDS: {
    ticker: "DDS",
    name: "Dillard's",
    sector: "Consumer / Real Estate",
    stance: "Long",
    price: 333,
    sharesOutstanding: 15.8e6,
    netDebt: -480e6,
    thesis:
      "Owned real estate, disciplined inventory control, and relentless buybacks create a sturdier cash engine than most specialty retail screens imply.",
    debate:
      "The market still treats current margins as peak-cycle noise even though the balance sheet and share count have structurally improved.",
    catalysts: [
      "Share count keeps shrinking faster than the sell side refreshes its model.",
      "Real estate value offers a valuation floor that standard retail comps miss.",
      "Steadier gross margin performance should narrow the 'melting ice cube' discount."
    ],
    artifact: {
      title: "Dillard's long pitch PDF",
      href: "../output/DDS_Long_Dillards.pdf",
      copy: "The full single-name deck for the department-store / real-estate long case."
    },
    defaults: {
      growthRate: 3,
      wacc: 11,
      terminalGrowth: 2,
      projectionYears: 5
    },
    history: [
      { year: 2020, revenue: 6.34e9, netIncome: 0.206e9, freeCashFlow: 0.356e9 },
      { year: 2021, revenue: 6.49e9, netIncome: 1.009e9, freeCashFlow: 0.811e9 },
      { year: 2022, revenue: 6.87e9, netIncome: 0.741e9, freeCashFlow: 0.523e9 },
      { year: 2023, revenue: 6.62e9, netIncome: 0.738e9, freeCashFlow: 0.446e9 },
      { year: 2024, revenue: 6.84e9, netIncome: 0.702e9, freeCashFlow: 0.394e9 }
    ]
  },
  MEDP: {
    ticker: "MEDP",
    name: "Medpace",
    sector: "Healthcare / CRO",
    stance: "Long",
    price: 293,
    sharesOutstanding: 31.1e6,
    netDebt: -420e6,
    thesis:
      "A founder-led CRO with unusually strong free-cash conversion and disciplined growth still screens below slower, lower-quality peers.",
    debate:
      "Investors accept quality, but not yet the degree of operating leverage embedded in a maturing backlog and steady FCF conversion.",
    catalysts: [
      "Bookings resilience and mix improvements support a cleaner multi-year revenue bridge.",
      "High incremental margins should turn modest top-line beats into larger EPS revisions.",
      "Net cash and high conversion sustain optionality without forcing aggressive guidance."
    ],
    artifact: {
      title: "Medpace long pitch PDF",
      href: "../output/MEDP_Long_Medpace.pdf",
      copy: "The single-name deck for the CRO quality-compounder re-rating thesis."
    },
    defaults: {
      growthRate: 9,
      wacc: 9.5,
      terminalGrowth: 2.5,
      projectionYears: 6
    },
    history: [
      { year: 2020, revenue: 1.52e9, netIncome: 0.281e9, freeCashFlow: 0.316e9 },
      { year: 2021, revenue: 1.71e9, netIncome: 0.313e9, freeCashFlow: 0.339e9 },
      { year: 2022, revenue: 1.84e9, netIncome: 0.355e9, freeCashFlow: 0.403e9 },
      { year: 2023, revenue: 2.05e9, netIncome: 0.408e9, freeCashFlow: 0.477e9 },
      { year: 2024, revenue: 2.25e9, netIncome: 0.458e9, freeCashFlow: 0.531e9 }
    ]
  },
  PLTR: {
    ticker: "PLTR",
    name: "Palantir",
    sector: "Software / AI Platforms",
    stance: "Short",
    price: 80,
    sharesOutstanding: 2.42e9,
    netDebt: -3.1e9,
    thesis:
      "The operating story is real, but the market is capitalizing a much larger future cash stream than the current base-case economics justify.",
    debate:
      "Enthusiasm around AI distribution keeps resetting the valuation anchor higher even when the actual free-cash outcome remains well below the implied ramp.",
    catalysts: [
      "Multiple compression can dominate good execution when expectations are already extreme.",
      "Commercial growth needs to stay exceptional for years to justify today's price.",
      "Government momentum helps the story, but it does not close an 80-dollar valuation gap alone."
    ],
    artifact: {
      title: "Palantir short pitch PDF",
      href: "../output/PLTR_Short_Palantir.pdf",
      copy: "The single-name deck for the valuation-compression short setup."
    },
    defaults: {
      growthRate: 16,
      wacc: 10.5,
      terminalGrowth: 2.5,
      projectionYears: 6
    },
    history: [
      { year: 2020, revenue: 1.54e9, netIncome: -0.52e9, freeCashFlow: 0.35e9 },
      { year: 2021, revenue: 1.91e9, netIncome: -0.37e9, freeCashFlow: 0.46e9 },
      { year: 2022, revenue: 2.22e9, netIncome: 0.217e9, freeCashFlow: 0.57e9 },
      { year: 2023, revenue: 2.54e9, netIncome: 0.391e9, freeCashFlow: 0.68e9 },
      { year: 2024, revenue: 2.86e9, netIncome: 0.472e9, freeCashFlow: 0.72e9 }
    ]
  }
};

const elements = {
  tickerGrid: document.getElementById("ticker-grid"),
  growthRate: document.getElementById("growth-rate"),
  growthRateOutput: document.getElementById("growth-rate-output"),
  wacc: document.getElementById("wacc"),
  waccOutput: document.getElementById("wacc-output"),
  terminalGrowth: document.getElementById("terminal-growth"),
  terminalGrowthOutput: document.getElementById("terminal-growth-output"),
  projectionYears: document.getElementById("projection-years"),
  projectionYearsOutput: document.getElementById("projection-years-output"),
  resetButton: document.getElementById("reset-assumptions"),
  heroCompany: document.getElementById("hero-company"),
  heroThesis: document.getElementById("hero-thesis"),
  heroMetrics: document.getElementById("hero-metrics"),
  companyName: document.getElementById("company-name"),
  companyThesis: document.getElementById("company-thesis"),
  companyDebate: document.getElementById("company-debate"),
  companyCatalysts: document.getElementById("company-catalysts"),
  stancePill: document.getElementById("stance-pill"),
  metricStrip: document.getElementById("metric-strip"),
  historyChart: document.getElementById("history-chart"),
  heatmap: document.getElementById("heatmap"),
  projectionTableBody: document.getElementById("projection-table-body"),
  artifactPrimary: document.getElementById("artifact-primary"),
  artifactPrimaryTitle: document.getElementById("artifact-primary-title"),
  artifactPrimaryCopy: document.getElementById("artifact-primary-copy")
};

const state = {
  ticker: getInitialTicker(),
  assumptions: {}
};

function getInitialTicker() {
  const hashTicker = window.location.hash.replace("#", "").toUpperCase();
  if (companyData[hashTicker]) {
    return hashTicker;
  }
  return "DDS";
}

function formatMoney(value, digits = 0) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: digits,
    minimumFractionDigits: digits
  }).format(value);
}

function formatCompactMoney(value) {
  const absolute = Math.abs(value);
  if (absolute >= 1e9) {
    return `${value < 0 ? "-" : ""}$${(absolute / 1e9).toFixed(2)}B`;
  }
  if (absolute >= 1e6) {
    return `${value < 0 ? "-" : ""}$${(absolute / 1e6).toFixed(1)}M`;
  }
  return formatMoney(value, 0);
}

function formatPercent(value, digits = 1) {
  return `${value.toFixed(digits)}%`;
}

function buildTickerButtons() {
  elements.tickerGrid.innerHTML = Object.values(companyData)
    .map(
      (company) => `
        <button class="ticker-button${company.ticker === state.ticker ? " is-active" : ""}" type="button" data-ticker="${company.ticker}">
          <strong>${company.ticker}</strong>
          <span>${company.sector}</span>
        </button>
      `
    )
    .join("");

  elements.tickerGrid.querySelectorAll("[data-ticker]").forEach((button) => {
    button.addEventListener("click", () => {
      state.ticker = button.dataset.ticker;
      resetAssumptions();
      render();
    });
  });
}

function resetAssumptions() {
  const defaults = companyData[state.ticker].defaults;
  state.assumptions = { ...defaults };
}

function bindControls() {
  [
    { input: elements.growthRate, key: "growthRate", output: elements.growthRateOutput, suffix: "%" },
    { input: elements.wacc, key: "wacc", output: elements.waccOutput, suffix: "%" },
    { input: elements.terminalGrowth, key: "terminalGrowth", output: elements.terminalGrowthOutput, suffix: "%" },
    { input: elements.projectionYears, key: "projectionYears", output: elements.projectionYearsOutput, suffix: " years" }
  ].forEach(({ input, key, output, suffix }) => {
    input.addEventListener("input", () => {
      state.assumptions[key] = Number(input.value);
      output.value = `${input.value}${suffix}`;
      renderComputed();
    });
  });

  elements.resetButton.addEventListener("click", () => {
    resetAssumptions();
    render();
  });
}

function computeTrailingFcfMargin(history) {
  const trailing = history.slice(-3);
  const total = trailing.reduce((sum, row) => sum + row.freeCashFlow / row.revenue, 0);
  return total / trailing.length;
}

function computeProjection(company, assumptions) {
  const latest = company.history[company.history.length - 1];
  const fcfMargin = computeTrailingFcfMargin(company.history);
  const growthRate = assumptions.growthRate / 100;
  const wacc = assumptions.wacc / 100;
  const terminalGrowth = assumptions.terminalGrowth / 100;
  const projectionYears = assumptions.projectionYears;
  const rows = [];

  for (let yearNumber = 1; yearNumber <= projectionYears; yearNumber += 1) {
    const projectedRevenue = latest.revenue * (1 + growthRate) ** yearNumber;
    const projectedFcf = projectedRevenue * fcfMargin;
    const discountFactor = 1 / (1 + wacc) ** yearNumber;
    const presentValue = projectedFcf * discountFactor;

    rows.push({
      label: `FY${latest.year + yearNumber}`,
      projectedRevenue,
      projectedFcf,
      discountFactor,
      presentValue
    });
  }

  const terminalCashFlow = rows[rows.length - 1].projectedFcf * (1 + terminalGrowth);
  const terminalValue = terminalCashFlow / (wacc - terminalGrowth);
  const presentValueOfTerminal = terminalValue * rows[rows.length - 1].discountFactor;
  const enterpriseValue = rows.reduce((sum, row) => sum + row.presentValue, 0) + presentValueOfTerminal;
  const equityValue = enterpriseValue - company.netDebt;
  const intrinsicValuePerShare = equityValue / company.sharesOutstanding;
  const upsidePct = ((intrinsicValuePerShare - company.price) / company.price) * 100;

  return {
    rows,
    fcfMargin,
    terminalValue,
    presentValueOfTerminal,
    enterpriseValue,
    equityValue,
    intrinsicValuePerShare,
    upsidePct
  };
}

function buildSensitivity(company, assumptions) {
  const baseWacc = assumptions.wacc / 100;
  const baseTgr = assumptions.terminalGrowth / 100;
  const waccValues = [-0.02, -0.01, 0, 0.01, 0.02].map((delta) => Math.max(0.06, baseWacc + delta));
  const tgrValues = [-0.01, -0.005, 0, 0.005, 0.01]
    .map((delta) => baseTgr + delta)
    .filter((value) => value < baseWacc - 0.004);

  while (tgrValues.length < 5) {
    const lastValue = tgrValues[tgrValues.length - 1] ?? baseTgr - 0.005;
    tgrValues.push(Number((lastValue + 0.005).toFixed(4)));
  }

  return {
    waccValues,
    tgrValues,
    matrix: waccValues.map((waccValue) =>
      tgrValues.map((terminalGrowthValue) => {
        const result = computeProjection(company, {
          ...assumptions,
          wacc: waccValue * 100,
          terminalGrowth: terminalGrowthValue * 100
        });
        return result.upsidePct;
      })
    )
  };
}

function renderComputed() {
  const company = companyData[state.ticker];
  const assumptions = state.assumptions;
  const projection = computeProjection(company, assumptions);
  const sensitivity = buildSensitivity(company, assumptions);
  const revenueCagr = calculateCagr(company.history.map((row) => row.revenue));

  elements.heroCompany.textContent = company.name;
  elements.heroThesis.textContent = company.thesis;
  elements.companyName.textContent = `${company.name} (${company.ticker})`;
  elements.companyThesis.textContent = company.thesis;
  elements.companyDebate.textContent = company.debate;

  elements.companyCatalysts.innerHTML = company.catalysts.map((item) => `<li>${item}</li>`).join("");
  elements.stancePill.textContent = `${company.stance} Idea`;
  elements.stancePill.className = `stance-pill ${company.stance.toLowerCase()}`;

  elements.heroMetrics.innerHTML = buildMetricCards([
    {
      label: "Current Price",
      value: formatMoney(company.price, 0),
      context: company.sector
    },
    {
      label: "Intrinsic Value",
      value: formatMoney(projection.intrinsicValuePerShare, 0),
      context: `${assumptions.projectionYears}-year model`
    },
    {
      label: "Valuation Gap",
      value: formatPercent(projection.upsidePct, 1),
      context: projection.upsidePct >= 0 ? "Base-case upside" : "Base-case downside"
    },
    {
      label: "Trailing FCF Margin",
      value: formatPercent(projection.fcfMargin * 100, 1),
      context: "Average of last 3 years"
    }
  ]);

  elements.metricStrip.innerHTML = buildMetricCards([
    {
      label: "Enterprise Value",
      value: formatCompactMoney(projection.enterpriseValue),
      context: `Net debt ${formatCompactMoney(company.netDebt)}`
    },
    {
      label: "Equity Value",
      value: formatCompactMoney(projection.equityValue),
      context: `${(company.sharesOutstanding / 1e6).toFixed(1)}M shares`
    },
    {
      label: "Revenue CAGR",
      value: formatPercent(revenueCagr * 100, 1),
      context: `${company.history[0].year}-${company.history[company.history.length - 1].year}`
    },
    {
      label: "Terminal Value",
      value: formatCompactMoney(projection.terminalValue),
      context: `PV ${formatCompactMoney(projection.presentValueOfTerminal)}`
    }
  ]);

  renderHistoryChart(company.history);
  renderHeatmap(sensitivity);
  renderProjectionTable(projection.rows);

  elements.artifactPrimary.href = company.artifact.href;
  elements.artifactPrimaryTitle.textContent = company.artifact.title;
  elements.artifactPrimaryCopy.textContent = company.artifact.copy;
  window.location.hash = company.ticker;
}

function buildMetricCards(cards) {
  return cards
    .map(
      (card) => `
        <article class="metric-card">
          <p class="mini-label">${card.label}</p>
          <div class="metric-value">${card.value}</div>
          <span class="metric-context">${card.context}</span>
        </article>
      `
    )
    .join("");
}

function renderHistoryChart(history) {
  const series = [
    { key: "revenue", label: "Revenue", color: "#0b1f3a" },
    { key: "netIncome", label: "Net income", color: "#c9a84c" },
    { key: "freeCashFlow", label: "Free cash flow", color: "#1d6b4e" }
  ];

  elements.historyChart.innerHTML = series
    .map((item) => {
      const maxValue = Math.max(...history.map((row) => row[item.key]));
      const latestValue = history[history.length - 1][item.key];

      return `
        <div class="history-series">
          <div class="history-series-head">
            <div class="history-series-title">
              <i class="legend-swatch" style="background:${item.color}"></i>
              <span>${item.label}</span>
            </div>
            <div class="history-series-copy">Latest ${formatCompactMoney(latestValue)}</div>
          </div>
          <div class="history-bars">
            ${history
              .map((row) => {
                const height = Math.max((row[item.key] / maxValue) * 100, 8);
                return `
                  <div class="history-bar-wrap">
                    <div
                      class="history-bar"
                      style="height:${height}%; background:${item.color}"
                      title="${row.year} ${item.label}: ${formatCompactMoney(row[item.key])}"
                    ></div>
                    <div class="history-year">${row.year}</div>
                    <div class="history-scale">${formatCompactMoney(row[item.key])}</div>
                  </div>
                `;
              })
              .join("")}
          </div>
        </div>
      `;
    })
    .join("");
}

function renderHeatmap(sensitivity) {
  const headerCells = sensitivity.tgrValues
    .map((value) => `<th>${formatPercent(value * 100, 1)}</th>`)
    .join("");
  const bodyRows = sensitivity.matrix
    .map(
      (row, rowIndex) => `
        <tr>
          <th>${formatPercent(sensitivity.waccValues[rowIndex] * 100, 1)}</th>
          ${row
            .map((value) => {
              const background = heatmapColor(value);
              const textColor = Math.abs(value) > 24 ? "#ffffff" : "#132033";
              return `<td style="background:${background}; color:${textColor}">${formatPercent(value, 0)}</td>`;
            })
            .join("")}
        </tr>
      `
    )
    .join("");

  elements.heatmap.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>WACC \\ TGR</th>
          ${headerCells}
        </tr>
      </thead>
      <tbody>
        ${bodyRows}
      </tbody>
    </table>
  `;
}

function renderProjectionTable(rows) {
  elements.projectionTableBody.innerHTML = rows
    .map(
      (row) => `
        <tr>
          <td>${row.label}</td>
          <td>${formatCompactMoney(row.projectedRevenue)}</td>
          <td>${formatCompactMoney(row.projectedFcf)}</td>
          <td>${row.discountFactor.toFixed(3)}</td>
          <td>${formatCompactMoney(row.presentValue)}</td>
        </tr>
      `
    )
    .join("");
}

function calculateCagr(values) {
  const start = values[0];
  const end = values[values.length - 1];
  const periods = values.length - 1;
  return (end / start) ** (1 / periods) - 1;
}

function heatmapColor(value) {
  if (value >= 0) {
    const intensity = Math.min(value / 40, 1);
    return `rgba(29, 107, 78, ${0.14 + intensity * 0.58})`;
  }
  const intensity = Math.min(Math.abs(value) / 60, 1);
  return `rgba(161, 76, 67, ${0.12 + intensity * 0.62})`;
}

function syncControls() {
  [
    { input: elements.growthRate, key: "growthRate", output: elements.growthRateOutput, suffix: "%" },
    { input: elements.wacc, key: "wacc", output: elements.waccOutput, suffix: "%" },
    { input: elements.terminalGrowth, key: "terminalGrowth", output: elements.terminalGrowthOutput, suffix: "%" },
    { input: elements.projectionYears, key: "projectionYears", output: elements.projectionYearsOutput, suffix: " years" }
  ].forEach(({ input, key, output, suffix }) => {
    input.value = state.assumptions[key];
    output.value = `${state.assumptions[key]}${suffix}`;
  });
}

function render() {
  buildTickerButtons();
  syncControls();
  renderComputed();
}

resetAssumptions();
bindControls();
render();
