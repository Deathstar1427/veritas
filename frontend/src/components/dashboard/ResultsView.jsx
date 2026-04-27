import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import {
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Download,
  FileText,
  Sparkles,
  Search,
  SlidersHorizontal,
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

function WhatIfSimulator({ groupRates, attrName }) {
  const [threshold, setThreshold] = useState(0.5)

  const entries = Object.entries(groupRates || {})
  if (entries.length < 2) return null

  const adjustedRates = Object.fromEntries(
    entries.map(([group, rate]) => [
      group,
      Math.min(100, rate * (threshold / 0.5)),
    ]),
  )

  const rateValues = Object.values(adjustedRates)
  const minRate = Math.min(...rateValues)
  const maxRate = Math.max(...rateValues)
  const adjustedDIR = maxRate > 0 && minRate > 0 ? minRate / maxRate : null

  return (
    <div className="mt-4 rounded-lg border border-primary/20 bg-primary/[0.03] p-5">
      <div className="flex items-center gap-2 mb-3">
        <SlidersHorizontal size={16} className="text-primary" />
        <h4 className="text-sm font-bold text-on-surface">What-If Threshold Simulator</h4>
      </div>
      <p className="text-xs text-on-surface-variant mb-4">
        Adjust the decision threshold and see how the Disparate Impact Ratio changes in real time.
      </p>
      <div className="flex items-center gap-4 mb-4">
        <label htmlFor={`threshold-${attrName}`} className="text-xs font-semibold text-on-surface-variant whitespace-nowrap">
          Threshold: {threshold.toFixed(2)}
        </label>
        <input
          id={`threshold-${attrName}`}
          type="range"
          min={0.1}
          max={0.9}
          step={0.01}
          value={threshold}
          onChange={(e) => setThreshold(+e.target.value)}
          className="flex-1 h-2 rounded-full accent-primary cursor-pointer"
          aria-label={`Decision threshold for ${attrName}`}
        />
      </div>
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-on-surface-variant">Adjusted DIR:</span>
          <span className={`font-headline text-2xl font-bold ${
            adjustedDIR !== null && adjustedDIR < 0.8 ? 'text-error' : 'text-on-surface'
          }`}>
            {adjustedDIR !== null ? adjustedDIR.toFixed(3) : 'N/A'}
          </span>
        </div>
        {adjustedDIR !== null && <DisparateImpactStatus score={adjustedDIR} />}
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4">
        {Object.entries(adjustedRates).map(([group, rate]) => (
          <div key={group} className="rounded-md bg-surface-container-low border border-outline-variant px-3 py-2">
            <p className="text-[11px] font-semibold text-on-surface-variant truncate">{group}</p>
            <p className="text-sm font-bold text-on-surface">{rate.toFixed(1)}%</p>
          </div>
        ))}
      </div>
    </div>
  )
}

function ProxyColumnsCard({ proxyColumns }) {
  if (!proxyColumns || Object.keys(proxyColumns).length === 0) return null

  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 p-5 shadow-subtle">
      <div className="flex items-center gap-2 mb-3">
        <Search size={16} className="text-amber-600" />
        <h3 className="font-headline text-lg font-bold text-on-surface">
          Likely Proxy Columns Detected
        </h3>
      </div>
      <p className="text-xs text-on-surface-variant mb-4">
        These columns correlate strongly with protected attributes and may act as hidden proxies for bias.
      </p>
      {Object.entries(proxyColumns).map(([attr, proxies]) => (
        <div key={attr} className="mb-3 last:mb-0">
          <p className="text-xs font-bold uppercase tracking-wider text-amber-700 mb-2">
            Proxies for: {attr.replaceAll('_', ' ')}
          </p>
          <div className="space-y-1.5">
            {proxies.map(({ column, correlation }) => (
              <div key={column} className="flex items-center justify-between rounded-md bg-white border border-amber-100 px-3 py-2">
                <span className="text-sm font-medium text-on-surface">{column}</span>
                <span className={`text-xs font-bold rounded-full px-2 py-0.5 ${
                  correlation > 0.5
                    ? 'bg-error-container text-error border border-error/30'
                    : correlation > 0.3
                      ? 'bg-amber-100 text-amber-700 border border-amber-200'
                      : 'bg-surface-container-high text-on-surface-variant border border-outline-variant'
                }`}>
                  {correlation.toFixed(3)} correlation
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

export default function ResultsView({
  analysisData,
  overallSeverity,
  metricsList,
  resetAudit,
  exportReport,
  exportModelCard,
  busy,
  loadingSkeleton,
}) {
  const [aiSidebarOpen, setAiSidebarOpen] = useState(true)

  if (loadingSkeleton) {
    return <ResultsSkeleton />
  }

  const proxyColumns = analysisData?.results?.proxy_columns || {}
  const remediation = analysisData?.remediation || []

  return (
    <section className="space-y-8" aria-label="Audit results">
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
            aria-label={aiSidebarOpen ? 'Collapse AI explanation panel' : 'Expand AI explanation panel'}
            className="inline-flex items-center gap-2 rounded-md border border-outline-variant px-4 py-2 text-sm font-semibold text-on-surface transition hover:bg-surface-container-high"
          >
            {aiSidebarOpen ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
            {aiSidebarOpen ? 'Collapse AI Panel' : 'Show AI Panel'}
          </button>
          <button
            type="button"
            onClick={exportReport}
            disabled={busy}
            aria-label="Export audit results as PDF report"
            className="inline-flex items-center gap-2 rounded-md border border-primary/40 px-4 py-2 text-sm font-semibold text-primary transition hover:bg-primary/5 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Download size={14} />
            Export PDF
          </button>
          {exportModelCard && (
            <button
              type="button"
              onClick={exportModelCard}
              disabled={busy}
              aria-label="Generate and download model card"
              className="inline-flex items-center gap-2 rounded-md border border-primary/40 px-4 py-2 text-sm font-semibold text-primary transition hover:bg-primary/5 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <FileText size={14} />
              Model Card
            </button>
          )}
          <button
            type="button"
            onClick={resetAudit}
            aria-label="Start a new audit"
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

      {/* Proxy columns warning card */}
      <ProxyColumnsCard proxyColumns={proxyColumns} />

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

                <WhatIfSimulator
                  groupRates={metric.group_selection_rates}
                  attrName={attrName}
                />
              </div>
            )
          })}
        </div>

        {aiSidebarOpen ? (
          <aside className="space-y-6 md:col-span-4" aria-label="AI explanation and recommendations">
            <GeminiExplanation explanation={analysisData.explanation || ''} />

            {/* Gemini-generated remediation steps */}
            {remediation.length > 0 && (
              <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-6 shadow-subtle">
                <h3 className="flex items-center gap-2 font-headline text-xl font-bold text-on-surface">
                  <Sparkles size={18} className="text-emerald-600" />
                  AI Remediation Steps
                </h3>
                <p className="mt-1 text-xs text-on-surface-variant mb-4">
                  Gemini-generated suggestions to reduce detected bias
                </p>
                <div className="grid grid-cols-1 gap-3">
                  {remediation.map((step, idx) => (
                    <div key={idx} className="rounded-md border border-emerald-200 bg-white p-4">
                      <div className="flex items-start gap-3">
                        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-700">
                          {idx + 1}
                        </span>
                        <div className="text-sm text-on-surface leading-relaxed prose prose-sm prose-emerald">
                          <ReactMarkdown>{step}</ReactMarkdown>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

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
