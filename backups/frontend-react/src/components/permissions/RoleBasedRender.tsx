/**
 * RoleBasedRender Component
 * Renderiza conteúdo diferente baseado no role do usuário
 */

'use client';

import { Role } from '@/lib/permissions/permissions';
import { usePermissions } from '@/lib/permissions/rbac';

interface RoleBasedRenderProps {
  /**
   * Role ou array de roles permitidos
   */
  allowedRoles: Role | Role[];
  
  /**
   * Conteúdo a ser renderizado se o role for permitido
   */
  children: React.ReactNode;
  
  /**
   * Conteúdo a ser renderizado se o role não for permitido
   */
  fallback?: React.ReactNode;
}

/**
 * Componente para renderização condicional baseada em roles
 * 
 * @example
 * ```tsx
 * <RoleBasedRender allowedRoles={Role.ADMIN}>
 *   <AdminPanel />
 * </RoleBasedRender>
 * ```
 * 
 * @example Com múltiplos roles
 * ```tsx
 * <RoleBasedRender allowedRoles={[Role.ADMIN, Role.USER]}>
 *   <AdvancedFeatures />
 * </RoleBasedRender>
 * ```
 * 
 * @example Com fallback
 * ```tsx
 * <RoleBasedRender 
 *   allowedRoles={Role.ADMIN}
 *   fallback={<BasicView />}
 * >
 *   <AdvancedView />
 * </RoleBasedRender>
 * ```
 */
export function RoleBasedRender({
  allowedRoles,
  children,
  fallback = null,
}: RoleBasedRenderProps) {
  const { role } = usePermissions();

  const isAllowed = Array.isArray(allowedRoles)
    ? allowedRoles.includes(role)
    : role === allowedRoles;

  return isAllowed ? <>{children}</> : <>{fallback}</>;
}

/**
 * Componente para renderizar conteúdo apenas para admins
 */
export function AdminOnly({ children }: { children: React.ReactNode }) {
  return (
    <RoleBasedRender allowedRoles={Role.ADMIN}>
      {children}
    </RoleBasedRender>
  );
}

/**
 * Componente para renderizar conteúdo para usuários e admins
 */
export function UserAndAdmin({ children }: { children: React.ReactNode }) {
  return (
    <RoleBasedRender allowedRoles={[Role.ADMIN, Role.USER]}>
      {children}
    </RoleBasedRender>
  );
}
