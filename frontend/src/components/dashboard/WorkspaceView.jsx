import {
  BookOpen,
  Briefcase,
  DollarSign,
  Heart,
  Loader,
  Play,
  Upload,
} from 'lucide-react'
import SkeletonBlock from './SkeletonBlock'

const domainIcons = {
  hiring: Briefcase,
  loan: DollarSign,
  healthcare: Heart,
  education: BookOpen,
}

export default function WorkspaceView({
  domains,
  domainsLoading,
  domainsError,
  selectedDomain,
  setSelectedDomain,
  refreshDomains,
  file,
  previewRows,
  handleFile,
  runAnalysis,
  busy,
  analysisError,
}) {
  return (
    <section className="space-y-8">
      <div className="space-y-2">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-primary">
          Bias Audit Workspace
        </p>
        <h1 className="font-headline text-4xl font-bold tracking-tight text-on-surface md:text-[42px]">
          Configure Your Fairness Audit
        </h1>
        <p className="max-w-3xl text-sm text-on-surface-variant md:text-base">
          Choose a domain, upload a dataset, and run your audit with
          Fairlearn-backed metrics and plain-language guidance.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="space-y-6 lg:col-span-8">
          <section className="rounded-lg border border-outline-variant bg-surface p-6 shadow-subtle">
            <div className="mb-4 flex items-center justify-between gap-3">
              <h2 className="font-headline text-xl font-bold text-on-surface">
                1) Select Domain
              </h2>
              <button
                type="button"
                onClick={refreshDomains}
                disabled={domainsLoading}
                className="rounded-md border border-outline-variant bg-surface-container-high px-3 py-1.5 text-xs font-semibold text-on-surface transition hover:bg-surface-container-highest disabled:cursor-not-allowed disabled:opacity-60"
              >
                {domainsLoading ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>

            {domainsError ? (
              <div className="mb-4 rounded-md border border-error/30 bg-error-container p-3 text-sm text-error">
                {domainsError}
              </div>
            ) : null}

            {domainsLoading ? (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {Array.from({ length: 4 }).map((_, idx) => (
                  <DomainCardSkeleton key={`domain-skeleton-${idx}`} />
                ))}
              </div>
            ) : Object.keys(domains).length === 0 && !domainsError ? (
              <button
                type="button"
                onClick={refreshDomains}
                className="rounded-md border border-outline-variant bg-surface-container-high px-5 py-3 text-sm font-semibold text-on-surface"
              >
                Load available domains
              </button>
            ) : (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {Object.entries(domains).map(([key, config]) => {
                  const Icon = domainIcons[key] || Briefcase
                  const active = selectedDomain === key
                  return (
                    <button
                      key={key}
                      type="button"
                      onClick={() => setSelectedDomain(key)}
                      className={`rounded-lg border p-4 text-left transition ${
                        active
                          ? 'border-primary bg-primary/5 shadow-glow'
                          : 'border-outline-variant bg-surface-container-low hover:border-primary/40 hover:bg-surface-container-high'
                      }`}
                    >
                      <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 text-primary">
                        <Icon size={20} />
                      </div>
                      <h3 className="font-headline text-lg font-bold capitalize text-on-surface">
                        {key}
                      </h3>
                      <p className="mt-1 text-sm text-on-surface-variant">
                        {config.description}
                      </p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {config.protected_attributes.map((attr) => (
                          <span
                            key={attr}
                            className="rounded-full border border-outline-variant bg-surface px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant"
                          >
                            {attr}
                          </span>
                        ))}
                      </div>
                    </button>
                  )
                })}
              </div>
            )}
          </section>

          <section className="rounded-lg border border-outline-variant bg-surface p-6 shadow-subtle">
            <h2 className="font-headline text-xl font-bold text-on-surface">
              2) Upload CSV
            </h2>
            <label className="mt-4 flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-outline-variant bg-surface-container-low px-6 py-10 text-center transition hover:border-primary/40 hover:bg-surface-container-high">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 text-primary">
                <Upload size={28} />
              </div>
              <h3 className="font-headline text-2xl font-bold text-on-surface">
                Upload your dataset
              </h3>
              <p className="mt-2 max-w-xl text-sm text-on-surface-variant">
                Drag and drop a CSV file here, or click to browse. Max 10MB,
                UTF-8 encoded.
              </p>
              <span className="mt-5 inline-flex items-center rounded-md bg-primary px-4 py-2 text-sm font-bold text-on-primary transition hover:brightness-105">
                Browse Files
              </span>
              <input
                type="file"
                accept=".csv"
                className="hidden"
                onChange={(event) => handleFile(event.target.files?.[0])}
              />
            </label>

            {file ? (
              <div className="mt-4 rounded-lg border border-outline-variant bg-surface-container p-4">
                <p className="text-sm font-semibold text-on-surface">
                  Selected file: {file.name}
                </p>
                <p className="mt-1 text-xs text-on-surface-variant">
                  {(file.size / 1024).toFixed(2)} KB
                </p>

                {previewRows.length > 0 ? (
                  <div className="mt-4 overflow-x-auto rounded-md border border-outline-variant">
                    <table className="min-w-full text-left text-xs">
                      <thead className="bg-surface-container-high">
                        <tr>
                          {previewRows[0].split(',').map((col) => (
                            <th
                              key={col}
                              className="px-3 py-2 font-semibold uppercase tracking-wider text-on-surface-variant"
                            >
                              {col.trim()}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {previewRows.slice(1).map((row, index) => (
                          <tr
                            key={`${row}-${index}`}
                            className="border-t border-outline-variant"
                          >
                            {row.split(',').map((cell, cellIndex) => (
                              <td
                                key={`${cell}-${cellIndex}`}
                                className="px-3 py-2 text-on-surface-variant"
                              >
                                {cell.trim().slice(0, 30)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : null}
              </div>
            ) : null}
          </section>
        </div>

        <aside className="space-y-5 lg:col-span-4">
          <div className="rounded-lg border border-outline-variant bg-surface p-6 shadow-subtle">
            <h3 className="font-headline text-xl font-bold text-on-surface">
              3) Run Audit Analysis
            </h3>
            <p className="mt-2 text-sm text-on-surface-variant">
              Upload your dataset and launch the fairness analysis.
            </p>

            <div className="mt-5 grid grid-cols-1 gap-3">
              <button
                type="button"
                onClick={() => runAnalysis()}
                disabled={busy || !selectedDomain || !file}
                className="inline-flex items-center justify-center gap-2 rounded-md bg-primary px-4 py-3 text-sm font-bold text-on-primary transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {busy ? (
                  <Loader className="animate-spin" size={16} />
                ) : (
                  <Play size={16} />
                )}
                Run Bias Analysis
              </button>
            </div>

            <div className="mt-6 rounded-md border border-outline-variant bg-surface-container-low p-4">
              <p className="text-xs font-bold uppercase tracking-[0.15em] text-on-surface-variant">
                Validation hints
              </p>
              <ul className="mt-3 space-y-2 text-sm text-on-surface-variant">
                <li>CSV only, UTF-8, max 10MB.</li>
                <li>Outcome column must match selected domain.</li>
                <li>At least one protected attribute is required.</li>
              </ul>
            </div>
          </div>

          {analysisError ? (
            <div className="rounded-md border border-error/30 bg-error-container p-4 text-sm text-error">
              {analysisError}
            </div>
          ) : null}
        </aside>
      </div>
    </section>
  )
}

function DomainCardSkeleton() {
  return (
    <div className="rounded-lg border border-outline-variant bg-surface-container-low p-4">
      <SkeletonBlock className="h-10 w-10 rounded-md" />
      <SkeletonBlock className="mt-4 h-4 w-28" />
      <SkeletonBlock className="mt-3 h-3 w-full" />
      <SkeletonBlock className="mt-2 h-3 w-4/5" />
      <div className="mt-4 flex gap-2">
        <SkeletonBlock className="h-5 w-16 rounded-full" />
        <SkeletonBlock className="h-5 w-20 rounded-full" />
      </div>
    </div>
  )
}
