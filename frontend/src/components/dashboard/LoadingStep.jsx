import { AlertTriangle, CheckCircle2, Loader } from 'lucide-react'

export default function LoadingStep({ label, done, active }) {
  return (
    <div className="flex items-center gap-3">
      {done ? (
        <CheckCircle2 size={17} className="text-success" />
      ) : active ? (
        <Loader size={17} className="animate-spin text-primary" />
      ) : (
        <AlertTriangle size={17} className="text-on-surface-variant" />
      )}
      <p
        className={`text-sm ${
          active ? 'font-semibold text-on-surface' : 'text-on-surface-variant'
        }`}
      >
        {label}
      </p>
    </div>
  )
}
