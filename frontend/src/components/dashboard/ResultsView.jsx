import { useState } from 'react'
import {
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Download,
  Sparkles,
} from 'lucide-react'
import DisparateImpactStatus from '../DisparateImpactStatus'
import {
  disparateImpactTargetLabel,
  isDisparateImpactPassing,
} from '../disparateImpact'
import GeminiExplanation from '../GeminiExplanation'
import MetricsChart from '../MetricsChart'
import MetricCard from './MetricCard'
import SkeletonBlock from './SkeletonBlock'
import { severityStyles } from './config'

function metricPass(value, rule) {
  if (value === null || value === undefined) return false
  if (rule === 'dpd' || rule === 'eod') return Math.abs(value) < 0.1
  return false
}

function metricCardData(metric) {
  return [
    {
      key: 'dpd',
      label: 'Demographic Parity Diff',
      value:
        metric.demographic_parity_difference !== null
          ? metric.demographic_parity_difference.toFixed(4)
          : 'N/A',
      pass: metricPass(metric.demographic_parity_difference, 'dpd'),
      target: 'Target: less than 0.10',
    },
    {
      key: 'eod',
      label: 'Equalized Odds Diff',
      value:
        metric.equalized_odds_difference !== null
          ? metric.equalized_odds_difference.toFixed(4)
          : 'N/A',
      pass: metricPass(metric.equalized_odds_difference, 'eod'),
      target: 'Target: less than 0.10',
    },
    {
      key: 'dir',
      label: 'Disparate Impact Ratio',
      value:
        metric.disparate_impact_ratio !== null
          ? metric.disparate_impact_ratio.toFixed(4)
          : 'N/A',
      pass: isDisparateImpactPassing(metric.disparate_impact_ratio),
      score: metric.disparate_impact_ratio,
      target: disparateImpactTargetLabel,
    },
  ]
}

