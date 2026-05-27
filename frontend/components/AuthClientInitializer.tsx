'use client'

import { useEffect } from 'react'
import { initAuthClient } from '@/lib/api/auth'

/**
 * Initializes the API client's automatic 401 token-refresh interceptor.
 * Without this, expired access tokens cause unhandled 401 errors instead
 * of silently refreshing via the refresh token.
 */
export default function AuthClientInitializer() {
  useEffect(() => {
    initAuthClient()
  }, [])

  return null
}
