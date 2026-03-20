/**
 * Тесты для компонента Avatar
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect } from '@jest/globals'
import '@testing-library/jest-dom'
import Avatar from '../Avatar'

describe('Avatar Component', () => {
  it('должен рендерить изображение с imageUrl', () => {
    const testImageUrl = 'https://example.com/avatar.jpg'
    const testName = 'John Doe'

    render(<Avatar name={testName} imageUrl={testImageUrl} />)

    const img = screen.getByRole('img', { name: testName })
    expect(img).toBeInTheDocument()
  })

  it('должен рендерить фоллбэк с инициалами без imageUrl', () => {
    const testName = 'John Doe'
    render(<Avatar name={testName} />)

    // Проверяем, что есть текст с инициалами
    expect(screen.getByText('JD')).toBeInTheDocument()
  })

  it('должен применять кастомные классы', () => {
    const testClass = 'custom-class'
    const testName = 'Test User'
    render(<Avatar name={testName} className={testClass} />)

    const container = document.querySelector(`.${testClass}`)
    expect(container).toBeInTheDocument()
  })

  it('должен применять размеры sm', () => {
    const testName = 'Test User'
    render(<Avatar name={testName} size="sm" />)

    const container = document.querySelector('.h-8')
    expect(container).toBeInTheDocument()
  })

  it('должен применять размеры md', () => {
    const testName = 'Test User'
    render(<Avatar name={testName} size="md" />)

    const container = document.querySelector('.h-12')
    expect(container).toBeInTheDocument()
  })

  it('должен применять размеры lg', () => {
    const testName = 'Test User'
    render(<Avatar name={testName} size="lg" />)

    const container = document.querySelector('.h-16')
    expect(container).toBeInTheDocument()
  })

  it('должен применять круглую форму', () => {
    const testName = 'Test User'
    render(<Avatar name={testName} />)

    const container = document.querySelector('.rounded-full')
    expect(container).toBeInTheDocument()
  })
})
