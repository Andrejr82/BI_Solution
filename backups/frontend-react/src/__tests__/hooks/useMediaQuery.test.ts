/**
 * useMediaQuery Hook Tests
 */

import { renderHook } from '@testing-library/react';
import { useMediaQuery, useIsMobile } from '@/hooks/useMediaQuery';

describe('useMediaQuery', () => {
  it('returns false for non-matching query', () => {
    const { result } = renderHook(() => useMediaQuery('(min-width: 1200px)'));
    expect(result.current).toBe(false);
  });

  it('useIsMobile returns correct value', () => {
    const { result } = renderHook(() => useIsMobile());
    // Default mock returns false
    expect(result.current).toBe(false);
  });
});
