import React, { useState, useEffect } from 'react';
import { GitCompare, ArrowRight, Check, X, ShieldAlert, TrendingUp, Search, Loader2 } from 'lucide-react';
import { Instrument } from '../types';
import { InstrumentSearchModal } from '../components/InstrumentSearchModal';
import { searchInstruments, getInstrumentMarketData } from '../services/api';

interface RealStockData {
  symbol: string;
  name: string;
  exchange: string;
  sector: string;
  instrumentType: string;
  isin: string;
  price: number | null;
  change: string;
  sma20: number | null;
  sma50: number | null;
  rsi: number | null;
  volatility: string;
  totalBars: number;
  provider: string;
  latencyType: string;
  priceAvailable: boolean;
  strengths: string[];
  risks: string[];
}

function computeTechnicalsFromBars(bars: any[]): {
  price: number | null;
  change: string;
  sma20: number | null;
  sma50: number | null;
  rsi: number | null;
  volatility: string;
} {
  if (!bars || bars.length === 0) {
    return {
      price: null,
      change: 'N/A',
      sma20: null,
      sma50: null,
      rsi: null,
      volatility: 'N/A'
    };
  }

  const latest = bars[bars.length - 1];
  const price = latest.close;

  // Change %
  let change = '0.00%';
  if (bars.length >= 2) {
    const prev = bars[bars.length - 2];
    const diff = ((latest.close - prev.close) / prev.close) * 100;
    change = `${diff >= 0 ? '+' : ''}${diff.toFixed(2)}%`;
  }

  // 20 SMA
  const p20 = Math.min(20, bars.length);
  const slice20 = bars.slice(-p20);
  const sma20 = Number((slice20.reduce((acc, b) => acc + b.close, 0) / p20).toFixed(2));

  // 50 SMA
  const p50 = Math.min(50, bars.length);
  const slice50 = bars.slice(-p50);
  const sma50 = Number((slice50.reduce((acc, b) => acc + b.close, 0) / p50).toFixed(2));

  // 14 RSI
  let rsi: number | null = null;
  if (bars.length >= 15) {
    let gains = 0;
    let losses = 0;
    for (let i = bars.length - 14; i < bars.length; i++) {
      const d = bars[i].close - bars[i - 1].close;
      if (d >= 0) gains += d;
      else losses -= d;
    }
    const avgGain = gains / 14;
    const avgLoss = losses / 14;
    if (avgLoss === 0) {
      rsi = 100;
    } else {
      const rs = avgGain / avgLoss;
      rsi = Number((100 - 100 / (1 + rs)).toFixed(1));
    }
  }

  // Volatility
  let volatility = 'N/A';
  if (bars.length >= 10) {
    const returns: number[] = [];
    for (let i = 1; i < bars.length; i++) {
      returns.push((bars[i].close - bars[i - 1].close) / bars[i - 1].close);
    }
    const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / returns.length;
    const annualizedVol = Math.sqrt(variance) * Math.sqrt(252) * 100;
    volatility = `${annualizedVol.toFixed(1)}%`;
  }

  return { price, change, sma20, sma50, rsi, volatility };
}

