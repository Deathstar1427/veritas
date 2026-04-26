import { getDisparateImpactLabel } from './disparateImpact'

function statusClasses(label) {
  if (label === 'Biased') {
    return 'border-error/30 bg-error-container text-error'
  }

  if (label === 'Perfect') {
    return 'border-emerald-300 bg-emerald-100 text-emerald-800'
  }

  if (label === 'Fair') {
    return 'border-emerald-200 bg-emerald-50 text-emerald-700'
  }

  return 'border-outline-variant bg-surface-container-high text-on-surface-variant'
}

export default function DisparateImpactStatus({ score, className = '' }) {
  const label = getDisparateImpactLabel(score)

  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider ${statusClasses(
        label,
      )} ${className}`}
    >
      {label}
    </span>
  )
}
