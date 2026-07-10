export function getBackendUrl(): string {
  const url =
    process.env.BACKEND_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    process.env.NEXT_PUBLIC_API_URL

  if (!url) {
    throw new Error(
      'Backend URL not configured. Set BACKEND_URL, NEXT_PUBLIC_API_BASE_URL, or NEXT_PUBLIC_API_URL.',
    )
  }

  return url
}

export function extractBearerToken(request: Request): string | null {
  const header = request.headers.get('Authorization')
  if (!header?.startsWith('Bearer ')) return null
  return header.slice(7)
}
