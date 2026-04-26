import { Card } from '@tremor/react'
import DisparateImpactStatus from './DisparateImpactStatus'
import { disparateImpactTargetLabel } from './disparateImpact'

function formatPercent(value) {
  if (typeof value !== 'number') return '0.0%'
  return `${value.toFixed(1)}%`
}

export default function MetricsChart({
  groupRates,
  disparateImpactRatio,
  attributeName,
}) {
  const entries = Object.entries(groupRates || {})
  const title =
    attributeName.charAt(0).toUpperCase() + attributeName.slice(1).replaceAll('_', ' ')

  const sorted = entries.sort((a, b) => b[1] - a[1])
  const topRate = sorted.length > 0 ? sorted[0][1] : 0

  return (
    <Card className="rounded-lg border border-outline-variant bg-surface p-5 shadow-subtle">
      <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <h4 className="font-headline text-lg font-bold text-on-surface">
          Outcome Rates Across {title} Groups
        </h4>
        <div className="flex items-center gap-4 text-xs text-on-surface-variant">
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-primary" />
            Higher rate
          </div>
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-slate-400" />
            Other groups
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {sorted.map(([group, rate], idx) => {
          const width = topRate > 0 ? Math.max((rate / topRate) * 100, 6) : 6
          const highlight = idx === 0
          return (
            <div key={group} className="grid grid-cols-12 items-center gap-3">
              <div className="col-span-4 truncate text-sm font-medium text-on-surface">
                {group}
              </div>
              <div className="col-span-6 h-3 rounded-full bg-surface-container-highest">
                <div
                  className={`h-full rounded-full ${
                    highlight ? 'bg-primary' : 'bg-slate-400'
                  }`}
                  style={{ width: `${width}%` }}
                />
              </div>
              <div className="col-span-2 text-right text-sm font-semibold text-on-surface-variant">
                {formatPercent(rate)}
              </div>
            </div>
          )
        })}
      </div>

      <div className="mt-5 rounded-md border border-outline-variant bg-surface-container-low p-4">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-on-surface-variant">
          Disparate Impact Ratio
        </p>
        <div className="mt-2 flex items-end gap-3">
          <p
            className={`font-headline text-4xl font-bold leading-none ${
              disparateImpactRatio !== null && disparateImpactRatio < 0.8
                ? 'text-error'
                : 'text-on-surface'
            }`}
          >
            {disparateImpactRatio !== null ? disparateImpactRatio.toFixed(3) : 'N/A'}
          </p>
          <DisparateImpactStatus score={disparateImpactRatio} className="mb-1" />
        </div>
        <p className="mt-2 text-xs text-on-surface-variant">{disparateImpactTargetLabel}</p>
      </div>
    </Card>
  )
}
