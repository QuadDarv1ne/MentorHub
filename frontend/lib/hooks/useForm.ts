/**
 * Универсальный хук для управления формами с валидацией
 * Поддерживает реальное время валидации, async проверки, удобное управление состоянием
 */

import { useState, useCallback } from 'react'

type ValidationRule<T> = {
  validator: (value: T, formData: Record<string, unknown>) => boolean | Promise<boolean>
  message: string
}

type FieldConfig<T = unknown> = {
  initialValue: T
  rules?: ValidationRule<T>[]
  validateOn?: 'change' | 'blur' | 'submit'
  transform?: (value: T) => T
}

type FormConfig<T extends Record<string, unknown>> = {
  [K in keyof T]: FieldConfig<T[K]>
}

type FormErrors<T> = Partial<Record<keyof T, string>>
type TouchedFields<T> = Partial<Record<keyof T, boolean>>

export function useForm<T extends Record<string, unknown>>(
  config: FormConfig<T>,
  onSubmit?: (data: T) => void | Promise<void>
) {
  const [values, setValues] = useState<T>(() => {
    const initial = {} as T
    Object.keys(config).forEach((key) => {
      initial[key as keyof T] = config[key as keyof T].initialValue
    })
    return initial
  })

  const [errors, setErrors] = useState<FormErrors<T>>({})
  const [touched, setTouched] = useState<TouchedFields<T>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isValidating, setIsValidating] = useState(false)
  const [submitCount, setSubmitCount] = useState(0)

  // Валидация одного поля
  const validateField = useCallback(
    async (name: keyof T, value: unknown): Promise<string | null> => {
      const fieldConfig = config[name]
      if (!fieldConfig?.rules) return null

      for (const rule of fieldConfig.rules) {
        const isValid = await rule.validator(value as T[keyof T], values)
        if (!isValid) {
          return rule.message
        }
      }

      return null
    },
    [config, values]
  )

  // Валидация всей формы
  const validateForm = useCallback(async (): Promise<boolean> => {
    setIsValidating(true)
    const newErrors: FormErrors<T> = {}

    await Promise.all(
      Object.keys(config).map(async (key) => {
        const fieldKey = key as keyof T
        const error = await validateField(fieldKey, values[fieldKey])
        if (error) {
          newErrors[fieldKey] = error
        }
      })
    )

    setErrors(newErrors)
    setIsValidating(false)
    return Object.keys(newErrors).length === 0
  }, [config, values, validateField])

  // Установка значения поля
  const setValue = useCallback(
    async (name: keyof T, value: unknown) => {
      const fieldConfig = config[name]
      const transformedValue = fieldConfig.transform ? fieldConfig.transform(value as T[keyof T]) : value

      setValues((prev) => ({ ...prev, [name]: transformedValue }))

      // Валидация на изменение если настроена
      if (fieldConfig.validateOn === 'change' || (touched[name] && submitCount > 0)) {
        const error = await validateField(name, transformedValue)
        setErrors((prev) => ({
          ...prev,
          [name]: error || undefined,
        }))
      }
    },
    [config, touched, submitCount, validateField]
  )

  // Обработка blur
  const handleBlur = useCallback(
    async (name: keyof T) => {
      setTouched((prev) => ({ ...prev, [name]: true }))

      const fieldConfig = config[name]
      if (fieldConfig.validateOn === 'blur' || fieldConfig.validateOn === 'change') {
        const error = await validateField(name, values[name])
        setErrors((prev) => ({
          ...prev,
          [name]: error || undefined,
        }))
      }
    },
    [config, values, validateField]
  )

  // Обработка change
  const handleChange = useCallback(
    (name: keyof T) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      setValue(name, e.target.value)
    },
    [setValue]
  )

  // Сброс формы
  const reset = useCallback(() => {
    const initial = {} as T
    Object.keys(config).forEach((key) => {
      initial[key as keyof T] = config[key as keyof T].initialValue
    })
    setValues(initial)
    setErrors({})
    setTouched({})
    setSubmitCount(0)
  }, [config])

  // Обработка submit
  const handleSubmit = useCallback(
    async (e?: React.FormEvent) => {
      e?.preventDefault()
      setSubmitCount((prev) => prev + 1)

      const isValid = await validateForm()

      if (!isValid) {
        // Пометить все поля как touched для отображения ошибок
        const allTouched = Object.keys(config).reduce((acc, key) => {
          acc[key as keyof T] = true
          return acc
        }, {} as TouchedFields<T>)
        setTouched(allTouched)
        return
      }

      if (onSubmit) {
        setIsSubmitting(true)
        try {
          await onSubmit(values)
        } catch (error) {
          console.error('Form submission error:', error)
        } finally {
          setIsSubmitting(false)
        }
      }
    },
    [config, values, validateForm, onSubmit]
  )

  // Установка ошибки поля вручную
  const setFieldError = useCallback((name: keyof T, error: string) => {
    setErrors((prev) => ({ ...prev, [name]: error }))
  }, [])

  // Установка нескольких значений
  const setFieldsValue = useCallback((fields: Partial<T>) => {
    setValues((prev) => ({ ...prev, ...fields }))
  }, [])

  // Получение props для поля (удобно для инпутов)
  const getFieldProps = useCallback(
    (name: keyof T) => ({
      name: String(name),
      value: values[name],
      onChange: handleChange(name),
      onBlur: () => handleBlur(name),
      error: touched[name] ? errors[name] : undefined,
    }),
    [values, errors, touched, handleChange, handleBlur]
  )

  // Проверка, валидна ли форма
  const isValid = Object.keys(errors).length === 0

  return {
    values,
    errors,
    touched,
    isSubmitting,
    isValidating,
    isValid,
    submitCount,
    setValue,
    setFieldError,
    setFieldsValue,
    handleChange,
    handleBlur,
    handleSubmit,
    reset,
    validateForm,
    validateField,
    getFieldProps,
  }
}

