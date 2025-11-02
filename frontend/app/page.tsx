import Header from '@/components/Header'
import Hero from '@/components/Hero'
import Features from '@/components/Features'
import CodingTasks from '@/components/CodingTasks'
import InterviewTrainer from '@/components/InterviewTrainer'
import QuestionDatabase from '@/components/QuestionDatabase'
import PopularQuestions from '@/components/PopularQuestions'
import MentorsPreview from '@/components/MentorsPreview'
import Footer from '@/components/Footer'

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow">
        <Hero />
        <Features />
        <CodingTasks />
        <InterviewTrainer />
        <QuestionDatabase />
        <PopularQuestions />
        <MentorsPreview />
      </main>
      <Footer />
    </div>
  )
}

