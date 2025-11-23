/**
 * Definições de Roles e Permissões do Sistema
 * Sistema RBAC (Role-Based Access Control)
 */

export enum Role {
  ADMIN = 'admin',
  USER = 'user',
  VIEWER = 'viewer',
}

export enum Permission {
  // Analytics
  VIEW_ANALYTICS = 'view_analytics',
  EXPORT_DATA = 'export_data',
  
  // Reports
  VIEW_REPORTS = 'view_reports',
  CREATE_REPORTS = 'create_reports',
  EDIT_REPORTS = 'edit_reports',
  DELETE_REPORTS = 'delete_reports',
  SCHEDULE_REPORTS = 'schedule_reports',
  
  // Admin
  VIEW_ADMIN = 'view_admin',
  MANAGE_USERS = 'manage_users',
  VIEW_AUDIT_LOGS = 'view_audit_logs',
  MANAGE_SETTINGS = 'manage_settings',
  
  // Chat
  USE_CHAT = 'use_chat',
  VIEW_CHAT_HISTORY = 'view_chat_history',
}

/**
 * Mapeamento de roles para permissões
 * Define quais permissões cada role possui
 */
export const rolePermissions: Record<Role, Permission[]> = {
  [Role.ADMIN]: Object.values(Permission), // Admin tem todas as permissões
  
  [Role.USER]: [
    // Analytics
    Permission.VIEW_ANALYTICS,
    Permission.EXPORT_DATA,
    
    // Reports
    Permission.VIEW_REPORTS,
    Permission.CREATE_REPORTS,
    Permission.EDIT_REPORTS,
    Permission.SCHEDULE_REPORTS,
    
    // Chat
    Permission.USE_CHAT,
    Permission.VIEW_CHAT_HISTORY,
  ],
  
  [Role.VIEWER]: [
    // Analytics (apenas visualização)
    Permission.VIEW_ANALYTICS,
    
    // Reports (apenas visualização)
    Permission.VIEW_REPORTS,
    
    // Chat (apenas uso básico)
    Permission.USE_CHAT,
  ],
};

/**
 * Labels amigáveis para roles
 */
export const roleLabels: Record<Role, string> = {
  [Role.ADMIN]: 'Administrador',
  [Role.USER]: 'Usuário',
  [Role.VIEWER]: 'Visualizador',
};

/**
 * Labels amigáveis para permissões
 */
export const permissionLabels: Record<Permission, string> = {
  [Permission.VIEW_ANALYTICS]: 'Visualizar Análises',
  [Permission.EXPORT_DATA]: 'Exportar Dados',
  [Permission.VIEW_REPORTS]: 'Visualizar Relatórios',
  [Permission.CREATE_REPORTS]: 'Criar Relatórios',
  [Permission.EDIT_REPORTS]: 'Editar Relatórios',
  [Permission.DELETE_REPORTS]: 'Excluir Relatórios',
  [Permission.SCHEDULE_REPORTS]: 'Agendar Relatórios',
  [Permission.VIEW_ADMIN]: 'Acessar Administração',
  [Permission.MANAGE_USERS]: 'Gerenciar Usuários',
  [Permission.VIEW_AUDIT_LOGS]: 'Visualizar Logs de Auditoria',
  [Permission.MANAGE_SETTINGS]: 'Gerenciar Configurações',
  [Permission.USE_CHAT]: 'Usar Chat BI',
  [Permission.VIEW_CHAT_HISTORY]: 'Visualizar Histórico do Chat',
};
