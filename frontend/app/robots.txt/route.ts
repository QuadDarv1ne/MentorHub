export function GET() {
  const body = `User-agent: *
Disallow:

Sitemap: ${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'}/sitemap.xml`
  return new Response(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } })
}
