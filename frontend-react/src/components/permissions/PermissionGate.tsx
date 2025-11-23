/**
 * PermissionGate Component
 * Renderiza children apenas se o usuário tiver as permissões necessárias
 */

'use client';

import { Permission } from '@/lib/permissions/permissions';
import { usePermissions } from '@/lib/permissions/rbac';

interface PermissionGateProps {
  /**
   * Permissão ou array de permissões necessárias
   * Se for array, usuário precisa ter pelo menos uma
   */
  permission: Permission | Permission[];
  
  /**
   * Conteúdo a ser renderizado se não tiver permissão
   */
  fallback?: React.ReactNode;
  
  /**
   * Conteúdo a ser renderizado se tiver permissão
   */
  children: React.ReactNode;
  
  /**
   * Se true, requer todas as permissões do array
   * Se false (padrão), requer apenas uma
   */
  requireAll?: boolean;
}

/**
 * Componente para renderização condicional baseada em permissões
 * 
 * @example
 * ```tsx
 * <PermissionGate permission={Permission.EXPORT_DATA}>
 *   <ExportButton />
 * </PermissionGate>
 * ```
 * 
 * @example Com fallback
 * ```tsx
 * <PermissionGate 
 *   permission={Permission.MANAGE_USERS}
 *   fallback={<p>Você não tem permissão para ver isto</p>}
 * >
 *   <UserManagement />
 * </PermissionGate>
 * ```
 * 
 * @example Com múltiplas permissões
 * ```tsx
 * <PermissionGate 
 *   permission={[Permission.VIEW_REPORTS, Permission.VIEW_ANALYTICS]}
 * >
 *   <ReportsSection />
 * </PermissionGate>
 * ```
 */
export function PermissionGate({
  permission,
  fallback = null,
  children,
  requireAll = false,
}: PermissionGateProps) {
  const { hasPermission, hasAnyPermission, hasAllPermissions } = usePermissions();

  let hasAccess = false;

  if (Array.isArray(permission)) {
    hasAccess = requireAll
      ? hasAllPermissions(permission)
      : hasAnyPermission(permission);
  } else {
    hasAccess = hasPermission(permission);
  }

  return hasAccess ? <>{children}</> : <>{fallback}</>;
}
