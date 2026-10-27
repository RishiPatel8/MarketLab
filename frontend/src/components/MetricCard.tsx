import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  change?: string;
  isPositive?: boolean;
  sentiment?: 'positive' | 'negative' | 'neutral' | 'gold';
  icon?: React.ReactNode;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  change,
  isPositive,
  sentiment,
  icon
}) => {
  let badgeColor = 'text-obsidian-muted bg-obsidian-elevated border-obsidian-border';
  if (sentiment === 'positive' || isPositive === true) {
    badgeColor = 'text-market-positive bg-market-positive/10 border-market-positive/20';
  } else if (sentiment === 'negative' || isPositive === false) {
    badgeColor = 'text-market-negative bg-market-negative/10 border-market-negative/20';
  } else if (sentiment === 'gold') {
    badgeColor = 'text-gold bg-gold/10 border-gold/20';
  }

  return (
    <div className="p-5 rounded-card bg-obsidian-card border border-obsidian-border hover:border-obsidian-border-muted transition-all duration-200">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-obsidian-muted uppercase tracking-wider">{title}</span>
        {icon && <div className="text-obsidian-secondary">{icon}</div>}
      </div>
      <div className="flex items-baseline gap-2 mb-1">
        <span className="text-2xl font-bold tracking-tight text-obsidian-text tabular-nums">{value}</span>
        {change && (
          <span className={`text-xs font-medium px-1.5 py-0.5 rounded border tabular-nums ${badgeColor}`}>
            {change}
          </span>
        )}
      </div>
      {subtitle && <p className="text-xs text-obsidian-secondary">{subtitle}</p>}
    </div>
  );
};
