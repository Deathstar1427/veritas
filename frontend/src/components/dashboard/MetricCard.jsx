export default function MetricCard({ label, value }) {
  return (
    <div className="rounded-lg border border-outline-variant bg-surface p-4 shadow-subtle">
      <p className="text-xs font-semibold uppercase tracking-[0.15em] text-on-surface-variant">
        {label}
      </p>
      <p className="mt-2 font-headline text-4xl font-bold leading-none text-on-surface">
        {value}
      </p>
    </div>
  )
}
