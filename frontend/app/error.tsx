'use client'

import { useEffect } from 'react'
import { EnhancedAppError } from '@/components/ErrorBoundary'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log ошибки в сервис мониторинга (например, Sentry)
    console.error('Application error:', error)
  }, [error])

  // Use the enhanced error component
  return <EnhancedAppError error={error} reset={reset} />
}