"use strict";

const numberFormat = new Intl.NumberFormat(document.documentElement.lang, {maximumFractionDigits: 2});

function setText(id, value) {
  const node = document.getElementById(id);
  if (node) node.textContent = value;
}

function formatNumber(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numberFormat.format(numeric) : "—";
}

function formatTime(value) {
  const date = new Date(String(value));
  return Number.isNaN(date.getTime()) ? "—" : date.toLocaleString(document.documentElement.lang, {timeZoneName:"short"});
}

function formatDualTime(value) {
  const date = new Date(String(value));
  if (Number.isNaN(date.getTime())) return "—";
  const options = {year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false};
  const utc = date.toLocaleString(document.documentElement.lang, {...options,timeZone:"UTC"});
  const beijing = date.toLocaleString(document.documentElement.lang, {...options,timeZone:"Asia/Shanghai"});
  return `UTC ${utc} · 北京 ${beijing}`;
}

function setTimes(ids, value) {
  ids.forEach((id) => setText(id, value));
}

async function getJson(path) {
  const response = await fetch(path, {cache:"no-store"});
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

async function loadMarketData() {
  try {
    const [cot, drivers, xau, dxy] = await Promise.all([
      getJson("/data/cot.json"),
      getJson("/data/drivers.json"),
      getJson("/data/xauusd.json"),
      getJson("/data/dxy.json")
    ]);
    setText("cot-date", cot.reportDate || "—");
    setText("cot-oi", formatNumber(cot.openInterest));
    setText("cot-managed", formatNumber(cot.managedMoney?.net));
    setText("cot-change", cot.managedMoneyWeeklyChange === null ? "—" : formatNumber(cot.managedMoneyWeeklyChange));
    setText("cot-producer", formatNumber(cot.producer?.net));
    const cotTime = `${cot.reportDate || "—"} (CFTC)`;
    setTimes(["cot-managed-time","cot-change-time","cot-producer-time","cot-oi-time"], cotTime);
    setText("driver-xau", formatNumber(xau.price));
    setText("driver-dxy", formatNumber(dxy.value));
    setText("driver-us2y", `${formatNumber(drivers.us2y)}%`);
    setText("driver-us10y", `${formatNumber(drivers.us10y)}%`);
    setText("driver-real10", `${formatNumber(drivers.real10y)}%`);
    setText("driver-xau-time", formatDualTime(xau.fetched_at));
    setText("driver-dxy-time", formatDualTime(dxy.fetched_at));
    const treasuryTime = `${String(drivers.treasuryDate || "—").slice(0, 10)} (U.S. Treasury EOD)`;
    setTimes(["driver-us2y-time","driver-us10y-time","driver-real10-time"], treasuryTime);
    setText("driver-time", formatDualTime(drivers.updatedAt));
  } catch (error) {
    document.querySelectorAll("[data-market-value]").forEach((node) => { node.textContent = "—"; });
    setText("market-status", document.body.dataset.loadError || "Data unavailable");
  }
}

function positiveNumber(id) {
  const input = document.getElementById(id);
  const value = input ? Number(input.value) : Number.NaN;
  return Number.isFinite(value) && value > 0 ? value : null;
}

function calculateRisk() {
  const balance = positiveNumber("risk-balance");
  const riskPercent = positiveNumber("risk-percent");
  const entry = positiveNumber("risk-entry");
  const stop = positiveNumber("risk-stop");
  const target = positiveNumber("risk-target");
  if ([balance,riskPercent,entry,stop,target].includes(null)) return setText("risk-message", document.body.dataset.inputError);
  const distance = Math.abs(entry - stop);
  if (distance === 0) return setText("risk-message", document.body.dataset.inputError);
  const riskAmount = balance * riskPercent / 100;
  const lots = Math.floor((riskAmount / (distance * 100)) * 100) / 100;
  const rewardRisk = Math.abs(target - entry) / distance;
  setText("risk-amount", `$${formatNumber(riskAmount)}`);
  setText("risk-lots", formatNumber(lots));
  setText("risk-rr", `1 : ${formatNumber(rewardRisk)}`);
  setText("risk-message", "");
}

function normalizeReport(text) {
  return text.replace(/<[^>]+>/g, " ").replace(/&nbsp;|&#160;/gi, " ").replace(/\s+/g, " ");
}

function metric(text, labels) {
  for (const label of labels) {
    const match = text.match(new RegExp(`${label}\\s*[:：]?\\s*(-?[\\d,.]+%?)`, "i"));
    if (match) return match[1];
  }
  return "—";
}

function parseReport(event) {
  const file = event.target.files?.[0];
  if (!file || file.size > 10 * 1024 * 1024) return setText("report-status", document.body.dataset.fileError);
  const reader = new FileReader();
  reader.onerror = () => setText("report-status", document.body.dataset.fileError);
  reader.onload = () => {
    const text = normalizeReport(String(reader.result || ""));
    setText("report-profit", metric(text, ["Total Net Profit","总净利润","總淨利潤"]));
    setText("report-factor", metric(text, ["Profit Factor","盈利因子","獲利因子"]));
    setText("report-drawdown", metric(text, ["Maximal Drawdown","最大回撤","最大回落"]));
    setText("report-trades", metric(text, ["Total Trades","总交易","總交易"]));
    setText("report-status", file.name);
  };
  reader.readAsText(file);
}

document.getElementById("risk-calculate")?.addEventListener("click", calculateRisk);
document.getElementById("report-file")?.addEventListener("change", parseReport);
loadMarketData();
