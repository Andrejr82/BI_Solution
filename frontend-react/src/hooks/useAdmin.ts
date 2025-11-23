/**
 * useAdmin Hook
 * Hook para gerenciar operações administrativas
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminService } from '@/services/admin.service';
import { useToast } from '@/hooks/use-toast';
import type { CreateUserDTO, UpdateUserDTO, SystemSettings } from '@/types/admin';

export function useAdmin() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Queries
  const statsQuery = useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: adminService.getStats,
  });

  const usersQuery = useQuery({
    queryKey: ['admin', 'users'],
    queryFn: adminService.getUsers,
  });

  const auditLogsQuery = useQuery({
    queryKey: ['admin', 'audit'],
    queryFn: () => adminService.getAuditLogs(),
  });

  const settingsQuery = useQuery({
    queryKey: ['admin', 'settings'],
    queryFn: adminService.getSettings,
  });

  // Mutations
  const createUserMutation = useMutation({
    mutationFn: adminService.createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
      toast({ title: 'Usuário criado com sucesso!' });
    },
    onError: () => {
      toast({ 
        title: 'Erro ao criar usuário', 
        variant: 'destructive' 
      });
    }
  });

  const updateUserMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateUserDTO }) => 
      adminService.updateUser(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
      toast({ title: 'Usuário atualizado com sucesso!' });
    },
    onError: () => {
      toast({ 
        title: 'Erro ao atualizar usuário', 
        variant: 'destructive' 
      });
    }
  });

  const deleteUserMutation = useMutation({
    mutationFn: adminService.deleteUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
      toast({ title: 'Usuário removido' });
    },
  });

  const updateSettingsMutation = useMutation({
    mutationFn: adminService.updateSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'settings'] });
      toast({ title: 'Configurações salvas com sucesso!' });
    },
  });

  return {
    stats: statsQuery.data,
    users: usersQuery.data,
    auditLogs: auditLogsQuery.data,
    settings: settingsQuery.data,
    isLoadingStats: statsQuery.isLoading,
    isLoadingUsers: usersQuery.isLoading,
    createUser: createUserMutation.mutate,
    updateUser: updateUserMutation.mutate,
    deleteUser: deleteUserMutation.mutate,
    updateSettings: updateSettingsMutation.mutate,
    isCreatingUser: createUserMutation.isPending,
    isUpdatingUser: updateUserMutation.isPending,
    isSavingSettings: updateSettingsMutation.isPending,
  };
}
