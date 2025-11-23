/**
 * AdminStatsCards Component
 * Cards de estatísticas do dashboard admin
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, FileText, Activity, Server, Database, Shield } from 'lucide-react';
import type { AdminStats } from '@/types/admin';

interface AdminStatsCardsProps {
  stats?: AdminStats;
}

export function AdminStatsCards({ stats }: AdminStatsCardsProps) {
  if (!stats) return null;

  const items = [
    {
      title: 'Usuários Ativos',
      value: stats.activeUsers,
      icon: Users,
      description: 'Total de usuários ativos',
    },
    {
      title: 'Relatórios Gerados',
      value: stats.reportsGenerated,
      icon: FileText,
      description: 'Total de relatórios criados',
    },
    {
      title: 'Queries Hoje',
      value: stats.queriesToday,
      icon: Activity,
      description: 'Consultas realizadas hoje',
    },
    {
      title: 'Saúde do Sistema',
      value: `${stats.systemHealth}%`,
      icon: Server,
      description: 'Status operacional',
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {items.map((item) => (
        <Card key={item.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {item.title}
            </CardTitle>
            <item.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{item.value}</div>
            <p className="text-xs text-muted-foreground">
              {item.description}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
