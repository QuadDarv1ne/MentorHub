import { Star } from 'lucide-react'
import Card from './Card'

interface TestimonialCardProps {
  name: string
  role: string
  text: string
  rating: number
}

export default function TestimonialCard({
  name,
  role,
  text,
  rating
}: TestimonialCardProps) {
  return (
    <Card padding="md">
      <div className="flex items-center mb-4">
        <div className="h-12 w-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold mr-3">
          {name.split(' ').map(n => n[0]).join('')}
        </div>
        <div>
          <h4 className="font-semibold text-gray-900">{name}</h4>
          <p className="text-sm text-gray-600">{role}</p>
        </div>
      </div>
      <div className="flex mb-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <Star
            key={i}
            className={`h-4 w-4 ${
              i < rating
                ? 'text-yellow-400 fill-current'
                : 'text-gray-300'
            }`}
          />
        ))}
      </div>
      <p className="text-gray-700 italic">&ldquo;{text}&rdquo;</p>
    </Card>
  )
}
