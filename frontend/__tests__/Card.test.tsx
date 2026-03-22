/**
 * Компонентные тесты для Card компонента
 */

import { render, screen } from '@testing-library/react'
import Card from '@/components/ui/Card'

describe('Card Component', () => {
  test('рендерит Card с детьми', () => {
    render(<Card>Card content</Card>)
    expect(screen.getByText('Card content')).toBeInTheDocument()
  })

  test('рендерит Card с базовыми стилями', () => {
    const { container } = render(<Card>Content</Card>)
    expect(container.firstChild).toHaveClass('bg-white')
    expect(container.firstChild).toHaveClass('rounded-xl')
    expect(container.firstChild).toHaveClass('border-gray-200')
  })

  test('рендерит Card с hover эффектом', () => {
    const { container } = render(<Card hover>Hoverable</Card>)
    expect(container.firstChild).toHaveClass('hover:shadow-lg')
    expect(container.firstChild).toHaveClass('cursor-pointer')
  })

  test('рендерит Card с padding none', () => {
    const { container } = render(<Card padding="none">No padding</Card>)
    expect(container.firstChild).not.toHaveClass('p-4')
    expect(container.firstChild).not.toHaveClass('p-6')
    expect(container.firstChild).not.toHaveClass('p-8')
  })

  test('рендерит Card с padding sm', () => {
    const { container } = render(<Card padding="sm">Small padding</Card>)
    expect(container.firstChild).toHaveClass('p-4')
  })

  test('рендерит Card с padding md', () => {
    const { container } = render(<Card padding="md">Medium padding</Card>)
    expect(container.firstChild).toHaveClass('p-6')
  })

  test('рендерит Card с padding lg', () => {
    const { container } = render(<Card padding="lg">Large padding</Card>)
    expect(container.firstChild).toHaveClass('p-8')
  })

  test('рендерит Card с кастомным className', () => {
    const { container } = render(<Card className="custom-class">Custom</Card>)
    expect(container.firstChild).toHaveClass('custom-class')
  })

  test('передаёт дополнительные HTML props', () => {
    render(<Card data-testid="custom-card" role="article">Test</Card>)
    expect(screen.getByTestId('custom-card')).toBeInTheDocument()
    expect(screen.getByRole('article')).toBeInTheDocument()
  })

  test('рендерит Card с несколькими детьми', () => {
    render(
      <Card>
        <h2>Title</h2>
        <p>Paragraph</p>
        <button>Action</button>
      </Card>
    )
    expect(screen.getByText('Title')).toBeInTheDocument()
    expect(screen.getByText('Paragraph')).toBeInTheDocument()
    expect(screen.getByText('Action')).toBeInTheDocument()
  })

  test('рендерит вложенные компоненты', () => {
    const NestedComponent = () => <span>Nested</span>
    render(
      <Card>
        <NestedComponent />
      </Card>
    )
    expect(screen.getByText('Nested')).toBeInTheDocument()
  })
})
