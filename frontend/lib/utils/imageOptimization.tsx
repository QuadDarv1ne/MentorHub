/**
 * Image Optimization Utilities для Next.js
 * Помощники для оптимизации изображений и lazy loading
 */

import Image from 'next/image'
import { useState } from 'react'

interface OptimizedImageProps {
  src: string
  alt: string
  width?: number
  height?: number
  className?: string
  priority?: boolean
  sizes?: string
  objectFit?: 'cover' | 'contain' | 'fill' | 'scale-down'
  placeholder?: 'blur' | 'empty'
  blurDataURL?: string
  onLoad?: () => void
}

/**
 * Оптимизированный компонент Image с поддержкой blur placeholder
 * 
 * Пример использования:
 * ```tsx
 * <OptimizedImage
 *   src="/course-image.jpg"
 *   alt="Course"
 *   width={400}
 *   height={300}
 *   priority={false}
 * />
 * ```
 */
export function OptimizedImage({
  src,
  alt,
  width = 400,
  height = 300,
  className = '',
  priority = false,
  sizes,
  objectFit = 'cover',
  placeholder = 'blur',
  blurDataURL,
  onLoad,
}: OptimizedImageProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(false)

  // Генерируем blur data URL если не предоставлен
  const defaultBlurDataURL =
    blurDataURL ||
    'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZTBmMmZlIi8+PC9zdmc+'

  const handleLoad = () => {
    setIsLoading(false)
    onLoad?.()
  }

  const handleError = () => {
    setError(true)
    setIsLoading(false)
  }

  if (error) {
    return (
      <div
        className={`flex items-center justify-center bg-gray-200 text-gray-500 ${className}`}
        style={{ width, height }}
      >
        Ошибка загрузки изображения
      </div>
    )
  }

  return (
    <div className={`relative overflow-hidden ${className}`} style={{ width, height }}>
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        priority={priority}
        sizes={sizes}
        placeholder={placeholder}
        blurDataURL={defaultBlurDataURL}
        onLoad={handleLoad}
        onError={handleError}
        className={`transition-opacity duration-300 ${isLoading ? 'opacity-0' : 'opacity-100'}`}
        style={{
          objectFit,
          objectPosition: 'center',
        }}
      />
      {isLoading && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}
    </div>
  )
}

/**
 * Галерея изображений с lazy loading
 */
export function LazyImageGallery({
  images,
  columns = 3,
  gap = 4,
}: {
  images: Array<{ src: string; alt: string; width?: number; height?: number }>
  columns?: number
  gap?: number
}) {
  return (
    <div
      className="grid"
      style={{
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
        gap: `${gap * 0.25}rem`,
      }}
    >
      {images.map((image, index) => (
        <OptimizedImage
          key={index}
          src={image.src}
          alt={image.alt}
          width={image.width || 300}
          height={image.height || 300}
          priority={index < 3} // Первые 3 изображения загружаем с приоритетом
          sizes={`(max-width: 768px) 100vw, (max-width: 1200px) 50vw, ${100 / columns}vw`}
        />
      ))}
    </div>
  )
}

/**
 * Responsive image с разными источниками для разных размеров экрана
 */
export function ResponsiveImage({
  mobileSrc,
  tabletSrc,
  desktopSrc,
  alt,
  className = '',
  priority = false,
}: {
  mobileSrc: string
  tabletSrc: string
  desktopSrc: string
  alt: string
  className?: string
  priority?: boolean
}) {
  return (
    <picture className={className}>
      {/* Mobile */}
      <source media="(max-width: 640px)" srcSet={mobileSrc} />
      {/* Tablet */}
      <source media="(max-width: 1024px)" srcSet={tabletSrc} />
      {/* Desktop */}
      <img
        src={desktopSrc}
        alt={alt}
        loading={priority ? 'eager' : 'lazy'}
        className="w-full h-auto"
      />
    </picture>
  )
}

/**
 * Image preloader - предзагрузка изображений перед отображением
 */
export function useImagePreloader() {
  const preloadImage = (src: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const img = new window.Image()
      img.onload = () => resolve()
      img.onerror = reject
      img.src = src
    })
  }

  const preloadImages = async (srcs: string[]): Promise<void> => {
    try {
      await Promise.all(srcs.map(preloadImage))
    } catch (error) {
      console.error('Failed to preload images:', error)
    }
  }

  return { preloadImage, preloadImages }
}

/**
 * Generate blur data URL для placeholder
 * Используется для создания маленьких размытых превью изображений
 */
export async function generateBlurDataURL(
  imagePath: string
): Promise<string> {
  try {
    // В production используйте сервис оптимизации изображений
    // Пример: https://vercel.com/docs/concepts/image-optimization/blur

    // Для локальной разработки возвращаем SVG placeholder
    const svgString = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><filter id="blur"><feGaussianBlur stdDeviation="20" /></filter><rect width="400" height="300" fill="#e0f2fe" filter="url(#blur)" /></svg>`
    const base64svg = btoa(svgString)

    return `data:image/svg+xml;base64,${base64svg}`
  } catch (error) {
    console.error('Error generating blur data URL:', error)
    return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZTBmMmZlIi8+PC9zdmc+'
  }
}

/**
 * Image optimization tips and constants
 */
export const IMAGE_OPTIMIZATION = {
  // Размеры для breakpoints
  SIZES: {
    mobile: 360,
    tablet: 768,
    desktop: 1200,
  },

  // Рекомендуемые соотношения сторон
  ASPECT_RATIOS: {
    thumbnail: '1/1',
    card: '4/3',
    banner: '16/9',
    hero: '2/1',
  },

  // Форматы и качество
  FORMATS: {
    webp: 'webp', // Для современных браузеров
    jpeg: 'jpeg', // Fallback
  },

  // Оптимальное качество для разных использований
  QUALITY: {
    thumbnail: 60,
    card: 75,
    banner: 80,
    hero: 85,
    fullscreen: 90,
  },
}

/**
 * Утилита для генерации srcset для responsive images
 */
export function generateSrcSet(
  basePath: string,
  sizes: number[] = [360, 768, 1200, 1920]
): string {
  return sizes
    .map((size) => `${basePath}?w=${size} ${size}w`)
    .join(', ')
}
