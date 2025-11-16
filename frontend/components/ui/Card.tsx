import { HTMLAttributes, ReactNode } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  hover?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

export default function Card({ 
  children, 
  hover = false, 
  padding = 'md', 
  className = '', 
  ...props 
}: CardProps) {
  const baseStyles = 'bg-white rounded-xl border border-gray-200 transition-shadow'
  const hoverStyles = hover ? 'hover:shadow-lg cursor-pointer' : ''
  
  const paddingStyles = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  }
  
  return (
    <div 
      className={`${baseStyles} ${hoverStyles} ${paddingStyles[padding]} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}
