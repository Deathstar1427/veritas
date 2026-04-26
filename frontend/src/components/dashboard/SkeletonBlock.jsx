export default function SkeletonBlock({ className = '' }) {
  return (
    <div
      className={`animate-pulse rounded bg-surface-container-high ${className}`}
      aria-hidden="true"
    />
  )
}
