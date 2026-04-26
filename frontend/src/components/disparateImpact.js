const FAIR_THRESHOLD = 0.8
const PERFECT_THRESHOLD = 1

export const disparateImpactTargetLabel = 'Target: >= 0.80'

export function getDisparateImpactLabel(score) {
  if (score === null || score === undefined || Number.isNaN(score)) {
    return 'N/A'
  }

  if (score < FAIR_THRESHOLD) {
    return 'Biased'
  }

  if (score >= PERFECT_THRESHOLD) {
    return 'Perfect'
  }

  return 'Fair'
}

export function isDisparateImpactPassing(score) {
  return typeof score === 'number' && score >= FAIR_THRESHOLD
}
