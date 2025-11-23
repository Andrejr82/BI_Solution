/**
 * Types para o módulo Administrativo
 */

import { Role } from '@/lib/permissions';

export interface AdminStats {
  activeUsers: number;
  reportsGenerated: number;
  queriesToday: number;
  systemHealth: number; // 0-100
  storageUsed: number; // bytes
  activeSessions: number;
}

export interface User {
  id: string;
  username: string;
  email: string;
  role: Role;
  isActive: boolean;
  lastLogin?: string;
  createdAt: string;
  avatar?: string;
  department?: string;
}

export interface CreateUserDTO {
  username: string;
  email: string;
  password?: string; // Opcional se usar convite
  role: Role;
  department?: string;
}

export interface UpdateUserDTO {
  username?: string;
  email?: string;
  role?: Role;
  isActive?: boolean;
  department?: string;
  password?: string;
}

export interface AuditLog {
  id: string;
  userId: string;
  userName: string;
  action: string;
  resource: string;
  details?: string;
  ipAddress: string;
  timestamp: string;
  status: 'success' | 'failure';
}

export interface SystemSettings {
  siteName: string;
  maintenanceMode: boolean;
  allowRegistration: boolean;
  defaultRole: Role;
  sessionTimeout: number; // minutos
  emailSettings: {
    smtpHost?: string;
    smtpPort?: number;
    senderEmail?: string;
  };
}
