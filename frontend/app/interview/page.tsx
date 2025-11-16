import InterviewTrainer from "@/components/InterviewTrainer"

export const metadata = {
  title: "Тренажёр собеседований — MentorHub",
  description: "Потренируйтесь проходить технические собеседования с интерактивным тренажёром.",
}

export default function InterviewPage() {
  return (
    <main className="container mx-auto max-w-5xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-6">Тренажёр собеседований</h1>
      <div className="rounded-xl border bg-white p-6">
        <InterviewTrainer />
      </div>
    </main>
  )
}
