'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  MessageSquare,
  BarChart3,
  FileText,
  Settings,
  Shield,
  LogOut,
} from 'lucide-react';
import { useAuthStore } from '@/store/auth.store';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { PermissionGate } from '@/components/permissions';
import { Permission, roleLabels, Role } from '@/lib/permissions';

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  permission?: Permission;
}

const navigation: NavigationItem[] = [
  { 
    name: 'Dashboard', 
    href: '/dashboard', 
    icon: LayoutDashboard 
  },
  { 
    name: 'Chat BI', 
    href: '/chat', 
    icon: MessageSquare,
    permission: Permission.USE_CHAT 
  },
  { 
    name: 'Análises', 
    href: '/analytics', 
    icon: BarChart3,
    permission: Permission.VIEW_ANALYTICS 
  },
  { 
    name: 'Relatórios', 
    href: '/reports', 
    icon: FileText,
    permission: Permission.VIEW_REPORTS 
  },
  { 
    name: 'Admin', 
    href: '/admin', 
    icon: Shield,
    permission: Permission.VIEW_ADMIN 
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  
  const userRole = (user?.role as Role) || Role.VIEWER;
  const roleLabel = roleLabels[userRole];

  return (
    <div className="flex h-screen w-64 flex-col border-r bg-card">
      {/* Header */}
      <div className="flex h-16 items-center px-6">
        <h1 className="text-xl font-bold">Agent BI</h1>
      </div>

      <Separator />

      {/* User info */}
      <div className="px-6 py-4">
        <div className="flex items-center gap-3">
          <Avatar>
            <AvatarFallback className="bg-primary text-primary-foreground">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 overflow-hidden">
            <p className="truncate text-sm font-medium">{user?.username}</p>
            <p className="truncate text-xs text-muted-foreground">
              {user?.email}
            </p>
          </div>
        </div>
        
        {/* Role Badge */}
        <div className="mt-2">
          <Badge 
            variant={userRole === Role.ADMIN ? 'default' : 'secondary'}
            className="text-xs"
          >
            {roleLabel}
          </Badge>
        </div>
      </div>

      <Separator />

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          
          const NavLink = (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          );

          // Se tem permissão requerida, envolve com PermissionGate
          if (item.permission) {
            return (
              <PermissionGate key={item.name} permission={item.permission}>
                {NavLink}
              </PermissionGate>
            );
          }

          // Senão, renderiza direto
          return NavLink;
        })}
      </nav>

      <Separator />

      {/* Logout */}
      <div className="p-4">
        <Button
          variant="ghost"
          className="w-full justify-start"
          onClick={logout}
        >
          <LogOut className="mr-3 h-5 w-5" />
          Sair
        </Button>
      </div>
    </div>
  );
}
