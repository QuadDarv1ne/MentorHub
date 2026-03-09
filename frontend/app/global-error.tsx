'use client'

import { useEffect } from 'react'
import { EnhancedAppError } from '@/components/ErrorBoundary'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log критических ошибок
    console.error('Critical application error:', error)
  }, [error])

  // Use the enhanced error component
  return <EnhancedAppError error={error} reset={reset} />
}