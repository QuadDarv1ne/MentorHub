/**
 * Компонентные тесты для LoadingSpinner компонента
 */

import { render, screen } from '@testing-library/react'
import LoadingSpinner, { PageLoader, SectionLoader, InlineLoader } from '@/components/LoadingSpinner'

describe('LoadingSpinner Components', () => {
  describe('LoadingSpinner', () => {
    test('рендерит LoadingSpinner по умолчанию', () => {
      render(<LoadingSpinner />)
      expect(screen.getByRole('status')).toBeInTheDocument()
    })

    test('рендерит текст загрузки', () => {
      render(<LoadingSpinner text="Loading..." />)
      expect(screen.getByText('Loading...')).toBeInTheDocument()
    })

    test('рендерит fullScreen режим', () => {
      render(<LoadingSpinner fullScreen />)
      expect(screen.getByRole('status')).toBeInTheDocument()
    })

    test('применяет размер sm', () => {
      const { container } = render(<LoadingSpinner size="sm" />)
      expect(container.querySelector('.h-8')).toBeInTheDocument()
    })

    test('применяет размер md', () => {
      const { container } = render(<LoadingSpinner size="md" />)
      expect(container.querySelector('.h-12')).toBeInTheDocument()
    })

    test('применяет размер lg', () => {
      const { container } = render(<LoadingSpinner size="lg" />)
      expect(container.querySelector('.h-16')).toBeInTheDocument()
    })

    test('рендерит variant dots', () => {
      render(<LoadingSpinner variant="dots" />)
      expect(screen.getAllByRole('status').length).toBeGreaterThan(0)
    })

    test('рендерит variant bars', () => {
      render(<LoadingSpinner variant="bars" />)
      expect(screen.getAllByRole('status').length).toBeGreaterThan(0)
    })

    test('рендерит variant pulse', () => {
      render(<LoadingSpinner variant="pulse" />)
      expect(screen.getByRole('status')).toBeInTheDocument()
    })
  })

  describe('PageLoader', () => {
    test('рендерит PageLoader', () => {
      render(<PageLoader />)
      expect(screen.getByText(/загрузка страницы/i)).toBeInTheDocument()
    })

    test('рендерит кастомный текст', () => {
      render(<PageLoader text="Custom loading..." />)
      expect(screen.getByText('Custom loading...')).toBeInTheDocument()
    })

    test('рендерит вспомогательный текст', () => {
      render(<PageLoader />)
      expect(screen.getByText(/это может занять/i)).toBeInTheDocument()
    })
  })

  describe('SectionLoader', () => {
    test('рендерит SectionLoader', () => {
      render(<SectionLoader />)
      expect(screen.getByText(/загрузка данных/i)).toBeInTheDocument()
    })

    test('рендерит кастомный текст', () => {
      render(<SectionLoader text="Loading section..." />)
      expect(screen.getByText('Loading section...')).toBeInTheDocument()
    })

    test('рендерит три dots анимации', () => {
      render(<SectionLoader />)
      const dots = screen.getAllByRole('status')
      expect(dots.length).toBeGreaterThanOrEqual(3)
    })
  })

  describe('InlineLoader', () => {
    test('рендерит InlineLoader', () => {
      render(<InlineLoader />)
      expect(screen.getByRole('status')).toBeInTheDocument()
    })

    test('рендерит размер sm по умолчанию', () => {
      const { container } = render(<InlineLoader />)
      expect(container.querySelector('.h-4')).toBeInTheDocument()
    })

    test('рендерит размер md', () => {
      const { container } = render(<InlineLoader size="md" />)
      expect(container.querySelector('.h-6')).toBeInTheDocument()
    })
  })
})
