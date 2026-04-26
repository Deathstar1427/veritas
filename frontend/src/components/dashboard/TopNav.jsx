import { LogOut, ShieldCheck, User } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../AuthContext'

const navItems = [
  { id: 'workspace', label: 'Audit Workspace' },
  { id: 'results', label: 'Results' },
]

export default function TopNav({ screen, setScreen, hasResults }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const canOpenScreen = (id) => id === 'workspace' || hasResults

  const handleLogout = async () => {
    try {
      await logout()
      navigate('/login')
    } catch {
      // silent fail
    }
  }

  const displayName = user?.displayName || user?.email?.split('@')[0] || 'User'
  const avatarUrl = user?.photoURL

  return (
    <header className="no-print sticky top-0 z-40 border-b border-outline-variant bg-surface/95 backdrop-blur">
      <div className="mx-auto flex w-full max-w-[1200px] flex-col gap-4 px-6 py-4 md:flex-row md:items-center md:justify-between md:px-10">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-on-primary shadow-glow">
            <ShieldCheck size={18} />
          </div>
          <div>
            <p className="font-headline text-2xl font-bold leading-tight tracking-tight text-on-surface">
              Veritas
            </p>
            <p className="text-[11px] uppercase tracking-[0.16em] text-on-surface-variant">
              Fairness Auditor
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-6">
          {/* Dashboard nav items */}
          <nav className="flex flex-wrap items-center gap-6">
            {navItems.map((item) => {
              const active =
                item.id === 'workspace'
                  ? screen === 'workspace' || screen === 'loading'
                  : screen === item.id
              const disabled = !canOpenScreen(item.id)

              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => canOpenScreen(item.id) && setScreen(item.id)}
                  className={`border-b-2 pb-1 text-sm font-semibold transition ${
                    active
                      ? 'border-primary text-primary'
                      : 'border-transparent text-on-surface hover:text-primary'
                  } ${disabled ? 'cursor-not-allowed opacity-50' : ''}`}
                >
                  {item.label}
                </button>
              )
            })}
          </nav>

          {/* Divider */}
          <div className="hidden h-6 w-px bg-outline-variant md:block" />

          {/* User info + Logout */}
          {user && (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                {avatarUrl ? (
                  <img
                    src={avatarUrl}
                    alt={displayName}
                    className="h-8 w-8 rounded-full border border-outline-variant object-cover"
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary">
                    <User size={14} />
                  </div>
                )}
                <span className="hidden text-sm font-medium text-on-surface md:inline">
                  {displayName}
                </span>
              </div>
              <button
                type="button"
                onClick={handleLogout}
                title="Sign out"
                className="inline-flex items-center gap-1.5 rounded-md border border-outline-variant px-3 py-1.5 text-xs font-semibold text-on-surface-variant transition hover:border-error/40 hover:bg-error-container hover:text-error"
              >
                <LogOut size={13} />
                <span className="hidden md:inline">Sign out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
