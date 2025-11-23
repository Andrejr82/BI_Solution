/**
 * Admin Dashboard Page
 * Página principal do painel administrativo
 */

'use client';

import { useAdmin } from '@/hooks/useAdmin';
import { AdminStatsCards } from '@/components/admin/AdminStatsCards';
import { UserTable } from '@/components/admin/UserTable';
import { AuditLogTable } from '@/components/admin/AuditLogTable';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Plus, Settings } from 'lucide-react';
import Link from 'next/link';
import { RoleBasedRender } from '@/components/permissions';
import { Role } from '@/lib/permissions';

export default function AdminDashboardPage() {
  const { 
    stats, 
    users, 
    auditLogs, 
    deleteUser, 
    isLoadingStats 
  } = useAdmin();

  // Mock de função de edição (será implementada com modal)
  const handleEditUser = (user: any) => {
    console.log('Edit user:', user);
  };

  return (
    <RoleBasedRender allowedRoles={Role.ADMIN} fallback={<div className="p-6">Acesso negado</div>}>
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">🛡️ Painel Administrativo</h1>
            <p className="text-muted-foreground mt-1">
              Gerencie usuários, configurações e monitore o sistema
            </p>
          </div>
          
          <div className="flex gap-2">
            <Link href="/admin/settings">
              <Button variant="outline">
                <Settings className="mr-2 h-4 w-4" />
                Configurações
              </Button>
            </Link>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Novo Usuário
            </Button>
          </div>
        </div>

        {/* Stats */}
        <AdminStatsCards stats={stats} />

        {/* Main Content */}
        <Tabs defaultValue="users" className="space-y-4">
          <TabsList>
            <TabsTrigger value="users">Usuários</TabsTrigger>
            <TabsTrigger value="audit">Auditoria</TabsTrigger>
          </TabsList>

          <TabsContent value="users" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Gestão de Usuários</CardTitle>
              </CardHeader>
              <CardContent>
                {users && (
                  <UserTable 
                    users={users} 
                    onEdit={handleEditUser}
                    onDelete={deleteUser}
                  />
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="audit" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Logs de Auditoria</CardTitle>
              </CardHeader>
              <CardContent>
                {auditLogs && <AuditLogTable logs={auditLogs} />}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </RoleBasedRender>
  );
}
