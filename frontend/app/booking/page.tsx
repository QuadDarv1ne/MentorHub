'use client'

import { useState } from 'react'
import { Calendar, Clock, Check } from 'lucide-react'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'

interface TimeSlot {
  time: string
  available: boolean
  booked?: boolean
}

interface Mentor {
  id: number
  name: string
  title: string
  image?: string
  rate: number
  rating: number
  reviews: number
  specialization: string[]
  availability: {
    [key: string]: TimeSlot[]
  }
}

const DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
const MONTHS = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']

export default function BookingPage() {
  const [selectedMentorId, setSelectedMentorId] = useState<number | null>(null)
  const [selectedDate, setSelectedDate] = useState<string | null>(null)
  const [selectedTime, setSelectedTime] = useState<string | null>(null)
  const [bookingStep, setBookingStep] = useState(1)

  const mockMentors: Mentor[] = [
    {
      id: 1,
      name: 'Иван Петров',
      title: 'Senior React Developer',
      rate: 1500,
      rating: 4.9,
      reviews: 342,
      specialization: ['React', 'JavaScript', 'Web Development'],
      availability: {
        '2025-11-22': [
          { time: '09:00', available: true },
          { time: '10:00', available: true },
          { time: '11:00', available: false, booked: true },
          { time: '14:00', available: true },
          { time: '15:00', available: true }
        ],
        '2025-11-23': [
          { time: '10:00', available: true },
          { time: '11:00', available: true },
          { time: '15:00', available: true },
          { time: '16:00', available: true }
        ],
        '2025-11-24': [
          { time: '09:00', available: true },
          { time: '14:00', available: true },
          { time: '16:00', available: true }
        ]
      }
    },
    {
      id: 2,
      name: 'Мария Сидорова',
      title: 'Full Stack Developer',
      rate: 1200,
      rating: 4.8,
      reviews: 287,
      specialization: ['Node.js', 'React', 'MongoDB'],
      availability: {
        '2025-11-22': [
          { time: '10:00', available: true },
          { time: '11:00', available: true },
          { time: '13:00', available: true },
          { time: '14:00', available: true }
        ],
        '2025-11-23': [
          { time: '09:00', available: true },
          { time: '10:00', available: true },
          { time: '14:00', available: true }
        ]
      }
    },
    {
      id: 3,
      name: 'Алексей Иванов',
      title: 'Backend & DevOps Specialist',
      rate: 1800,
      rating: 4.7,
      reviews: 215,
      specialization: ['Node.js', 'DevOps', 'AWS'],
      availability: {
        '2025-11-22': [
          { time: '15:00', available: true },
          { time: '16:00', available: true }
        ],
        '2025-11-25': [
          { time: '10:00', available: true },
          { time: '11:00', available: true },
          { time: '14:00', available: true }
        ]
      }
    },
    {
      id: 4,
      name: 'Екатерина Лебедева',
      title: 'Frontend Architect',
      rate: 1600,
      rating: 4.9,
      reviews: 298,
      specialization: ['React', 'TypeScript', 'UI/UX'],
      availability: {
        '2025-11-22': [
          { time: '09:00', available: true },
          { time: '11:00', available: true },
          { time: '13:00', available: true }
        ],
        '2025-11-24': [
          { time: '10:00', available: true },
          { time: '15:00', available: true }
        ]
      }
    },
    {
      id: 5,
      name: 'Дмитрий Волков',
      title: 'Technical Interviewer',
      rate: 1400,
      rating: 4.6,
      reviews: 156,
      specialization: ['Algorithms', 'System Design', 'Interview Prep'],
      availability: {
        '2025-11-22': [
          { time: '10:00', available: true },
          { time: '14:00', available: true },
          { time: '16:00', available: true }
        ],
        '2025-11-23': [
          { time: '09:00', available: true },
          { time: '15:00', available: true }
        ]
      }
    }
  ]

  const selectedMentor = mockMentors.find(m => m.id === selectedMentorId)
  const dates = selectedMentor ? Object.keys(selectedMentor.availability) : []
  const timeSlots = selectedDate && selectedMentor ? selectedMentor.availability[selectedDate] : []

  const getDateLabel = (dateStr: string) => {
    const date = new Date(dateStr)
    const day = date.getDate()
    const month = MONTHS[date.getMonth()]
    const dayOfWeek = DAYS[date.getDay() - 1]
    return `${dayOfWeek}, ${day} ${month}`
  }

  const handleBooking = () => {
    if (selectedMentorId && selectedDate && selectedTime) {
      alert(`Сессия забронирована!\nМентор: ${selectedMentor?.name}\nДата: ${getDateLabel(selectedDate)}\nВремя: ${selectedTime}`)
      setBookingStep(1)
      setSelectedMentorId(null)
      setSelectedDate(null)
      setSelectedTime(null)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Заголовок */}
      <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4">Забронируйте сессию</h1>
          <p className="text-indigo-100 text-lg">
            Выберите ментора и удобное время для встречи
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Прогресс */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            {[1, 2, 3].map(step => (
              <div key={step} className="flex items-center flex-1">
                <div
                  className={`flex items-center justify-center h-10 w-10 rounded-full font-semibold transition-all ${
                    step <= bookingStep
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {step}
                </div>
                {step < 3 && (
                  <div
                    className={`flex-1 h-1 mx-2 transition-all ${
                      step < bookingStep ? 'bg-indigo-600' : 'bg-gray-300'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between text-sm text-gray-600">
            <span className={bookingStep >= 1 ? 'text-indigo-600 font-semibold' : ''}>Выбор ментора</span>
            <span className={bookingStep >= 2 ? 'text-indigo-600 font-semibold' : ''}>Выбор даты/времени</span>
            <span className={bookingStep >= 3 ? 'text-indigo-600 font-semibold' : ''}>Подтверждение</span>
          </div>
        </div>

        {/* Шаг 1: Выбор ментора */}
        {bookingStep === 1 && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Выберите ментора</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {mockMentors.map(mentor => (
                <Card
                  key={mentor.id}
                  className={`cursor-pointer transition-all ${
                    selectedMentorId === mentor.id ? 'ring-2 ring-indigo-600 shadow-lg' : 'hover:shadow-lg'
                  }`}
                  onClick={() => {
                    setSelectedMentorId(mentor.id)
                    setBookingStep(2)
                  }}
                >
                  {/* Аватар */}
                  <div className="w-16 h-16 bg-gradient-to-br from-indigo-400 to-indigo-600 rounded-full flex items-center justify-center text-white text-2xl font-bold mb-4">
                    {mentor.name.charAt(0)}
                  </div>

                  {/* Информация */}
                  <h3 className="text-lg font-semibold text-gray-900">{mentor.name}</h3>
                  <p className="text-sm text-gray-600 mb-3">{mentor.title}</p>

                  {/* Специализация */}
                  <div className="flex flex-wrap gap-1 mb-4">
                    {mentor.specialization.map(spec => (
                      <Badge key={spec} variant="info">
                        {spec}
                      </Badge>
                    ))}
                  </div>

                  {/* Рейтинг и цена */}
                  <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                    <div className="flex items-center space-x-2">
                      <span className="text-yellow-400">★</span>
                      <span className="font-semibold text-gray-900">{mentor.rating}</span>
                      <span className="text-xs text-gray-500">({mentor.reviews})</span>
                    </div>
                    <p className="text-lg font-bold text-indigo-600">{mentor.rate}₽/ч</p>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Шаг 2: Выбор даты и времени */}
        {bookingStep === 2 && selectedMentor && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Выберите дату и время</h2>
                <p className="text-gray-600">Ментор: <span className="font-semibold">{selectedMentor.name}</span></p>
              </div>
              <button
                onClick={() => setBookingStep(1)}
                className="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                Вернуться
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Выбор даты */}
              <div className="lg:col-span-1">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                  <Calendar size={20} className="text-indigo-600" />
                  <span>Дата</span>
                </h3>
                <div className="space-y-2">
                  {dates.map(date => (
                    <button
                      key={date}
                      onClick={() => setSelectedDate(date)}
                      className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                        selectedDate === date
                          ? 'border-indigo-600 bg-indigo-50'
                          : 'border-gray-200 hover:border-indigo-300'
                      }`}
                    >
                      <p className="font-semibold text-gray-900">{getDateLabel(date)}</p>
                      <p className="text-xs text-gray-600 mt-1">
                        Свободных слотов: {selectedMentor.availability[date].filter(s => s.available).length}
                      </p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Выбор времени */}
              <div className="lg:col-span-2">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                  <Clock size={20} className="text-indigo-600" />
                  <span>Время</span>
                </h3>
                {selectedDate ? (
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {timeSlots.map(slot => (
                      <button
                        key={slot.time}
                        disabled={!slot.available}
                        onClick={() => {
                          if (slot.available) {
                            setSelectedTime(slot.time)
                          }
                        }}
                        className={`p-3 rounded-lg border-2 font-medium transition-all ${
                          selectedTime === slot.time && slot.available
                            ? 'border-indigo-600 bg-indigo-50 text-indigo-600'
                            : slot.available
                            ? 'border-gray-200 text-gray-900 hover:border-indigo-300'
                            : 'border-gray-100 bg-gray-50 text-gray-400 cursor-not-allowed'
                        }`}
                      >
                        {slot.time}
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 bg-gray-50 rounded-lg text-center text-gray-600">
                    Выберите дату для просмотра доступного времени
                  </div>
                )}

                {/* Итоговая информация */}
                {selectedDate && selectedTime && (
                  <div className="mt-8 p-6 bg-indigo-50 rounded-lg border border-indigo-200">
                    <h4 className="font-semibold text-gray-900 mb-3">Резюме бронирования</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Ментор:</span>
                        <span className="font-semibold text-gray-900">{selectedMentor.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Дата:</span>
                        <span className="font-semibold text-gray-900">{getDateLabel(selectedDate)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Время:</span>
                        <span className="font-semibold text-gray-900">{selectedTime}</span>
                      </div>
                      <div className="flex justify-between pt-2 border-t border-indigo-200">
                        <span className="text-gray-600">Цена:</span>
                        <span className="font-bold text-indigo-600">{selectedMentor.rate}₽</span>
                      </div>
                    </div>
                    <button
                      onClick={() => setBookingStep(3)}
                      className="w-full mt-4 px-4 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                      Продолжить к подтверждению
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Шаг 3: Подтверждение и контакты */}
        {bookingStep === 3 && selectedMentor && selectedDate && selectedTime && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Подтверждение бронирования</h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Детали */}
              <Card>
                <h3 className="font-semibold text-gray-900 mb-6">Детали сессии</h3>
                <div className="space-y-4">
                  <div className="flex items-start space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-indigo-400 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
                      {selectedMentor.name.charAt(0)}
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{selectedMentor.name}</p>
                      <p className="text-sm text-gray-600">{selectedMentor.title}</p>
                    </div>
                  </div>

                  <div className="space-y-3 pt-4 border-t border-gray-200">
                    <div className="flex items-center space-x-3 text-gray-900">
                      <Calendar size={20} className="text-indigo-600" />
                      <span>{getDateLabel(selectedDate)}</span>
                    </div>
                    <div className="flex items-center space-x-3 text-gray-900">
                      <Clock size={20} className="text-indigo-600" />
                      <span>{selectedTime}</span>
                    </div>
                    <div className="flex items-center space-x-3 text-lg font-bold text-indigo-600">
                      💰
                      <span>{selectedMentor.rate}₽</span>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Форма контактов */}
              <Card>
                <h3 className="font-semibold text-gray-900 mb-6">Ваши контакты</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Полное имя</label>
                    <input
                      type="text"
                      title="Введите ваше имя"
                      placeholder="Ваше имя"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      defaultValue="Максим Иванов"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                    <input
                      type="email"
                      title="Введите email"
                      placeholder="ваш@email.com"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      defaultValue="maksim@example.com"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Телефон</label>
                    <input
                      type="tel"
                      title="Введите телефон"
                      placeholder="+7 (999) 999-99-99"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      defaultValue="+7 915 048-02-49"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Коментарий</label>
                    <textarea
                      title="Добавьте коментарий"
                      placeholder="Расскажите о том, что вы хотите обсудить на сессии..."
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      rows={4}
                    />
                  </div>
                </div>
              </Card>
            </div>

            {/* Действия */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => setBookingStep(2)}
                className="px-6 py-3 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 font-medium transition-colors"
              >
                Вернуться
              </button>
              <button
                onClick={handleBooking}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors flex items-center space-x-2"
              >
                <Check size={20} />
                <span>Подтвердить бронирование</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
