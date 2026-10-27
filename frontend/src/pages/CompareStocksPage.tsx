import React, { useState } from 'react';
import { GitCompare, ArrowRight, Check, X, ShieldAlert, TrendingUp } from 'lucide-react';

interface StockData {
  symbol: string;
  name: string;
  exchange: string;
  sector: string;
  price: number;
  sma20: number;
  sma50: number;
  rsi: number;
  volatility: string;
  revenue: string;
  margin: string;
  netProfit: string;
  debtToEquity: string;
  pe: string;
  pb: string;
  strengths: string[];
  risks: string[];
}

const COMPARISON_FIXTURES: Record<string, StockData> = {
  GREENPOWER: {
    symbol: "GREENPOWER",
    name: "Orient Green Power Company Limited",
    exchange: "NSE",
    sector: "Renewable Energy / Wind",
    price: 17.71,
    sma20: 17.58,
    sma50: 18.24,
    rsi: 54.9,
    volatility: "34.3%",
    revenue: "INR 284.5 Cr",
    margin: "60.1%",
    netProfit: "INR 38.6 Cr",
    debtToEquity: "0.63",
    pe: "45.4x",
    pb: "1.25x",
    strengths: [
      "High operating EBITDA margin (60.1%)",
      "Debt reduction from 12.5% to 9.25% cost",
      "Installed wind asset fleet of 402.3 MW"
    ],
    risks: [
      "Cyclical monsoon dependency (May-Sep)",
      "State discom payment delays",
      "Grid curtailment directives"
    ]
  },
  RELIANCE: {
    symbol: "RELIANCE",
    name: "Reliance Industries Limited",
    exchange: "NSE",
    sector: "Oil, Gas, Telecom & Retail",
    price: 2750.00,
    sma20: 2742.10,
    sma50: 2715.40,
    rsi: 58.2,
    volatility: "18.4%",
    revenue: "INR 1,000,122 Cr",
    margin: "17.8%",
    netProfit: "INR 79,020 Cr",
    debtToEquity: "0.41",
    pe: "23.5x",
    pb: "2.34x",
    strengths: [
      "Market leader across Jio 5G and physical retail",
      "Massive balance sheet and cash generation",
      "New energy giga complex in Jamnagar"
    ],
    risks: [
      "Refining margin cyclicality in global O2C",
      "Heavy ongoing 5G capex deployment",
      "Regulatory scrutiny on consumer tariffs"
    ]
  },
  TATAMOTORS: {
    symbol: "TATAMOTORS",
    name: "Tata Motors Limited",
    exchange: "NSE",
    sector: "Automobiles / EVs",
    price: 820.00,
    sma20: 812.50,
    sma50: 835.00,
    rsi: 48.7,
    volatility: "26.5%",
    revenue: "INR 437,928 Cr",
    margin: "14.2%",
    netProfit: "INR 31,807 Cr",
    debtToEquity: "0.72",
    pe: "10.2x",
    pb: "3.12x",
    strengths: [
      "Dominant Indian electric vehicle passenger market share",
      "Strong order backlog and cash flow at JLR",
      "Commercial vehicle infrastructure tailwinds"
    ],
    risks: [
      "Intensifying competition from foreign EV entrants",
      "Geopolitical and supply chain risks across Europe",
      "Raw material and chip cost inflation"
    ]
  }
};

