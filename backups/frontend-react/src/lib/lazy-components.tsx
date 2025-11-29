/**
 * Lazy Loading Configuration
 * Dynamic imports para rotas pesadas
 */

import dynamic from 'next/dynamic';
import { Loader2 } from 'lucide-react';

// Loading fallback component
const LoadingFallback = () => {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
    </div>
  );
};

// Lazy load heavy components
export const ChartBuilder = dynamic(
  () => import('@/components/analytics/ChartBuilder').then(mod => ({ default: mod.ChartBuilder })),
  {
    loading: LoadingFallback,
    ssr: false, // Disable SSR for chart components
  }
);

export const ReportEditor = dynamic(
  () => import('@/components/reports/ReportEditor').then(mod => ({ default: mod.ReportEditor })),
  {
    loading: LoadingFallback,
    ssr: false, // TipTap needs client-side only
  }
);

export const UserTable = dynamic(
  () => import('@/components/admin/UserTable').then(mod => ({ default: mod.UserTable })),
  {
    loading: LoadingFallback,
  }
);

export const AuditLogTable = dynamic(
  () => import('@/components/admin/AuditLogTable').then(mod => ({ default: mod.AuditLogTable })),
  {
    loading: LoadingFallback,
  }
);
