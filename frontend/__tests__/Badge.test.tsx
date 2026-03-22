/**
 * Компонентные тесты для Badge компонента
 */

import { render, screen } from '@testing-library/react'
import Badge from '@/components/ui/Badge'

describe('Badge Component', () => {
  test('рендерит Badge с текстом', () => {
    render(<Badge>New</Badge>)
    expect(screen.getByText('New')).toBeInTheDocument()
  })

  test('рендерит Badge с variant default', () => {
    const { container } = render(<Badge variant="default">Default</Badge>)
    expect(container.firstChild).toHaveClass('bg-gray-100')
    expect(container.firstChild).toHaveClass('text-gray-800')
  })

  test('рендерит Badge с variant success', () => {
    const { container } = render(<Badge variant="success">Success</Badge>)
    expect(container.firstChild).toHaveClass('bg-green-100')
    expect(container.firstChild).toHaveClass('text-green-800')
  })

  test('рендерит Badge с variant warning', () => {
    const { container } = render(<Badge variant="warning">Warning</Badge>)
    expect(container.firstChild).toHaveClass('bg-yellow-100')
    expect(container.firstChild).toHaveClass('text-yellow-800')
  })

  test('рендерит Badge с variant danger', () => {
    const { container } = render(<Badge variant="danger">Danger</Badge>)
    expect(container.firstChild).toHaveClass('bg-red-100')
    expect(container.firstChild).toHaveClass('text-red-800')
  })

  test('рендерит Badge с variant info', () => {
    const { container } = render(<Badge variant="info">Info</Badge>)
    expect(container.firstChild).toHaveClass('bg-blue-100')
    expect(container.firstChild).toHaveClass('text-blue-800')
  })

  test('рендерит Badge с размером sm', () => {
    const { container } = render(<Badge size="sm">Small</Badge>)
    expect(container.firstChild).toHaveClass('text-xs')
    expect(container.firstChild).toHaveClass('px-2')
    expect(container.firstChild).toHaveClass('py-0.5')
  })

  test('рендерит Badge с размером md', () => {
    const { container } = render(<Badge size="md">Medium</Badge>)
    expect(container.firstChild).toHaveClass('text-sm')
    expect(container.firstChild).toHaveClass('px-2.5')
    expect(container.firstChild).toHaveClass('py-1')
  })

  test('рендерит Badge с размером lg', () => {
    const { container } = render(<Badge size="lg">Large</Badge>)
    expect(container.firstChild).toHaveClass('text-base')
    expect(container.firstChild).toHaveClass('px-3')
    expect(container.firstChild).toHaveClass('py-1.5')
  })

  test('рендерит Badge с кастомным className', () => {
    const { container } = render(<Badge className="custom-class">Custom</Badge>)
    expect(container.firstChild).toHaveClass('custom-class')
  })

  test('передаёт дополнительные HTML props', () => {
    render(<Badge data-testid="custom-badge" role="status">Test</Badge>)
    expect(screen.getByTestId('custom-badge')).toBeInTheDocument()
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  test('рендерит Badge с иконкой', () => {
    render(<Badge><span>🔥</span> Hot</Badge>)
    expect(screen.getByText('🔥')).toBeInTheDocument()
    expect(screen.getByText('Hot')).toBeInTheDocument()
  })
})