// Предопределённые валидаторы для удобства

export const validators = {
  required: (message = 'Это поле обязательно'): ValidationRule<unknown> => ({
    validator: (value) => {
      if (typeof value === 'string') return value.trim().length > 0
      if (Array.isArray(value)) return value.length > 0
      return value !== null && value !== undefined
    },
    message,
  }),

  email: (message = 'Введите корректный email'): ValidationRule<string> => ({
    validator: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
    message,
  }),

  minLength: (min: number, message?: string): ValidationRule<string> => ({
    validator: (value) => value.length >= min,
    message: message || `Минимальная длина ${min} символов`,
  }),

  maxLength: (max: number, message?: string): ValidationRule<string> => ({
    validator: (value) => value.length <= max,
    message: message || `Максимальная длина ${max} символов`,
  }),

  pattern: (regex: RegExp, message: string): ValidationRule<string> => ({
    validator: (value) => regex.test(value),
    message,
  }),

  min: (min: number, message?: string): ValidationRule<number> => ({
    validator: (value) => value >= min,
    message: message || `Минимальное значение ${min}`,
  }),

  max: (max: number, message?: string): ValidationRule<number> => ({
    validator: (value) => value <= max,
    message: message || `Максимальное значение ${max}`,
  }),

  match: (fieldName: string, message?: string): ValidationRule<unknown> => ({
    validator: (value, formData) => value === formData[fieldName],
    message: message || 'Значения не совпадают',
  }),

  url: (message = 'Введите корректный URL'): ValidationRule<string> => ({
    validator: (value) => {
      try {
        new URL(value)
        return true
      } catch {
        return false
      }
    },
    message,
  }),

  phone: (message = 'Введите корректный номер телефона'): ValidationRule<string> => ({
    validator: (value) => /^[\d\s\-\+\(\)]+$/.test(value) && value.replace(/\D/g, '').length >= 10,
    message,
  }),

  async: (
    asyncValidator: (value: unknown) => Promise<boolean>,
    message: string
  ): ValidationRule<unknown> => ({
    validator: asyncValidator,
    message,
  }),
}
