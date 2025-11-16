import CodingTasks from "@/components/CodingTasks"

export const metadata = {
  title: "Лайв-кодинг задачи — MentorHub",
  description: "Практикуйте решение задач по алгоритмам и структурам данных.",
}

export default function CodingPage() {
  return (
    <main className="container mx-auto max-w-5xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-6">Лайв-кодинг</h1>
      <div className="rounded-xl border bg-white p-6">
        <CodingTasks />
      </div>
    </main>
  )
}
