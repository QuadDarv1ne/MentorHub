import { Metadata } from 'next'
import Hero from '@/components/Hero'
import Features from '@/components/Features'
import Statistics from '@/components/Statistics'
import CodingTasks from '@/components/CodingTasks'
import InterviewTrainer from '@/components/InterviewTrainer'
import QuestionDatabase from '@/components/QuestionDatabase'
import PopularQuestions from '@/components/PopularQuestions'
import MentorsPreview from '@/components/MentorsPreview'
import Testimonials from '@/components/Testimonials'
import CallToAction from '@/components/CallToAction'
import { seoPresets } from '@/lib/utils/seo'

export const metadata: Metadata = seoPresets.home()

export default function HomePage() {
  return (
    <>
      <Hero />
      <Statistics />
      <Features />
      <CodingTasks />
      <InterviewTrainer />
      <QuestionDatabase />
      <PopularQuestions />
      <MentorsPreview />
      <Testimonials />
      <CallToAction />
    </>
  )
}

