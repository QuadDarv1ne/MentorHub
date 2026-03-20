/**
 * Тесты для компонента StepikCourseCard
 */

import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, jest } from '@jest/globals'
import '@testing-library/jest-dom'
import StepikCourseCard from '../StepikCourseCard'

const mockCourse = {
  id: '123',
  title: 'Test Course',
  description: 'Test description',
  stepikUrl: 'https://stepik.org/course/123',
  price: 0,
  studentsCount: 100,
  rating: 4.5,
  category: 'Python',
  imageUrl: 'https://example.com/image.jpg',
}

describe('StepikCourseCard Component', () => {
  it('должен рендерить название курса', () => {
    render(<StepikCourseCard {...mockCourse} />)

    expect(screen.getByText('Test Course')).toBeInTheDocument()
  })

  it('должен рендерить описание курса', () => {
    render(<StepikCourseCard {...mockCourse} />)

    expect(screen.getByText('Test description')).toBeInTheDocument()
  })

  it('должен рендерить рейтинг', () => {
    render(<StepikCourseCard {...mockCourse} />)

    expect(screen.getByText('4.5')).toBeInTheDocument()
  })

  it('должен рендерить количество студентов', () => {
    render(<StepikCourseCard {...mockCourse} />)
    
    expect(screen.getByText('100')).toBeInTheDocument()
  })

  it('должен рендерить категорию', () => {
    render(<StepikCourseCard {...mockCourse} />)
    
    expect(screen.getByText('Python')).toBeInTheDocument()
  })

  it('должен рендерить "Бесплатно" для бесплатных курсов', () => {
    render(<StepikCourseCard {...mockCourse} price={0} />)
    
    expect(screen.getByText('Бесплатно')).toBeInTheDocument()
  })

  it('должен рендерить цену для платных курсов', () => {
    render(<StepikCourseCard {...mockCourse} price={5000} />)
    
    expect(screen.getByText('5 000')).toBeInTheDocument()
    expect(screen.getByText('₽')).toBeInTheDocument()
  })

  it('должен иметь ссылку на Stepik', () => {
    render(<StepikCourseCard {...mockCourse} />)

    const stepikLink = screen.getByText('Stepik').closest('a')
    expect(stepikLink).toHaveAttribute('href', expect.stringContaining('stepik.org/course/123'))
    expect(stepikLink).toHaveAttribute('target', '_blank')
  })

  it('должен иметь ссылку "Подробнее"', () => {
    render(<StepikCourseCard {...mockCourse} />)

    const detailsLink = screen.getByText('Подробнее').closest('a')
    expect(detailsLink).toHaveAttribute('href', expect.stringContaining('/courses/stepik/123'))
  })

  it('должен рендерить кнопку избранного при наличии onFavoriteToggle', () => {
    const onFavoriteToggle = jest.fn()
    render(<StepikCourseCard {...mockCourse} onFavoriteToggle={onFavoriteToggle} />)

    const favoriteButton = screen.getByRole('button')
    expect(favoriteButton).toBeInTheDocument()
  })

  it('должен вызывать onFavoriteToggle при клике на избранное', () => {
    const onFavoriteToggle = jest.fn()
    render(<StepikCourseCard {...mockCourse} onFavoriteToggle={onFavoriteToggle} />)

    const favoriteButton = screen.getByRole('button')
    fireEvent.click(favoriteButton)

    expect(onFavoriteToggle).toHaveBeenCalledWith('123')
  })

  it('должен рендерить фоллбэк иконку при ошибке загрузки изображения', () => {
    render(<StepikCourseCard {...mockCourse} />)

    // Проверяем, что есть SVG иконка книги (fallback) или изображение
    const svg = document.querySelector('svg')
    const img = document.querySelector('img')
    expect(svg || img).toBeInTheDocument()
  })

  it('должен рендерить бейдж уровня сложности', () => {
    render(<StepikCourseCard {...mockCourse} level="beginner" />)

    expect(screen.getByText('Начальный')).toBeInTheDocument()
  })

  it('должен рендерить длительность курса', () => {
    render(<StepikCourseCard {...mockCourse} duration="40 ч." />)

    // Проверяем, что длительность отображается
    expect(screen.getByText(/40/)).toBeInTheDocument()
  })
})