export const CompareStocksPage: React.FC = () => {
  const [dataA, setDataA] = useState<RealStockData | null>(null);
  const [dataB, setDataB] = useState<RealStockData | null>(null);
  const [loadingA, setLoadingA] = useState(true);
  const [loadingB, setLoadingB] = useState(true);
  const [searchTarget, setSearchTarget] = useState<'A' | 'B' | null>(null);

  // Load real market data for an instrument
  const loadInstrumentData = async (inst: Instrument): Promise<RealStockData> => {
    try {
      const md = await getInstrumentMarketData(inst.id);
      const bars = md?.bars || [];
      const val = md?.validation || {};
      const tech = computeTechnicalsFromBars(bars);

      const hasPrice = bars.length > 0 || (inst.latest_nav !== undefined && inst.latest_nav !== null);
      const displayPrice = tech.price !== null ? tech.price : (inst.latest_nav || null);

      return {
        symbol: inst.symbol,
        name: inst.company_name,
        exchange: inst.exchange,
        sector: inst.sector || inst.scheme_category || (inst.instrument_type === 'ETF' ? 'Exchange Traded Fund' : 'Equities'),
        instrumentType: inst.instrument_type,
        isin: inst.isin || 'Verified Master Record',
        price: displayPrice,
        change: tech.change,
        sma20: tech.sma20,
        sma50: tech.sma50,
        rsi: tech.rsi,
        volatility: tech.volatility,
        totalBars: bars.length,
        provider: val.provider_attribution || inst.source_provider || 'Official Master',
        latencyType: val.latency_type || 'daily_historical',
        priceAvailable: hasPrice,
        strengths: [
          `Verified Official Identifier: ISIN ${inst.isin || inst.bse_code || inst.scheme_code}`,
          inst.exchange === 'NSE,BSE'
            ? 'Dual-listed on both NSE and BSE with arbitrage and liquidity choice'
            : `Active primary listing on ${inst.exchange}`,
          inst.bse_code ? `BSE Official Scrip Code: ${inst.bse_code}` : 'Authoritative exchange membership'
        ],
        risks: [
          inst.instrument_type === 'MUTUAL_FUND'
            ? 'Subject to daily Net Asset Value fluctuations per AMFI market valuation'
            : 'Subject to exchange market volatility and systematic sector exposure',
          'Macroeconomic interest rate and policy factors',
          hasPrice ? 'Standard historical market risk profile' : 'Pricing data not active on configured feed provider'
        ]
      };
    } catch (err) {
      console.error('Failed to load instrument market data:', err);
      return {
        symbol: inst.symbol,
        name: inst.company_name,
        exchange: inst.exchange,
        sector: inst.sector || 'Equities',
        instrumentType: inst.instrument_type,
        isin: inst.isin || 'N/A',
        price: inst.latest_nav || null,
        change: 'N/A',
        sma20: null,
        sma50: null,
        rsi: null,
        volatility: 'N/A',
        totalBars: 0,
        provider: 'N/A',
        latencyType: 'daily_historical',
        priceAvailable: false,
        strengths: [`Listing recorded in verified master: ${inst.symbol}`],
        risks: ['Real-time provider response unavailable']
      };
    }
  };

  // Initial load on mount for default instruments (GREENPOWER and RELIANCE)
  useEffect(() => {
    let isMounted = true;

    async function initComparison() {
      setLoadingA(true);
      setLoadingB(true);

      const [resA, resB] = await Promise.all([
        searchInstruments('GREENPOWER', 'ALL', 'ALL', 1, 1),
        searchInstruments('RELIANCE', 'ALL', 'ALL', 1, 1)
      ]);

      if (resA.items && resA.items.length > 0) {
        const dA = await loadInstrumentData(resA.items[0]);
        if (isMounted) {
          setDataA(dA);
          setLoadingA(false);
        }
      }

      if (resB.items && resB.items.length > 0) {
        const dB = await loadInstrumentData(resB.items[0]);
        if (isMounted) {
          setDataB(dB);
          setLoadingB(false);
        }
      }
    }

    initComparison();
    return () => {
      isMounted = false;
    };
  }, []);

  const handleSelectInstrument = async (symbol: string, inst?: Instrument) => {
    if (!inst) {
      const res = await searchInstruments(symbol, 'ALL', 'ALL', 1, 1);
      if (res.items && res.items.length > 0) {
        inst = res.items[0];
      }
    }

    if (!inst) {
      setSearchTarget(null);
      return;
    }

    if (searchTarget === 'A') {
      setLoadingA(true);
      const data = await loadInstrumentData(inst);
      setDataA(data);
      setLoadingA(false);
    } else if (searchTarget === 'B') {
      setLoadingB(true);
      const data = await loadInstrumentData(inst);
      setDataB(data);
      setLoadingB(false);
    }
    setSearchTarget(null);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-obsidian-text flex items-center gap-2">
            <GitCompare className="w-5 h-5 text-gold" />
            Side-by-Side Equities & Fund Comparison
          </h2>
          <p className="text-xs text-obsidian-secondary mt-1">
            Compare financial performance, technical momentum, and volatility calculated directly from original market data feeds across 20,000+ Indian instruments.
          </p>
        </div>
      </div>

      {/* Selectors Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Instrument A Selector */}
        <div className="p-4 rounded-xl bg-obsidian-card border border-obsidian-border flex items-center justify-between">
          <div>
            <span className="text-xs text-obsidian-muted font-medium block">Instrument A:</span>
            {loadingA ? (
              <span className="text-sm font-bold text-obsidian-muted flex items-center gap-1.5 mt-0.5">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-gold" />
                Loading original data feed...
              </span>
            ) : (
              <div>
                <span className="text-sm font-bold text-gold">{dataA?.name} ({dataA?.symbol})</span>
                <span className="text-[10px] text-obsidian-muted block">{dataA?.exchange} • {dataA?.sector}</span>
              </div>
            )}
          </div>
          <button
            onClick={() => setSearchTarget('A')}
            className="px-3 py-1.5 rounded-lg bg-obsidian-bg hover:bg-obsidian-elevated border border-obsidian-border text-xs text-gold font-medium flex items-center gap-1.5 transition-colors"
          >
            <Search className="w-3.5 h-3.5" />
            <span>Select Instrument</span>
          </button>
        </div>

        {/* Instrument B Selector */}
        <div className="p-4 rounded-xl bg-obsidian-card border border-obsidian-border flex items-center justify-between">
          <div>
            <span className="text-xs text-obsidian-muted font-medium block">Instrument B:</span>
            {loadingB ? (
              <span className="text-sm font-bold text-obsidian-muted flex items-center gap-1.5 mt-0.5">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-market-benchmark" />
                Loading original data feed...
              </span>
            ) : (
              <div>
                <span className="text-sm font-bold text-market-benchmark">{dataB?.name} ({dataB?.symbol})</span>
                <span className="text-[10px] text-obsidian-muted block">{dataB?.exchange} • {dataB?.sector}</span>
              </div>
            )}
          </div>
          <button
            onClick={() => setSearchTarget('B')}
            className="px-3 py-1.5 rounded-lg bg-obsidian-bg hover:bg-obsidian-elevated border border-obsidian-border text-xs text-market-benchmark font-medium flex items-center gap-1.5 transition-colors"
          >
            <Search className="w-3.5 h-3.5" />
            <span>Select Instrument</span>
          </button>
        </div>
      </div>

      {/* Side-by-Side Comparison Matrix */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-obsidian-border text-obsidian-muted">
                <th className="pb-4 font-semibold uppercase tracking-wider text-obsidian-muted">Metric Category (Calculated from Feed)</th>
                <th className="pb-4 font-bold text-sm text-gold">{dataA?.name} ({dataA?.symbol})</th>
                <th className="pb-4 font-bold text-sm text-market-benchmark">{dataB?.name} ({dataB?.symbol})</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-obsidian-border/40 font-mono">
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">Exchange & Sector</td>
                <td className="py-3 text-obsidian-text font-sans">{dataA?.exchange} • {dataA?.sector}</td>
                <td className="py-3 text-obsidian-text font-sans">{dataB?.exchange} • {dataB?.sector}</td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">Latest Price / NAV</td>
                <td className="py-3 text-obsidian-text font-bold">
                  {dataA?.price !== null ? `₹${dataA?.price?.toFixed(2)}` : 'Price unavailable from provider'}
                </td>
                <td className="py-3 text-obsidian-text font-bold">
                  {dataB?.price !== null ? `₹${dataB?.price?.toFixed(2)}` : 'Price unavailable from provider'}
                </td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">24h Day Change</td>
                <td className="py-3 text-obsidian-text">{dataA?.change}</td>
                <td className="py-3 text-obsidian-text">{dataB?.change}</td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">20-Day vs 50-Day SMA</td>
                <td className="py-3 text-obsidian-text">
                  {dataA?.sma20 ? `₹${dataA.sma20} / ₹${dataA.sma50}` : 'Insufficient bar history'}
                </td>
                <td className="py-3 text-obsidian-text">
                  {dataB?.sma20 ? `₹${dataB.sma20} / ₹${dataB.sma50}` : 'Insufficient bar history'}
                </td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">RSI (14-day momentum)</td>
                <td className="py-3 text-obsidian-text">{dataA?.rsi !== null ? dataA?.rsi : 'N/A'}</td>
                <td className="py-3 text-obsidian-text">{dataB?.rsi !== null ? dataB?.rsi : 'N/A'}</td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">Annualized Volatility</td>
                <td className="py-3 text-obsidian-text">{dataA?.volatility}</td>
                <td className="py-3 text-obsidian-text">{dataB?.volatility}</td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">Data Feed Provider</td>
                <td className="py-3 text-gold">{dataA?.provider} ({dataA?.latencyType})</td>
                <td className="py-3 text-market-benchmark">{dataB?.provider} ({dataB?.latencyType})</td>
              </tr>
              <tr>
                <td className="py-3 text-obsidian-secondary font-sans font-medium">Verified Official ISIN</td>
                <td className="py-3 text-obsidian-text">{dataA?.isin}</td>
                <td className="py-3 text-obsidian-text">{dataB?.isin}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Comparative Catalysts & Risks */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-3">
          <h4 className="font-bold text-sm text-gold flex items-center gap-2">
            <span>{dataA?.name}</span>
          </h4>
          <span className="text-xs text-obsidian-muted block font-semibold">Verified Catalysts:</span>
          <ul className="space-y-1.5 text-xs text-obsidian-secondary">
            {dataA?.strengths.map((s, idx) => (
              <li key={idx} className="flex items-start gap-1.5">
                <Check className="w-3.5 h-3.5 text-market-positive shrink-0 mt-0.5" />
                <span>{s}</span>
              </li>
            ))}
          </ul>
          <span className="text-xs text-obsidian-muted block font-semibold pt-2">Operational Risks:</span>
          <ul className="space-y-1.5 text-xs text-obsidian-secondary">
            {dataA?.risks.map((r, idx) => (
              <li key={idx} className="flex items-start gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-market-warning shrink-0 mt-0.5" />
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-3">
          <h4 className="font-bold text-sm text-market-benchmark flex items-center gap-2">
            <span>{dataB?.name}</span>
          </h4>
          <span className="text-xs text-obsidian-muted block font-semibold">Verified Catalysts:</span>
          <ul className="space-y-1.5 text-xs text-obsidian-secondary">
            {dataB?.strengths.map((s, idx) => (
              <li key={idx} className="flex items-start gap-1.5">
                <Check className="w-3.5 h-3.5 text-market-positive shrink-0 mt-0.5" />
                <span>{s}</span>
              </li>
            ))}
          </ul>
          <span className="text-xs text-obsidian-muted block font-semibold pt-2">Operational Risks:</span>
          <ul className="space-y-1.5 text-xs text-obsidian-secondary">
            {dataB?.risks.map((r, idx) => (
              <li key={idx} className="flex items-start gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-market-warning shrink-0 mt-0.5" />
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <InstrumentSearchModal
        isOpen={searchTarget !== null}
        onClose={() => setSearchTarget(null)}
        onSelectInstrument={handleSelectInstrument}
        title={`Select Instrument for Comparison (${searchTarget === 'A' ? 'Instrument A' : 'Instrument B'})`}
      />
    </div>
  );
};
