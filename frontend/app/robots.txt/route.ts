export function GET() {
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL
  const sitemapUrl = baseUrl ? `${baseUrl}/sitemap.xml` : '/sitemap.xml'
  const body = `User-agent: *
Disallow:

Sitemap: ${sitemapUrl}`
  return new Response(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } })
}
