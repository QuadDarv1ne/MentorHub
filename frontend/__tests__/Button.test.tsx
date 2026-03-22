/**
 * Компонентные тесты для UI компонентов
 */

import { render, screen, fireEvent } from '@testing-library/react'
import Button from '@/components/ui/Button'

describe('Button Component', () => {
  test('рендерит кнопку с текстом', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  test('рендерит кнопку с variant primary', () => {
    const { container } = render(<Button variant="primary">Primary</Button>)
    expect(container.firstChild).toHaveClass('bg-indigo-600')
  })

  test('рендерит кнопку с variant secondary', () => {
    const { container } = render(<Button variant="secondary">Secondary</Button>)
    expect(container.firstChild).toHaveClass('bg-gray-600')
  })

  test('рендерит кнопку с variant outline', () => {
    const { container } = render(<Button variant="outline">Outline</Button>)
    expect(container.firstChild).toHaveClass('border-indigo-600')
  })

  test('рендерит кнопку с variant danger', () => {
    const { container } = render(<Button variant="danger">Danger</Button>)
    expect(container.firstChild).toHaveClass('bg-red-600')
  })

  test('рендерит кнопку с variant ghost', () => {
    const { container } = render(<Button variant="ghost">Ghost</Button>)
    expect(container.firstChild).toHaveClass('text-gray-700')
  })

  test('рендерит кнопку с размером sm', () => {
    const { container } = render(<Button size="sm">Small</Button>)
    expect(container.firstChild).toHaveClass('text-sm')
  })

  test('рендерит кнопку с размером md', () => {
    const { container } = render(<Button size="md">Medium</Button>)
    expect(container.firstChild).toHaveClass('text-base')
  })

  test('рендерит кнопку с размером lg', () => {
    const { container } = render(<Button size="lg">Large</Button>)
    expect(container.firstChild).toHaveClass('text-lg')
  })

  test('рендерит кнопку на полную ширину', () => {
    const { container } = render(<Button fullWidth>Full Width</Button>)
    expect(container.firstChild).toHaveClass('w-full')
  })

  test('рендерит кнопку в состоянии loading', () => {
    render(<Button loading>Loading</Button>)
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
    expect(screen.getByText('Loading')).toBeInTheDocument()
  })

  test('вызывает onClick при клике', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click</Button>)
    fireEvent.click(screen.getByText('Click'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  test('не вызывает onClick при disabled', () => {
    const handleClick = jest.fn()
    render(<Button disabled onClick={handleClick}>Disabled</Button>)
    fireEvent.click(screen.getByText('Disabled'))
    expect(handleClick).not.toHaveBeenCalled()
  })

  test('не вызывает onClick при loading', () => {
    const handleClick = jest.fn()
    render(<Button loading onClick={handleClick}>Loading</Button>)
    fireEvent.click(screen.getByText('Loading'))
    expect(handleClick).not.toHaveBeenCalled()
  })

  test('передаёт дополнительные props', () => {
    render(<Button data-testid="custom-button" aria-label="Custom">Test</Button>)
    expect(screen.getByTestId('custom-button')).toBeInTheDocument()
    expect(screen.getByLabelText('Custom')).toBeInTheDocument()
  })

  test('использует forwardRef', () => {
    const ref = jest.fn()
    render(<Button ref={ref}>Test</Button>)
    expect(ref).toHaveBeenCalledWith(expect.any(HTMLButtonElement), expect.anything())
  })
})
