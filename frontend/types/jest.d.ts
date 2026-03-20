/**
 * Jest Testing Library types augmentation
 */

import '@testing-library/jest-dom'

// Add missing matchers types
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeInTheDocument(): R
      toHaveAttribute(attr: string, value?: string | RegExp): R
      toHaveClass(...classNames: string[]): R
      toHaveTextContent(text: string | RegExp): R
      toBeDisabled(): R
      toBeEnabled(): R
      toBeEmpty(): R
      toBeInvalid(): R
      toBeRequired(): R
      toBeValid(): R
      toHaveFocus(): R
      toHaveValue(value?: string | string[] | number): R
    }
  }
}

// Export empty to make it a module
export {}
