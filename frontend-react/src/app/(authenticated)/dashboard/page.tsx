'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, Users, DollarSign, Package } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

interface Metrics {
  totalSales: number;
  totalUsers: number;
  revenue: number;
  productsCount: number;
  salesGrowth: number;
  usersGrowth: number;
}

async function fetchMetrics(): Promise<Metrics> {
  return apiClient.get<Metrics>('/api/metrics/summary');
}

export default function DashboardPage() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['metrics'],
    queryFn: fetchMetrics,
  });

  const cards = [
    {
      title: 'Vendas Totais',
      value: metrics?.totalSales.toLocaleString('pt-BR') || '0',
      icon: TrendingUp,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      growth: metrics?.salesGrowth,
    },
    {
      title: 'Usuários Ativos',
      value: metrics?.totalUsers.toLocaleString('pt-BR') || '0',
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      growth: metrics?.usersGrowth,
    },
    {
      title: 'Receita',
      value: `R$ ${(metrics?.revenue || 0).toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
      })}`,
      icon: DollarSign,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Produtos',
      value: metrics?.productsCount.toLocaleString('pt-BR') || '0',
      icon: Package,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Visão geral do seu negócio em tempo real
        </p>
      </div>

      {/* Métricas principais */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {cards.map((card) => (
          <Card key={card.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {card.title}
              </CardTitle>
              <div className={`rounded-full p-2 ${card.bgColor}`}>
                <card.icon className={`h-4 w-4 ${card.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <Skeleton className="h-8 w-24" />
              ) : (
                <>
                  <div className="text-2xl font-bold">{card.value}</div>
                  {card.growth !== undefined && (
                    <p
                      className={`mt-1 text-xs ${
                        card.growth >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {card.growth >= 0 ? '+' : ''}
                      {card.growth}% vs mês anterior
                    </p>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Placeholder para gráficos */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Vendas Recentes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Gráfico de vendas será implementado aqui
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Top Produtos</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Ranking de produtos será implementado aqui
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
