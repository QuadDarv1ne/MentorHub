
'use client'

import { useEffect, useState } from 'react'
import Head from 'next/head'

type Consent = {
  necessary: boolean
  analytics: boolean
  marketing: boolean
}

const defaultConsent: Consent = { necessary: true, analytics: false, marketing: false }

export default function ConsentPage() {
  const [consent, setConsent] = useState<Consent>(defaultConsent)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    try {
      const raw = localStorage.getItem('cookie_consent')
      if (raw) setConsent({ ...defaultConsent, ...JSON.parse(raw) })
    } catch {}
  }, [])

  const save = () => {
    localStorage.setItem('cookie_consent', JSON.stringify(consent))
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <>
      <Head>
        <title>Настройки cookie — MentorHub</title>
      </Head>
      <div className="prose max-w-none">
        <h2>Настройки cookie</h2>
        <p>Управляйте категориями cookie. Необходимые cookie включены всегда.</p>
        <div className="not-prose mt-4 space-y-3">
          <label className="flex items-center gap-3">
            <input type="checkbox" checked disabled className="h-4 w-4" />
            <span>Необходимые</span>
          </label>
          <label className="flex items-center gap-3">
            <input type="checkbox" className="h-4 w-4" checked={consent.analytics} onChange={e => setConsent({ ...consent, analytics: e.target.checked })} />
            <span>Аналитические</span>
          </label>
          <label className="flex items-center gap-3">
            <input type="checkbox" className="h-4 w-4" checked={consent.marketing} onChange={e => setConsent({ ...consent, marketing: e.target.checked })} />
            <span>Маркетинговые</span>
          </label>
          <button onClick={save} className="mt-4 rounded-md bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700">Сохранить</button>
          {saved && <p className="text-sm text-green-600">Сохранено</p>}
        </div>
      </div>
    </>
  )
}
