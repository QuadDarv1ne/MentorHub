import { Metadata } from 'next'
import Hero from '@/components/Hero'
import Features from '@/components/Features'
import MentorsPreview from '@/components/MentorsPreview'
import Testimonials from '@/components/Testimonials'
import CallToAction from '@/components/CallToAction'
import PopularQuestions from '@/components/PopularQuestions'
import { seoPresets } from '@/lib/utils/seo'
import { 
  LazyStatistics, 
  LazyCodingTasks, 
  LazyInterviewTrainer, 
  LazyQuestionDatabase 
} from '@/components/LazyComponents'

export const metadata: Metadata = seoPresets.home()

export default function HomePage() {
  return (
    <>
      <Hero />
      <LazyStatistics />
      <Features />
      <LazyCodingTasks />
      <LazyInterviewTrainer />
      <LazyQuestionDatabase />
      <PopularQuestions />
      <MentorsPreview />
      <Testimonials />
      <CallToAction />
    </>
  )
}

