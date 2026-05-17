'use client'

import { useEffect, useRef } from 'react'
import { publicRequest } from '@/lib/api/client'

interface UserEvent {
  event_type: string
  user_id?: string
  page_url: string
  timestamp: string
  metadata?: Record<string, any>
}

export function useAnalytics() {
  const initialized = useRef(false)

  useEffect(() => {
    if (typeof window === 'undefined') return

    initialized.current = true

    // Track page views
    const trackPageView = () => {
      const event: UserEvent = {
        event_type: 'page_view',
        page_url: window.location.href,
        timestamp: new Date().toISOString()
      }
      sendEvent(event)
    }

    // Track clicks
    const trackClicks = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (target.closest('a') || target.closest('button')) {
        const event: UserEvent = {
          event_type: 'click',
          page_url: window.location.href,
          timestamp: new Date().toISOString(),
          metadata: {
            element: target.tagName,
            text: target.textContent?.slice(0, 100)
          }
        }
        sendEvent(event)
      }
    }

    // Track scroll depth
    let scrollDepth = 0
    const trackScroll = () => {
      const depth = Math.round((window.scrollY / document.body.scrollHeight) * 100)
      if (depth > scrollDepth && depth % 25 === 0) {
        scrollDepth = depth
        const event: UserEvent = {
          event_type: 'scroll_depth',
          page_url: window.location.href,
          timestamp: new Date().toISOString(),
          metadata: { depth }
        }
        sendEvent(event)
      }
    }

    // Track time on page
    const startTime = Date.now()
    const trackTimeSpent = () => {
      const timeSpent = Math.round((Date.now() - startTime) / 1000)
      const event: UserEvent = {
        event_type: 'time_on_page',
        page_url: window.location.href,
        timestamp: new Date().toISOString(),
        metadata: { seconds: timeSpent }
      }
      sendEvent(event)
    }

    // Track form submissions
    const trackFormSubmit = (e: Event) => {
      const form = e.target as HTMLFormElement
      const event: UserEvent = {
        event_type: 'form_submit',
        page_url: window.location.href,
        timestamp: new Date().toISOString(),
        metadata: {
          form_id: form.id,
          form_action: form.action
        }
      }
      sendEvent(event)
    }

    // Track errors
    const trackErrors = (e: ErrorEvent) => {
      const event: UserEvent = {
        event_type: 'error',
        page_url: window.location.href,
        timestamp: new Date().toISOString(),
        metadata: {
          message: e.message,
          source: e.filename,
          line: e.lineno,
          column: e.colno
        }
      }
      sendEvent(event)
    }

    // Initialize listeners
    window.addEventListener('popstate', trackPageView)
    document.addEventListener('click', trackClicks)
    window.addEventListener('scroll', trackScroll, { passive: true })
    window.addEventListener('beforeunload', trackTimeSpent)
    document.addEventListener('submit', trackFormSubmit)
    window.addEventListener('error', trackErrors)

    // Initial page view
    trackPageView()

    return () => {
      window.removeEventListener('popstate', trackPageView)
      document.removeEventListener('click', trackClicks)
      window.removeEventListener('scroll', trackScroll)
      window.removeEventListener('beforeunload', trackTimeSpent)
      document.removeEventListener('submit', trackFormSubmit)
      window.removeEventListener('error', trackErrors)
    }
  }, [])

  const sendEvent = async (event: UserEvent) => {
    try {
      await publicRequest<void>('/analytics/track', {
        method: 'POST',
        body: JSON.stringify(event)
      })
    } catch (error) {
      // Silently fail - analytics shouldn't break the app
      console.error('Analytics event failed:', error)
    }
  }

  const trackCustomEvent = (eventType: string, metadata?: Record<string, any>) => {
    const event: UserEvent = {
      event_type: eventType,
      page_url: window.location.href,
      timestamp: new Date().toISOString(),
      metadata
    }
    sendEvent(event)
  }

  return { trackCustomEvent }
}
