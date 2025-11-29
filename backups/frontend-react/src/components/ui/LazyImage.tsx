/**
 * LazyImage Component
 * Componente otimizado para carregamento de imagens
 */

import Image, { ImageProps } from 'next/image';
import { useState } from 'react';
import { cn } from '@/lib/utils';

interface LazyImageProps extends Omit<ImageProps, 'onLoad'> {
  fallbackSrc?: string;
}

export function LazyImage({ 
  src, 
  alt, 
  className,
  fallbackSrc = '/placeholder.png',
  ...props 
}: LazyImageProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);

  return (
    <div className={cn('relative overflow-hidden', className)}>
      <Image
        src={error ? fallbackSrc : src}
        alt={alt}
        className={cn(
          'transition-opacity duration-300',
          isLoading ? 'opacity-0' : 'opacity-100'
        )}
        onLoad={() => setIsLoading(false)}
        onError={() => {
          setError(true);
          setIsLoading(false);
        }}
        {...props}
      />
      {isLoading && (
        <div className="absolute inset-0 bg-muted animate-pulse" />
      )}
    </div>
  );
}
