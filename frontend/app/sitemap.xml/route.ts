const routes = [
  '/',
  '/about',
  '/pricing',
  '/faq',
  '/contact',
  '/mentors',
  '/courses',
  '/courses/stepik',
  '/sessions',
  '/learning',
  '/roadmap',
  '/dashboard',
  '/legal/terms',
  '/legal/privacy',
  '/legal/cookies',
  '/legal/dpa',
  '/legal/refund',
  '/legal/aup',
  '/legal/community',
  '/legal/license',
]

export function GET() {
  const base = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'
  const updated = new Date().toISOString()
  const urls = routes
    .map((path) => `    <url>\n      <loc>${base}${path}</loc>\n      <lastmod>${updated}</lastmod>\n      <changefreq>weekly</changefreq>\n      <priority>0.7</priority>\n    </url>`) 
    .join('\n')

  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>`
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } })
}
