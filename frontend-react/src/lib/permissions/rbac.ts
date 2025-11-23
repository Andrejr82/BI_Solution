/**
 * Sistema RBAC (Role-Based Access Control)
 * Gerencia permissões e controle de acesso baseado em roles
 */

import { Role, Permission, rolePermissions } from './permissions';
import { useAuthStore } from '@/store/auth.store';

/**
 * Classe principal do sistema RBAC
 */
export class RBAC {
  /**
   * Verifica se um role tem uma permissão específica
   */
  static hasPermission(userRole: Role, permission: Permission): boolean {
    const permissions = rolePermissions[userRole];
    return permissions.includes(permission);
  }

  /**
   * Verifica se um role tem pelo menos uma das permissões fornecidas
   */
  static hasAnyPermission(userRole: Role, permissions: Permission[]): boolean {
    return permissions.some(p => this.hasPermission(userRole, p));
  }

  /**
   * Verifica se um role tem todas as permissões fornecidas
   */
  static hasAllPermissions(userRole: Role, permissions: Permission[]): boolean {
    return permissions.every(p => this.hasPermission(userRole, p));
  }

  /**
   * Verifica se um role pode acessar uma rota específica
   */
  static canAccessRoute(userRole: Role, route: string): boolean {
    const routePermissions: Record<string, Permission[]> = {
      '/dashboard': [], // Rota pública (autenticada)
      '/chat': [Permission.USE_CHAT],
      '/analytics': [Permission.VIEW_ANALYTICS],
      '/reports': [Permission.VIEW_REPORTS],
      '/reports/new': [Permission.CREATE_REPORTS],
      '/admin': [Permission.VIEW_ADMIN],
      '/admin/users': [Permission.MANAGE_USERS],
      '/admin/audit': [Permission.VIEW_AUDIT_LOGS],
      '/admin/settings': [Permission.MANAGE_SETTINGS],
    };

    const required = routePermissions[route];
    if (!required || required.length === 0) return true; // Rota sem restrições

    return this.hasAnyPermission(userRole, required);
  }

  /**
   * Obtém todas as permissões de um role
   */
  static getPermissions(userRole: Role): Permission[] {
    return rolePermissions[userRole] || [];
  }

  /**
   * Verifica se um role é admin
   */
  static isAdmin(userRole: Role): boolean {
    return userRole === Role.ADMIN;
  }

  /**
   * Verifica se um role pode executar uma ação em um recurso
   */
  static canPerformAction(
    userRole: Role,
    action: 'create' | 'read' | 'update' | 'delete',
    resource: 'reports' | 'users' | 'analytics'
  ): boolean {
    const actionPermissionMap: Record<
      string,
      Record<string, Permission | null>
    > = {
      reports: {
        create: Permission.CREATE_REPORTS,
        read: Permission.VIEW_REPORTS,
        update: Permission.EDIT_REPORTS,
        delete: Permission.DELETE_REPORTS,
      },
      users: {
        create: Permission.MANAGE_USERS,
        read: Permission.MANAGE_USERS,
        update: Permission.MANAGE_USERS,
        delete: Permission.MANAGE_USERS,
      },
      analytics: {
        create: null,
        read: Permission.VIEW_ANALYTICS,
        update: null,
        delete: null,
      },
    };

    const permission = actionPermissionMap[resource]?.[action];
    if (!permission) return false;

    return this.hasPermission(userRole, permission);
  }
}

/**
 * Hook para usar permissões no React
 * Fornece funções utilitárias para verificar permissões do usuário atual
 */
export function usePermissions() {
  const { user } = useAuthStore();
  const userRole = (user?.role as Role) || Role.VIEWER;

  return {
    /**
     * Verifica se o usuário tem uma permissão específica
     */
    hasPermission: (permission: Permission) =>
      RBAC.hasPermission(userRole, permission),

    /**
     * Verifica se o usuário tem pelo menos uma das permissões
     */
    hasAnyPermission: (permissions: Permission[]) =>
      RBAC.hasAnyPermission(userRole, permissions),

    /**
     * Verifica se o usuário tem todas as permissões
     */
    hasAllPermissions: (permissions: Permission[]) =>
      RBAC.hasAllPermissions(userRole, permissions),

    /**
     * Verifica se o usuário pode acessar uma rota
     */
    canAccessRoute: (route: string) => RBAC.canAccessRoute(userRole, route),

    /**
     * Verifica se o usuário pode executar uma ação em um recurso
     */
    canPerformAction: (
      action: 'create' | 'read' | 'update' | 'delete',
      resource: 'reports' | 'users' | 'analytics'
    ) => RBAC.canPerformAction(userRole, action, resource),

    /**
     * Obtém todas as permissões do usuário
     */
    permissions: RBAC.getPermissions(userRole),

    /**
     * Role atual do usuário
     */
    role: userRole,

    /**
     * Verifica se o usuário é admin
     */
    isAdmin: RBAC.isAdmin(userRole),
  };
}
