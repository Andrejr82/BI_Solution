/**
 * ProtectedRoute Component
 * HOC para proteger rotas baseado em permissões
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Permission } from '@/lib/permissions/permissions';
import { usePermissions } from '@/lib/permissions/rbac';
import { useAuthStore } from '@/store/auth.store';

interface ProtectedRouteProps {
  /**
   * Permissão ou array de permissões necessárias
   */
  permission?: Permission | Permission[];
  
  /**
   * Se true, requer todas as permissões do array
   */
  requireAll?: boolean;
  
  /**
   * Rota para redirecionar se não tiver permissão
   */
  redirectTo?: string;
  
  /**
   * Conteúdo da rota protegida
   */
  children: React.ReactNode;
}

/**
 * Componente HOC para proteger rotas
 * Redireciona usuários sem permissão
 * 
 * @example
 * ```tsx
 * export default function AdminPage() {
 *   return (
 *     <ProtectedRoute permission={Permission.VIEW_ADMIN}>
 *       <AdminDashboard />
 *     </ProtectedRoute>
 *   );
 * }
 * ```
 */
export function ProtectedRoute({
  permission,
  requireAll = false,
  redirectTo = '/dashboard',
  children,
}: ProtectedRouteProps) {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const { hasPermission, hasAnyPermission, hasAllPermissions } = usePermissions();

  useEffect(() => {
    // Verificar autenticação
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    // Se não há permissão especificada, apenas verifica autenticação
    if (!permission) return;

    // Verificar permissões
    let hasAccess = false;

    if (Array.isArray(permission)) {
      hasAccess = requireAll
        ? hasAllPermissions(permission)
        : hasAnyPermission(permission);
    } else {
      hasAccess = hasPermission(permission);
    }

    // Redirecionar se não tiver acesso
    if (!hasAccess) {
      router.push(redirectTo);
    }
  }, [
    isAuthenticated,
    permission,
    requireAll,
    redirectTo,
    router,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
  ]);

  // Verificação inline para evitar flash de conteúdo
  if (!isAuthenticated) {
    return null;
  }

  if (permission) {
    let hasAccess = false;

    if (Array.isArray(permission)) {
      hasAccess = requireAll
        ? hasAllPermissions(permission)
        : hasAnyPermission(permission);
    } else {
      hasAccess = hasPermission(permission);
    }

    if (!hasAccess) {
      return null;
    }
  }

  return <>{children}</>;
}