export default function ResultsView({
  analysisData,
  overallSeverity,
  metricsList,
  resetAudit,
  exportReport,
  busy,
  loadingSkeleton,
}) {
  const [aiSidebarOpen, setAiSidebarOpen] = useState(true)

  if (loadingSkeleton) {
    return <ResultsSkeleton />
  }

  return (
    <section className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="font-headline text-4xl font-bold tracking-tight text-on-surface md:text-[42px]">
            Audit Results
          </h1>
          <p className="mt-1 text-sm text-on-surface-variant">
            Dataset domain: <span className="capitalize">{analysisData.results.domain}</span>{' '}
            | {analysisData.results.total_records} records analyzed
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => setAiSidebarOpen((open) => !open)}
            aria-expanded={aiSidebarOpen}
            className="inline-flex items-center gap-2 rounded-md border border-outline-variant px-4 py-2 text-sm font-semibold text-on-surface transition hover:bg-surface-container-high"
          >
            {aiSidebarOpen ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
            {aiSidebarOpen ? 'Collapse AI Panel' : 'Show AI Panel'}
          </button>
          <button
            type="button"
            onClick={exportReport}
            disabled={busy}
            className="inline-flex items-center gap-2 rounded-md border border-primary/40 px-4 py-2 text-sm font-semibold text-primary transition hover:bg-primary/5 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Download size={14} />
            Export PDF
          </button>
          <button
            type="button"
            onClick={resetAudit}
            className="rounded-md bg-primary px-4 py-2 text-sm font-bold text-on-primary transition hover:brightness-105"
          >
            New Audit
          </button>
        </div>
      </div>

      <div
        className={`rounded-lg border border-outline-variant bg-surface p-6 shadow-subtle ${
          severityStyles[overallSeverity]?.glow || ''
        }`}
      >
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-primary">
              Overall Severity
            </p>
            <h2 className="font-headline text-2xl font-bold text-on-surface">
              {overallSeverity === 'Unknown'
                ? 'No severity verdict available'
                : `${overallSeverity} Severity Detected`}
            </h2>
            <p className="mt-1 text-sm text-on-surface-variant">
              Severity is inferred from disparate impact and parity thresholds.
            </p>
          </div>
          <span
            className={`inline-flex items-center rounded-full border px-4 py-2 text-xs font-bold uppercase tracking-[0.15em] ${
              severityStyles[overallSeverity]?.chip ||
              'border-outline-variant bg-surface-container-high text-on-surface'
            }`}
          >
            {overallSeverity}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-12">
        <div className={`space-y-6 ${aiSidebarOpen ? 'md:col-span-8' : 'md:col-span-12'}`}>
          {metricsList.map(([attrName, metric]) => {
            const cards = metricCardData(metric)
            return (
              <div
                key={attrName}
                className="rounded-lg border border-outline-variant bg-surface p-6 shadow-subtle"
              >
                <div className="mb-5 flex items-center justify-between gap-3">
                  <h3 className="font-headline text-2xl font-bold capitalize text-on-surface">
                    {attrName.replaceAll('_', ' ')}
                  </h3>
                  <span
                    className={`rounded-full border px-3 py-1 text-[11px] font-bold uppercase tracking-[0.14em] ${
                      severityStyles[metric.bias_severity]?.chip ||
                      'border-outline-variant text-on-surface'
                    }`}
                  >
                    {metric.bias_severity}
                  </span>
                </div>

                <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
                  {cards.map((card) => (
                    <div key={card.key} className="space-y-2">
                      <MetricCard label={card.label} value={card.value} />
                      <div className="flex items-center justify-between text-xs">
                        {card.key === 'dir' ? (
                          <DisparateImpactStatus score={card.score} />
                        ) : (
                          <span
                            className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 font-bold uppercase tracking-wider ${
                              card.pass
                                ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
                                : 'border-error/30 bg-error-container text-error'
                            }`}
                          >
                            {card.pass ? (
                              <CheckCircle2 size={12} />
                            ) : (
                              <AlertTriangle size={12} />
                            )}
                            {card.pass ? 'Pass' : 'Flagged'}
                          </span>
                        )}
                        <span className="text-on-surface-variant">{card.target}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <MetricsChart
                  groupRates={metric.group_selection_rates}
                  disparateImpactRatio={metric.disparate_impact_ratio}
                  attributeName={attrName}
                />
              </div>
            )
          })}
        </div>

        {aiSidebarOpen ? (
          <aside className="space-y-6 md:col-span-4">
            <GeminiExplanation explanation={analysisData.explanation || ''} />

            <div className="rounded-lg border border-outline-variant bg-surface p-6 shadow-subtle">
              <h3 className="flex items-center gap-2 font-headline text-xl font-bold text-on-surface">
                <Sparkles size={18} className="text-primary" />
                Mitigation Recommendations
              </h3>
              <div className="mt-4 grid grid-cols-1 gap-3">
                <div className="rounded-md border border-outline-variant bg-surface-container-low p-4">
                  <p className="font-semibold text-on-surface">Review proxy variables</p>
                  <p className="mt-1 text-sm text-on-surface-variant">
                    Inspect protected group distributions and remove variables that
                    strongly correlate with sensitive attributes.
                  </p>
                </div>
                <div className="rounded-md border border-outline-variant bg-surface-container-low p-4">
                  <p className="font-semibold text-on-surface">Adjust decision thresholds</p>
                  <p className="mt-1 text-sm text-on-surface-variant">
                    Tune model thresholds and validate fairness-accuracy tradeoffs
                    before release.
                  </p>
                </div>
                <div className="rounded-md border border-outline-variant bg-surface-container-low p-4">
                  <p className="font-semibold text-on-surface">Automate fairness gates</p>
                  <p className="mt-1 text-sm text-on-surface-variant">
                    Add recurring checks in CI/CD so fairness regressions are caught
                    before deployment.
                  </p>
                </div>
              </div>
            </div>
          </aside>
        ) : null}
      </div>
    </section>
  )
}

function ResultsSkeleton() {
  return (
    <section className="space-y-8" aria-busy="true" aria-live="polite">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-2">
          <SkeletonBlock className="h-10 w-64" />
          <SkeletonBlock className="h-4 w-72" />
        </div>
        <div className="flex gap-3">
          <SkeletonBlock className="h-10 w-36" />
          <SkeletonBlock className="h-10 w-24" />
        </div>
      </div>

      <div className="rounded-lg border border-outline-variant bg-surface p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-2">
            <SkeletonBlock className="h-3 w-24" />
            <SkeletonBlock className="h-7 w-64" />
            <SkeletonBlock className="h-4 w-72" />
          </div>
          <SkeletonBlock className="h-8 w-20 rounded-full" />
        </div>
      </div>

      {Array.from({ length: 2 }).map((_, idx) => (
        <div
          key={`result-skeleton-${idx}`}
          className="rounded-lg border border-outline-variant bg-surface p-6"
        >
          <div className="mb-5 flex items-center justify-between">
            <SkeletonBlock className="h-8 w-40" />
            <SkeletonBlock className="h-7 w-20 rounded-full" />
          </div>
          <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
            <SkeletonMetricCard />
            <SkeletonMetricCard />
            <SkeletonMetricCard />
          </div>
          <SkeletonBlock className="h-52 w-full" />
        </div>
      ))}
    </section>
  )
}

function SkeletonMetricCard() {
  return (
    <div className="rounded-lg border border-outline-variant bg-surface-container p-4">
      <SkeletonBlock className="h-3 w-24" />
      <SkeletonBlock className="mt-3 h-8 w-20" />
      <SkeletonBlock className="mt-3 h-5 w-24 rounded-full" />
    </div>
  )
}
