import { Navigate, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { ShieldCheck } from 'lucide-react'
import { useAuth } from '../AuthContext'

export default function Login() {
  const { login, user } = useAuth()
  const location = useLocation()
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const fromPath = location.state?.from?.pathname || '/'

  if (user) {
    return <Navigate to={fromPath} replace />
  }

  const handleSignIn = async () => {
    setBusy(true)
    setError('')
    try {
      await login()
    } catch (err) {
      setError(err?.message || 'Google sign-in failed. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6 py-8">
      {/* Ambient glow */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-24 left-1/3 h-64 w-64 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute -right-20 bottom-6 h-52 w-52 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute left-1/2 top-1/2 h-80 w-80 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/5 blur-3xl" />
      </div>

      <section className="relative w-full max-w-md rounded-xl border border-outline-variant bg-surface p-8 text-center shadow-ambient md:p-10">
        {/* Logo */}
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-xl bg-primary text-on-primary shadow-glow">
          <ShieldCheck size={26} />
        </div>

        <p className="mt-5 text-xs font-bold uppercase tracking-[0.16em] text-primary">
          Veritas
        </p>
        <h1 className="mt-2 font-headline text-3xl font-bold text-on-surface">
          AI Fairness Auditor
        </h1>
        <p className="mx-auto mt-3 max-w-xs text-sm leading-relaxed text-on-surface-variant">
          Detect bias in ML datasets with Fairlearn metrics and get AI-powered
          explanations. Sign in to get started.
        </p>

        <button
          type="button"
          onClick={handleSignIn}
          disabled={busy}
          className="mt-8 inline-flex w-full items-center justify-center gap-3 rounded-lg bg-primary px-4 py-3.5 text-sm font-bold text-on-primary shadow-glow transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {/* Google icon */}
          <svg viewBox="0 0 24 24" width="18" height="18" className="shrink-0">
            <path
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
              fill="#4285F4"
            />
            <path
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              fill="#34A853"
            />
            <path
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              fill="#FBBC05"
            />
            <path
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              fill="#EA4335"
            />
          </svg>
          {busy ? 'Signing in…' : 'Sign in with Google'}
        </button>

        {error ? (
          <p className="mt-5 rounded-md border border-error/30 bg-error-container px-3 py-2.5 text-sm text-error">
            {error}
          </p>
        ) : null}

        <p className="mt-6 text-xs text-on-surface-variant">
          Your data is processed securely and never stored.
        </p>
      </section>
    </main>
  )
}
