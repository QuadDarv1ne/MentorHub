/**
 * Тесты для компонента Avatar
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect } from '@jest/globals'
import Avatar from '../Avatar'

describe('Avatar Component', () => {
  it('должен рендерить изображение с src', () => {
    const testSrc = 'https://example.com/avatar.jpg'
    const testAlt = 'User Avatar'
    
    render(<Avatar src={testSrc} alt={testAlt} />)
    
    const img = screen.getByRole('img', { name: testAlt })
    expect(img).toHaveAttribute('src', testSrc)
  })

  it('должен рендерить фоллбэк иконку без src', () => {
    render(<Avatar alt="User" />)
    
    // Проверяем, что есть SVG иконка (fallback)
    const svg = document.querySelector('svg')
    expect(svg).toBeInTheDocument()
  })

  it('должен применять кастомные классы', () => {
    const testClass = 'custom-class'
    render(<Avatar alt="User" className={testClass} />)
    
    const container = screen.getByTestId('avatar-container') || document.querySelector(`.${testClass}`)
    expect(container).toBeInTheDocument()
  })

  it('должен применять размеры sm', () => {
    render(<Avatar alt="User" size="sm" />)
    
    const img = screen.getByRole('img')
    expect(img).toHaveClass('w-8', 'h-8')
  })

  it('должен применять размеры md', () => {
    render(<Avatar alt="User" size="md" />)
    
    const img = screen.getByRole('img')
    expect(img).toHaveClass('w-12', 'h-12')
  })

  it('должен применять размеры lg', () => {
    render(<Avatar alt="User" size="lg" />)
    
    const img = screen.getByRole('img')
    expect(img).toHaveClass('w-16', 'h-16')
  })

  it('должен применять круглую форму', () => {
    render(<Avatar alt="User" rounded />)
    
    const img = screen.getByRole('img')
    expect(img).toHaveClass('rounded-full')
  })
})
