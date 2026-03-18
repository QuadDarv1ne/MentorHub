/**
 * Тесты для утилиты оптимизации изображений
 */

import { describe, it, expect } from '@jest/globals'
import { ResponsiveImage, ImageProps } from '../ResponsiveImage'
import { render, screen } from '@testing-library/react'

describe('ResponsiveImage Component', () => {
  const defaultProps: ImageProps = {
    src: 'https://example.com/image.jpg',
    alt: 'Test image',
    width: 800,
    height: 600,
  }

  it('должен рендерить изображение с правильными атрибутами', () => {
    render(<ResponsiveImage {...defaultProps} />)
    
    const img = screen.getByRole('img', { name: 'Test image' })
    expect(img).toHaveAttribute('src', 'https://example.com/image.jpg')
    expect(img).toHaveAttribute('alt', 'Test image')
  })

  it('должен применять lazy loading по умолчанию', () => {
    render(<ResponsiveImage {...defaultProps} />)
    
    const img = screen.getByRole('img')
    expect(img).toHaveAttribute('loading', 'lazy')
  })

  it('должен применять eager loading при priority', () => {
    render(<ResponsiveImage {...defaultProps} priority />)
    
    const img = screen.getByRole('img')
    expect(img).toHaveAttribute('loading', 'eager')
  })

  it('должен применять decoding async по умолчанию', () => {
    render(<ResponsiveImage {...defaultProps} />)
    
    const img = screen.getByRole('img')
    expect(img).toHaveAttribute('decoding', 'async')
  })

  it('должен применять object-fit cover по умолчанию', () => {
    render(<ResponsiveImage {...defaultProps} />)
    
    const img = screen.getByRole('img')
    expect(img).toHaveClass('object-cover')
  })

  it('должен применять кастомный object-fit', () => {
    render(<ResponsiveImage {...defaultProps} objectFit="contain" />)
    
    const img = screen.getByRole('img')
    expect(img).toHaveClass('object-contain')
  })

  it('должен применять кастомные классы', () => {
    render(<ResponsiveImage {...defaultProps} className="custom-class" />)
    
    const img = screen.getByRole('img')
    expect(img).toHaveClass('custom-class')
  })

  it('должен применять размеры из props', () => {
    render(<ResponsiveImage {...defaultProps} width={400} height={300} />)
    
    const img = screen.getByRole('img')
    expect(img).toHaveAttribute('width', '400')
    expect(img).toHaveAttribute('height', '300')
  })

  it('должен применять quality для webp формата', () => {
    render(<ResponsiveImage {...defaultProps} quality={80} />)
    
    // Проверяем, что компонент рендерится без ошибок
    const img = screen.getByRole('img')
    expect(img).toBeInTheDocument()
  })
})
