import { useEffect, useMemo, useRef, useState } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './AuthContext'
import ProtectedRoute from './ProtectedRoute'
import { authenticatedFetch } from './api'
import Login from './pages/Login'
import LoadingView from './components/dashboard/LoadingView'
import ResultsView from './components/dashboard/ResultsView'
import TopNav from './components/dashboard/TopNav'
import WorkspaceView from './components/dashboard/WorkspaceView'
import './App.css'

const getBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL
  return envUrl && envUrl.length > 0
    ? envUrl
    : 'https://veritas-backend-mopq7prvga-el.a.run.app'
}

function DashboardPage() {
  const [domains, setDomains] = useState({})
  const [domainsLoading, setDomainsLoading] = useState(false)
  const [domainsError, setDomainsError] = useState('')
  const [selectedDomain, setSelectedDomain] = useState(null)
  const [file, setFile] = useState(null)
  const [previewRows, setPreviewRows] = useState([])
  const [analysisData, setAnalysisData] = useState(null)
  const [screen, setScreen] = useState('workspace')
  const [analysisError, setAnalysisError] = useState('')
  const [busy, setBusy] = useState(false)
  const [resultsTransitioning, setResultsTransitioning] = useState(false)
  const resultsTransitionTimerRef = useRef(null)

  const baseUrl = getBaseUrl()

  const overallSeverity = useMemo(() => {
    if (!analysisData?.results?.bias_metrics) return 'Unknown'
    const severities = Object.values(analysisData.results.bias_metrics).map(
      (item) => item.bias_severity,
    )
    if (severities.includes('High')) return 'High'
    if (severities.includes('Medium')) return 'Medium'
    if (severities.includes('Low')) return 'Low'
    return 'Unknown'
  }, [analysisData])

  const metricsList = useMemo(() => {
    if (!analysisData?.results?.bias_metrics) return []
    return Object.entries(analysisData.results.bias_metrics)
  }, [analysisData])

  const refreshDomains = async () => {
    setDomainsLoading(true)
    setDomainsError('')
    try {
      const response = await authenticatedFetch(`${baseUrl}/api/domains`)
      if (!response.ok) {
        throw new Error('Failed to load domains')
      }

      const data = await response.json()
      setDomains(data)
    } catch {
      setDomainsError(
        'Failed to load domains. Check backend connection and try again.',
      )
    } finally {
      setDomainsLoading(false)
    }
  }

  useEffect(() => {
    refreshDomains()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [baseUrl])

  const handleFile = (incomingFile) => {
    if (!incomingFile) return
    if (!incomingFile.name.toLowerCase().endsWith('.csv')) {
      setAnalysisError('Please upload a CSV file.')
      return
    }
    setAnalysisError('')
    setFile(incomingFile)

    const reader = new FileReader()
    reader.onload = (event) => {
      const raw = String(event.target?.result || '')
      const lines = raw.split('\n').slice(0, 6)
      setPreviewRows(lines)
    }
    reader.readAsText(incomingFile)
  }

  const runAnalysis = async () => {
    if (!selectedDomain) {
      setAnalysisError('Please select a domain first.')
      return
    }

    if (!file) {
      setAnalysisError('Please select a CSV file.')
      return
    }

    setBusy(true)
    setAnalysisError('')
    setScreen('loading')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('domain', selectedDomain)
      const response = await authenticatedFetch(`${baseUrl}/api/analyze`, {
        method: 'POST',
        body: formData,
      })

      const responseData = await response.json()

      if (!response.ok) {
        throw new Error(responseData?.detail || 'Analysis failed. Please try again.')
      }

      const tprDebug = Object.fromEntries(
        Object.entries(responseData?.results?.bias_metrics || {}).map(([attribute, metric]) => [
          attribute,
          metric.equalized_odds_tpr_by_group || {},
        ]),
      )
      console.log('[Veritas] Equalized Odds TPR by group:', tprDebug)

      setAnalysisData(responseData)
      setResultsTransitioning(true)
      if (resultsTransitionTimerRef.current) {
        clearTimeout(resultsTransitionTimerRef.current)
      }
      resultsTransitionTimerRef.current = setTimeout(() => {
        setResultsTransitioning(false)
      }, 700)
      setScreen('results')
    } catch (error) {
      setAnalysisError(error?.message || 'Analysis failed. Please try again.')
      setScreen('workspace')
    } finally {
      setBusy(false)
    }
  }

  const exportReport = async () => {
    if (!analysisData) return
    setBusy(true)
    setAnalysisError('')
    try {
      const payload = {
        bias_results: analysisData.results,
        gemini_explanation: analysisData.explanation,
      }

      const response = await authenticatedFetch(`${baseUrl}/api/export`, {
        method: 'POST',
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        let detail = 'Failed to export PDF report.'
        try {
          const err = await response.json()
          detail = err?.detail || detail
        } catch {
          // no-op
        }
        throw new Error(detail)
      }

      const blob = await response.blob()

      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `Veritas_report_${Date.now()}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.parentNode?.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      setAnalysisError(error?.message || 'Failed to export PDF report.')
    } finally {
      setBusy(false)
    }
  }

  const resetAudit = () => {
    if (resultsTransitionTimerRef.current) {
      clearTimeout(resultsTransitionTimerRef.current)
      resultsTransitionTimerRef.current = null
    }
    setResultsTransitioning(false)
    setScreen('workspace')
    setAnalysisData(null)
    setAnalysisError('')
  }

  useEffect(() => {
    return () => {
      if (resultsTransitionTimerRef.current) {
        clearTimeout(resultsTransitionTimerRef.current)
      }
    }
  }, [])

  return (
    <div className="min-h-screen bg-background text-on-surface">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-24 left-1/3 h-64 w-64 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute -right-20 bottom-6 h-52 w-52 rounded-full bg-primary/10 blur-3xl" />
      </div>

      <TopNav
        screen={screen}
        setScreen={setScreen}
        hasResults={Boolean(analysisData)}
      />

      <main className="relative mx-auto w-full max-w-[1200px] px-6 py-8 md:px-10 md:py-10">
        {screen === 'workspace' && (
          <WorkspaceView
            domains={domains}
            domainsLoading={domainsLoading}
            domainsError={domainsError}
            selectedDomain={selectedDomain}
            setSelectedDomain={setSelectedDomain}
            refreshDomains={refreshDomains}
            file={file}
            previewRows={previewRows}
            handleFile={handleFile}
            runAnalysis={runAnalysis}
            busy={busy}
            analysisError={analysisError}
          />
        )}

        {screen === 'loading' && <LoadingView />}

        {screen === 'results' && analysisData && (
          <ResultsView
            analysisData={analysisData}
            overallSeverity={overallSeverity}
            metricsList={metricsList}
            setScreen={setScreen}
            resetAudit={resetAudit}
            exportReport={exportReport}
            busy={busy}
            loadingSkeleton={resultsTransitioning}
          />
        )}
      </main>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
