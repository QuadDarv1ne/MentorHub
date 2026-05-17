/**
 * Re-export from the canonical auth hook.
 *
 * This file previously duplicated auth logic. All consumers now use
 * `@/hooks/useAuth` as the single source of truth.
 *
 * Import from `@/hooks/useAuth` instead — this file exists only for
 * backwards compatibility during migration.
 */

export {
  useAuth,
  useOptionalAuth,
  useRole,
  useOwnership,
} from '@/hooks/useAuth'

export type { UseAuthReturn, UseAuthOptions } from '@/hooks/useAuth'
