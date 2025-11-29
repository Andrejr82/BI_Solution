/**
 * useReports Hook
 * Hook para gerenciar estado e operações de relatórios
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { reportsService } from '@/services/reports.service';
import { useToast } from '@/hooks/use-toast';
import { useRouter } from 'next/navigation';
import type { CreateReportDTO, UpdateReportDTO } from '@/types/reports';

export function useReports() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const router = useRouter();

  // Queries
  const reportsQuery = useQuery({
    queryKey: ['reports'],
    queryFn: reportsService.getAll,
  });

  const templatesQuery = useQuery({
    queryKey: ['reports', 'templates'],
    queryFn: reportsService.getTemplates,
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: reportsService.create,
    onSuccess: (newReport) => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      toast({ title: 'Relatório criado com sucesso!' });
      router.push(`/reports/${newReport.id}/edit`);
    },
    onError: () => {
      toast({ 
        title: 'Erro ao criar relatório', 
        variant: 'destructive' 
      });
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateReportDTO }) => 
      reportsService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      toast({ title: 'Relatório salvo com sucesso!' });
    },
    onError: () => {
      toast({ 
        title: 'Erro ao salvar relatório', 
        variant: 'destructive' 
      });
    }
  });

  const deleteMutation = useMutation({
    mutationFn: reportsService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      toast({ title: 'Relatório removido' });
    },
  });

  const generatePDFMutation = useMutation({
    mutationFn: reportsService.generatePDF,
    onSuccess: (blob) => {
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
      toast({ title: 'PDF gerado com sucesso!' });
    },
  });

  return {
    reports: reportsQuery.data,
    templates: templatesQuery.data,
    isLoading: reportsQuery.isLoading,
    createReport: createMutation.mutate,
    updateReport: updateMutation.mutate,
    deleteReport: deleteMutation.mutate,
    generatePDF: generatePDFMutation.mutate,
    isCreating: createMutation.isPending,
    isSaving: updateMutation.isPending,
    isGenerating: generatePDFMutation.isPending,
  };
}

export function useReport(id: string) {
  return useQuery({
    queryKey: ['reports', id],
    queryFn: () => reportsService.getById(id),
    enabled: !!id,
  });
}
