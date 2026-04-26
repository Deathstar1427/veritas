import { Card } from '@tremor/react'
import * as Accordion from '@radix-ui/react-accordion'
import { AlertTriangle, ChevronDown, Users, Wrench } from 'lucide-react'

function escapeHtml(text) {
  return text
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function formatMarkdownToHtml(markdownText) {
  if (!markdownText) return ''

  let html = escapeHtml(markdownText)
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>')
  html = html.replace(/^\* /gm, '&#8226; ')
  html = html.replace(/\n/g, '<br/>')
  return html
}

export default function GeminiExplanation({ explanation }) {
  const sections = {
    'What the Bias Is': '',
    'Why It Matters': '',
    'How to Fix It': '',
  }

  const lines = explanation.split('\n')
  let currentSection = null
  let buffer = ''

  lines.forEach((line) => {
    if (line.includes('What') && line.includes('Bias')) {
      if (buffer && currentSection) sections[currentSection] = buffer.trim()
      currentSection = 'What the Bias Is'
      buffer = ''
    } else if (line.includes('Why') && line.includes('Matters')) {
      if (buffer && currentSection) sections[currentSection] = buffer.trim()
      currentSection = 'Why It Matters'
      buffer = ''
    } else if (line.includes('How') && (line.includes('Fix') || line.includes('fix'))) {
      if (buffer && currentSection) sections[currentSection] = buffer.trim()
      currentSection = 'How to Fix It'
      buffer = ''
    } else {
      buffer += `${line}\n`
    }
  })

  if (buffer && currentSection) {
    sections[currentSection] = buffer.trim()
  }

  if (!sections['What the Bias Is'] && !sections['Why It Matters']) {
    sections['What the Bias Is'] = explanation
    delete sections['Why It Matters']
    delete sections['How to Fix It']
  }

  const sectionConfig = {
    'What the Bias Is': {
      icon: AlertTriangle,
      iconClass: 'text-error',
      borderClass: 'border-error/25',
      bgClass: 'bg-error-container/40',
    },
    'Why It Matters': {
      icon: Users,
      iconClass: 'text-amber-600',
      borderClass: 'border-amber-200',
      bgClass: 'bg-amber-50',
    },
    'How to Fix It': {
      icon: Wrench,
      iconClass: 'text-emerald-600',
      borderClass: 'border-emerald-200',
      bgClass: 'bg-emerald-50',
    },
  }

  return (
    <Card className="rounded-lg border border-outline-variant bg-surface p-5 shadow-subtle">
      <div className="mb-4">
        <p className="font-headline text-lg font-bold text-on-surface">
          Fairness Audit Explanation
        </p>
        <p className="mt-1 text-xs uppercase tracking-[0.14em] text-on-surface-variant">
          Powered by Google Gemini
        </p>
      </div>

      <Accordion.Root type="single" collapsible className="space-y-3">
        {Object.entries(sections).map(([title, content], idx) => {
          if (!content) return null

          const config = sectionConfig[title] || {}
          const Icon = config.icon || AlertTriangle

          return (
            <Accordion.Item key={idx} value={`item-${idx}`}>
              <Accordion.Trigger
                className={`group flex w-full items-center justify-between rounded-md border px-4 py-3 text-left transition ${
                  config.borderClass || 'border-outline-variant'
                } ${config.bgClass || 'bg-surface-container-low'}`}
              >
                <div className="flex items-center gap-3">
                  <Icon size={16} className={config.iconClass || 'text-primary'} />
                  <span className="text-sm font-semibold text-on-surface">{title}</span>
                </div>
                <ChevronDown className="h-4 w-4 text-on-surface-variant transition group-data-[state=open]:rotate-180" />
              </Accordion.Trigger>

              <Accordion.Content className="mt-2 overflow-hidden rounded-md border border-outline-variant bg-surface-container-low px-4 py-3">
                <p
                  className="text-sm leading-relaxed text-on-surface-variant"
                  dangerouslySetInnerHTML={{ __html: formatMarkdownToHtml(content) }}
                />
              </Accordion.Content>
            </Accordion.Item>
          )
        })}
      </Accordion.Root>
    </Card>
  )
}
