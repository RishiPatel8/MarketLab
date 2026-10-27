import React, { useState } from 'react';
import { EquityPoint } from '../types';

interface EquityChartProps {
  data: EquityPoint[];
  benchmarkCagr?: number;
  initialCapital?: number;
}

export const EquityChart: React.FC<EquityChartProps> = ({
  data,
  benchmarkCagr,
  initialCapital = 100000
}) => {
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-muted">
        No equity curve data available.
      </div>
    );
  }

  const values = data.map((d) => d.portfolio_value);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const range = maxVal - minVal || 1;

  const width = 800;
  const height = 240;
  const padding = 20;

  // Generate SVG points for strategy equity curve (Gold)
  const points = data
    .map((d, i) => {
      const x = padding + (i / (data.length - 1)) * (width - 2 * padding);
      const y = height - padding - ((d.portfolio_value - minVal) / range) * (height - 2 * padding);
      return `${x},${y}`;
    })
    .join(' ');

  // Gradient area fill
  const firstPoint = `${padding},${height - padding}`;
  const lastPoint = `${width - padding},${height - padding}`;
  const areaPoints = `${firstPoint} ${points} ${lastPoint}`;

  const currentHover = hoverIndex !== null ? data[hoverIndex] : data[data.length - 1];

  return (
    <div className="space-y-4">
      {/* Chart Legend & Live Cursor Inspector */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-3 h-1 bg-gold rounded-full"></span>
            <span className="text-obsidian-text font-medium">Strategy Portfolio (Obsidian Gold)</span>
          </div>
          {benchmarkCagr !== undefined && (
            <div className="flex items-center gap-2">
              <span className="w-3 h-1 bg-market-benchmark rounded-full"></span>
              <span className="text-obsidian-secondary">Nifty 50 Benchmark</span>
            </div>
          )}
        </div>

        {currentHover && (
          <div className="flex items-center gap-3 tabular-nums font-mono">
            <span className="text-obsidian-muted">{currentHover.date}</span>
            <span className="text-gold font-bold">
              INR {currentHover.portfolio_value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </span>
            <span className="text-obsidian-secondary text-[11px]">
              (Close: ₹{currentHover.close_price.toFixed(2)})
            </span>
          </div>
        )}
      </div>

      {/* SVG Container */}
      <div className="relative rounded-xl bg-obsidian-bg border border-obsidian-border p-3 overflow-hidden">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-64 overflow-visible"
          onMouseLeave={() => setHoverIndex(null)}
        >
          <defs>
            <linearGradient id="goldGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#D4AF37" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#D4AF37" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          <line x1={padding} y1={padding} x2={width - padding} y2={padding} stroke="#27272A" strokeDasharray="3 3" />
          <line x1={padding} y1={height / 2} x2={width - padding} y2={height / 2} stroke="#27272A" strokeDasharray="3 3" />
          <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#27272A" />

          {/* Area fill */}
          <polygon points={areaPoints} fill="url(#goldGradient)" />

          {/* Gold Strategy Line */}
          <polyline fill="none" stroke="#D4AF37" strokeWidth="2.2" points={points} strokeLinecap="round" strokeLinejoin="round" />

          {/* Interactive hover line */}
          {hoverIndex !== null && (
            <line
              x1={padding + (hoverIndex / (data.length - 1)) * (width - 2 * padding)}
              y1={padding}
              x2={padding + (hoverIndex / (data.length - 1)) * (width - 2 * padding)}
              y2={height - padding}
              stroke="#D4AF37"
              strokeDasharray="2 2"
              strokeWidth="1.5"
            />
          )}

          {/* Transparent hit boxes */}
          {data.map((_, i) => {
            const barW = (width - 2 * padding) / data.length;
            const x = padding + i * barW;
            return (
              <rect
                key={i}
                x={x}
                y={0}
                width={barW}
                height={height}
                fill="transparent"
                onMouseEnter={() => setHoverIndex(i)}
                className="cursor-crosshair"
              />
            );
          })}
        </svg>
      </div>
    </div>
  );
};
