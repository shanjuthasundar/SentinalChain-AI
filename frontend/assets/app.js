const form = document.getElementById("fraudForm");
const simulationTable = document.getElementById("simulationTable");
const refreshBtn = document.getElementById("refreshSimulation");

function parsePayload() {
  const fd = new FormData(form);
  return {
    transaction_id: fd.get("transaction_id"),
    supplier_id: fd.get("supplier_id"),
    buyer_id: fd.get("buyer_id"),
    invoice_amount: Number(fd.get("invoice_amount")),
    invoice_currency: "USD",
    invoice_count_last_30d: Number(fd.get("invoice_count_last_30d")),
    shipment_distance_km: Number(fd.get("shipment_distance_km")),
    shipment_delay_hours: Number(fd.get("shipment_delay_hours")),
    payment_term_days: Number(fd.get("payment_term_days")),
    contract_value: Number(fd.get("contract_value")),
    country_risk_index: Number(fd.get("country_risk_index")),
    sanctions_hit: fd.get("sanctions_hit") === "on",
    beneficial_owner_mismatch: fd.get("beneficial_owner_mismatch") === "on",
    split_invoice_pattern: fd.get("split_invoice_pattern") === "on",
    tier_level: Number(fd.get("tier_level"))
  };
}

function riskClass(band) {
  switch ((band || "").toLowerCase()) {
    case "critical":
      return "critical";
    case "high":
      return "high";
    case "medium":
      return "medium";
    default:
      return "low";
  }
}

function applyResult(data) {
  const shell = document.getElementById("riskDisplay");
  shell.className = `risk-shell ${riskClass(data.risk_band)}`;

  document.getElementById("riskBand").textContent = (data.risk_band || "LOW").toUpperCase();
  document.getElementById("riskScore").textContent = Number(data.risk_score || 0).toFixed(4);
  document.getElementById("anomalyScore").textContent = Number(data.score_breakdown?.anomaly_score || 0).toFixed(4);
  document.getElementById("ruleScore").textContent = Number(data.score_breakdown?.rule_score || 0).toFixed(4);
  document.getElementById("networkScore").textContent = Number(data.score_breakdown?.network_score || 0).toFixed(4);

  const ul = document.getElementById("reasonCodes");
  ul.innerHTML = "";
  (data.reason_codes || []).forEach((code) => {
    const li = document.createElement("li");
    li.textContent = code;
    ul.appendChild(li);
  });

  document.getElementById("recommendation").textContent = data.recommendation || "No recommendation.";
}

async function evaluate() {
  const payload = parsePayload();
  const response = await fetch("/api/fraud/evaluate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error("Evaluation failed");
  }

  const data = await response.json();
  applyResult(data);
}

async function loadSimulation() {
  const response = await fetch("/api/fraud/simulate", { method: "POST" });
  if (!response.ok) {
    throw new Error("Simulation failed");
  }

  const data = await response.json();
  simulationTable.innerHTML = "";

  (data.samples || []).forEach((item) => {
    const topSignal = item.reason_codes?.[0] || "NO_MATERIAL_ALERTS";
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${item.transaction_id}</td>
      <td>${Number(item.risk_score).toFixed(4)}</td>
      <td>${item.risk_band}</td>
      <td>${topSignal}</td>
    `;
    simulationTable.appendChild(tr);
  });
}

async function loadNetworkSummary() {
  const response = await fetch("/api/network/summary");
  if (!response.ok) {
    return;
  }

  const data = await response.json();
  document.getElementById("suppliersCount").textContent = data.total_suppliers ?? 0;
  document.getElementById("maxTier").textContent = data.max_tier ?? 0;
  document.getElementById("avgRisk").textContent = Number(data.average_base_risk ?? 0).toFixed(2);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await evaluate();
  } catch (error) {
    alert("Unable to evaluate transaction. Check if backend is running.");
  }
});

refreshBtn.addEventListener("click", async () => {
  try {
    await loadSimulation();
  } catch (error) {
    alert("Unable to refresh simulation feed.");
  }
});

(async function init() {
  await loadNetworkSummary();
  await evaluate();
  await loadSimulation();
})();
