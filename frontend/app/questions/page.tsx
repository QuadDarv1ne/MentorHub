import PopularQuestions from "@/components/PopularQuestions"
import QuestionDatabase from "@/components/QuestionDatabase"

export const metadata = {
  title: "Вопросы для собеседований — MentorHub",
  description: "Популярные вопросы и база задач для подготовки к собеседованиям в IT.",
}

export default function QuestionsPage() {
  return (
    <main className="container mx-auto max-w-6xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-6">Вопросы для собеседований</h1>
      <div className="grid gap-8 md:grid-cols-2">
        <section className="rounded-xl border bg-white p-6">
          <h2 className="text-xl font-semibold mb-4">Популярные вопросы</h2>
          <PopularQuestions />
        </section>
        <section className="rounded-xl border bg-white p-6">
          <h2 className="text-xl font-semibold mb-4">База вопросов</h2>
          <QuestionDatabase />
        </section>
      </div>
    </main>
  )
}
