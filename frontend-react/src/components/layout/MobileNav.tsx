/**
 * MobileNav Component
 * Navegação mobile com drawer/hamburger menu
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Menu, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  MessageSquare,
  BarChart3,
  FileText,
  Shield,
  LogOut,
} from 'lucide-react';
import { useAuthStore } from '@/store/auth.store';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
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
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Chat BI', href: '/chat', icon: MessageSquare, permission: Permission.USE_CHAT },
  { name: 'Análises', href: '/analytics', icon: BarChart3, permission: Permission.VIEW_ANALYTICS },
  { name: 'Relatórios', href: '/reports', icon: FileText, permission: Permission.VIEW_REPORTS },
  { name: 'Admin', href: '/admin', icon: Shield, permission: Permission.VIEW_ADMIN },
];

export function MobileNav() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  
  const userRole = (user?.role as Role) || Role.VIEWER;
  const roleLabel = roleLabels[userRole];

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-5 w-5" />
        </Button>
      </SheetTrigger>
      
      <SheetContent side="left" className="w-64 p-0">
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex h-16 items-center justify-between px-6 border-b">
            <h1 className="text-xl font-bold">Agent BI</h1>
            <Button variant="ghost" size="icon" onClick={() => setOpen(false)}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* User info */}
          <div className="px-6 py-4 border-b">
            <div className="flex items-center gap-3">
              <Avatar>
                <AvatarFallback className="bg-primary text-primary-foreground">
                  {user?.username?.charAt(0).toUpperCase() || 'U'}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 overflow-hidden">
                <p className="truncate text-sm font-medium">{user?.username}</p>
                <p className="truncate text-xs text-muted-foreground">{user?.email}</p>
              </div>
            </div>
            <div className="mt-2">
              <Badge variant={userRole === Role.ADMIN ? 'default' : 'secondary'} className="text-xs">
                {roleLabel}
              </Badge>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-3 py-4">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              
              const NavLink = (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setOpen(false)}
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

              if (item.permission) {
                return (
                  <PermissionGate key={item.name} permission={item.permission}>
                    {NavLink}
                  </PermissionGate>
                );
              }

              return NavLink;
            })}
          </nav>

          {/* Logout */}
          <div className="p-4 border-t">
            <Button
              variant="ghost"
              className="w-full justify-start"
              onClick={() => {
                logout();
                setOpen(false);
              }}
            >
              <LogOut className="mr-3 h-5 w-5" />
              Sair
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
