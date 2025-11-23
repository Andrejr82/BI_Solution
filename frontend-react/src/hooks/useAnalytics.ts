/**
 * useAnalytics Hook
 * Hook customizado para gerenciar estado e operações de analytics
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { analyticsService } from '@/services/analytics.service';
import type { AnalyticsFilter, ExportFormat } from '@/types/analytics';
import { useToast } from '@/hooks/use-toast';

export function useAnalytics(initialFilters?: AnalyticsFilter) {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Query para dados
  const dataQuery = useQuery({
    queryKey: ['analytics', 'data', initialFilters],
    queryFn: () => analyticsService.getData(initialFilters),
  });

  // Query para métricas
  const metricsQuery = useQuery({
    queryKey: ['analytics', 'metrics'],
    queryFn: analyticsService.getMetrics,
  });

  // Mutation para exportação
  const exportMutation = useMutation({
    mutationFn: ({ format, filters }: { format: ExportFormat; filters?: AnalyticsFilter }) =>
      analyticsService.exportData(format, filters),
    onSuccess: (blob, variables) => {
      // Criar download do arquivo
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics-export.${variables.format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast({
        title: 'Exportação concluída!',
        description: `Dados exportados em formato ${variables.format.toUpperCase()}`,
      });
    },
    onError: () => {
      toast({
        title: 'Erro na exportação',
        description: 'Não foi possível exportar os dados',
        variant: 'destructive',
      });
    },
  });

  return {
    data: dataQuery.data,
    metrics: metricsQuery.data,
    isLoading: dataQuery.isLoading || metricsQuery.isLoading,
    isError: dataQuery.isError || metricsQuery.isError,
    error: dataQuery.error || metricsQuery.error,
    refetch: () => {
      dataQuery.refetch();
      metricsQuery.refetch();
    },
    exportData: (format: ExportFormat, filters?: AnalyticsFilter) =>
      exportMutation.mutate({ format, filters }),
    isExporting: exportMutation.isPending,
  };
}
