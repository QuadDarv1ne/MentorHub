"use client";
import React from 'react';
import Image from 'next/image';
import { getInitials, getAvatarColor } from '@/lib/utils';

interface AvatarProps {
  name: string;
  imageUrl?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const sizeClasses = {
  sm: 'h-8 w-8 text-sm',
  md: 'h-12 w-12 text-base',
  lg: 'h-16 w-16 text-xl',
  xl: 'h-24 w-24 text-3xl',
};

const sizeDimensions = {
  sm: 32,
  md: 48,
  lg: 64,
  xl: 96,
};

export default function Avatar({ name, imageUrl, size = 'md', className = '' }: AvatarProps) {
  const initials = getInitials(name);
  const colorClass = getAvatarColor(name);
  const dimension = sizeDimensions[size];

  if (imageUrl) {
    return (
      <div className={`${sizeClasses[size]} rounded-full overflow-hidden ${className}`} style={{ position: 'relative' }}>
        <Image
          src={imageUrl}
          alt={name}
          width={dimension}
          height={dimension}
          className="rounded-full object-cover"
          loading="lazy"
          quality={75}
        />
      </div>
    );
  }

  return (
    <div
      className={`${sizeClasses[size]} ${colorClass} rounded-full flex items-center justify-center text-white font-semibold ${className}`}
    >
      {initials}
    </div>
  );
}
