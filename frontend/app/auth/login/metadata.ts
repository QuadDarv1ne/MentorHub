import { Metadata } from 'next'
import { seoPresets } from '@/lib/utils/seo'

export const metadata: Metadata = seoPresets.auth.login()
