import { Loader } from 'lucide-react'
import LoadingStep from './LoadingStep'

export default function LoadingView() {
  return (
    <section className="mx-auto flex max-w-4xl flex-col items-center justify-center gap-8 py-16 text-center">
      <div className="relative flex h-40 w-40 items-center justify-center rounded-full border border-primary/20 bg-surface shadow-glow">
        <div className="absolute inset-4 rounded-full border border-primary/15" />
        <Loader className="animate-spin text-primary" size={56} />
      </div>

      <div className="space-y-3">
        <h2 className="font-headline text-4xl font-bold tracking-tight text-on-surface">
          Audit Analysis in Progress
        </h2>
        <p className="mx-auto max-w-2xl text-sm leading-relaxed text-on-surface-variant md:text-base">
          Veritas is computing demographic parity, equalized odds, and
          disparate impact, then generating plain-language recommendations.
        </p>
      </div>

      <div className="w-full max-w-2xl rounded-lg border border-outline-variant bg-surface p-6 text-left shadow-subtle">
        <div className="space-y-4">
          <LoadingStep done label="Ingesting CSV and validating schema" />
          <LoadingStep done label="Computing fairness metrics by group" />
          <LoadingStep active label="Building AI narrative and recommendations" />
          <LoadingStep label="Preparing audit dashboard" />
        </div>
      </div>
    </section>
  )
}