export const CompareStocksPage: React.FC = () => {
  const [stockA, setStockA] = useState<string>('GREENPOWER');
  const [stockB, setStockB] = useState<string>('RELIANCE');

  const dataA = COMPARISON_FIXTURES[stockA] || COMPARISON_FIXTURES['GREENPOWER'];
  const dataB = COMPARISON_FIXTURES[stockB] || COMPARISON_FIXTURES['RELIANCE'];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-obsidian-text flex items-center gap-2">
            <GitCompare className="w-5 h-5 text-gold" />
            Side-by-Side Equities Comparison
          </h2>
          <p className="text-xs text-obsidian-secondary mt-1">
            Compare financial performance, valuation multiples, technical momentum, and risk factors using deterministic data.
          </p>
        </div>
      </div>

      {/* Selectors Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="p-4 rounded-xl bg-obsidian-card border border-obsidian-border flex items-center justify-between">
          <span className="text-xs text-obsidian-muted font-medium">Company A:</span>
          <select
            value={stockA}
            onChange={(e) => setStockA(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-obsidian-bg border border-obsidian-border text-xs text-gold font-bold focus:outline-none"
          >
            <option value="GREENPOWER">Orient Green Power (GREENPOWER)</option>
            <option value="RELIANCE">Reliance Industries (RELIANCE)</option>
            <option value="TATAMOTORS">Tata Motors (TATAMOTORS)</option>
          </select>
        </div>

        <div className="p-4 rounded-xl bg-obsidian-card border border-obsidian-border flex items-center justify-between">
          <span className="text-xs text-obsidian-muted font-medium">Company B:</span>
          <select
            value={stockB}
            onChange={(e) => setStockB(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-obsidian-bg border border-obsidian-border text-xs text-gold font-bold focus:outline-none"
          >
            <option value="RELIANCE">Reliance Industries (RELIANCE)</option>
            <option value="GREENPOWER">Orient Green Power (GREENPOWER)</option>
            <option value="TATAMOTORS">Tata Motors (TATAMOTORS)</option>
          </select>
        </div>
      </div>

      {/* Side-by-Side Comparison Matrix */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-obsidian-border text-obsidian-muted">
                <th className="pb-4 font-semibold uppercase tracking-wider text-obsidian-muted">Metric Category</th>
                <th className="pb-4 font-bold text-sm text-gold">{dataA.name} ({dataA.symbol})</th>
                <th className="pb-4 font-bold text-sm text-market-benchmark">{dataB.name} ({dataB.symbol})</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-obsidian-border/40 font-mono">
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">Exchange & Sector</td>
                <td className="py-3 text-obsidian-text font-sans">{dataA.exchange} • {dataA.sector}</td>
                <td className="py-3 text-obsidian-text font-sans">{dataB.exchange} • {dataB.sector}</td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">Latest Price</td>
                <td className="py-3 text-obsidian-text font-bold">₹{dataA.price.toFixed(2)}</td>
                <td className="py-3 text-obsidian-text font-bold">₹{dataB.price.toFixed(2)}</td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">20-Day vs 50-Day SMA</td>
                <td className="py-3 text-obsidian-text">₹{dataA.sma20} / ₹{dataA.sma50}</td>
                <td className="py-3 text-obsidian-text">₹{dataB.sma20} / ₹{dataB.sma50}</td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">RSI (14-day momentum)</td>
                <td className="py-3 text-obsidian-text">{dataA.rsi}</td>
                <td className="py-3 text-obsidian-text">{dataB.rsi}</td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">Annualized Volatility</td>
                <td className="py-3 text-obsidian-text">{dataA.volatility}</td>
                <td className="py-3 text-obsidian-text">{dataB.volatility}</td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">Revenue (Reported)</td>
                <td className="py-3 text-obsidian-text">{dataA.revenue}</td>
                <td className="py-3 text-obsidian-text">{dataB.revenue}</td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">Operating EBITDA Margin</td>
                <td className="py-3 text-market-positive font-bold">{dataA.margin}</td>
                <td className="py-3 text-market-positive font-bold">{dataB.margin}</td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">Consolidated Net Profit</td>
                <td className="py-3 text-obsidian-text">{dataA.netProfit}</td>
                <td className="py-3 text-obsidian-text">{dataB.netProfit}</td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">Debt to Equity Ratio</td>
                <td className="py-3 text-obsidian-text">{dataA.debtToEquity}</td>
                <td className="py-3 text-obsidian-text">{dataB.debtToEquity}</td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">Valuation Multiples</td>
                <td className="py-3 text-gold">P/E: {dataA.pe} | P/B: {dataA.pb}</td>
                <td className="py-3 text-market-benchmark">P/E: {dataB.pe} | P/B: {dataB.pb}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Comparative Catalysts & Risks */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-3">
          <h4 className="font-bold text-sm text-gold flex items-center gap-2">
            <span>{dataA.name}</span>
          </h4>
          <span className="text-xs text-obsidian-muted block font-semibold">Verified Catalysts:</span>
          <ul className="space-y-1.5 text-xs text-obsidian-secondary">
            {dataA.strengths.map((s, idx) => (
              <li key={idx} className="flex items-start gap-1.5">
                <Check className="w-3.5 h-3.5 text-market-positive shrink-0 mt-0.5" />
                <span>{s}</span>
              </li>
            ))}
          </ul>
          <span className="text-xs text-obsidian-muted block font-semibold pt-2">Operational Risks:</span>
          <ul className="space-y-1.5 text-xs text-obsidian-secondary">
            {dataA.risks.map((r, idx) => (
              <li key={idx} className="flex items-start gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-market-warning shrink-0 mt-0.5" />
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-3">
          <h4 className="font-bold text-sm text-market-benchmark flex items-center gap-2">
            <span>{dataB.name}</span>
          </h4>
          <span className="text-xs text-obsidian-muted block font-semibold">Verified Catalysts:</span>
          <ul className="space-y-1.5 text-xs text-obsidian-secondary">
            {dataB.strengths.map((s, idx) => (
              <li key={idx} className="flex items-start gap-1.5">
                <Check className="w-3.5 h-3.5 text-market-positive shrink-0 mt-0.5" />
                <span>{s}</span>
              </li>
            ))}
          </ul>
          <span className="text-xs text-obsidian-muted block font-semibold pt-2">Operational Risks:</span>
          <ul className="space-y-1.5 text-xs text-obsidian-secondary">
            {dataB.risks.map((r, idx) => (
              <li key={idx} className="flex items-start gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-market-warning shrink-0 mt-0.5" />
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
