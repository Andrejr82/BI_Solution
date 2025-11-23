/**
 * ChartBuilder Component
 * Construtor de gráficos interativos usando Recharts
 */

'use client';

import { useMemo } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { AnalyticsData } from '@/types/analytics';

interface ChartBuilderProps {
  data?: AnalyticsData[];
  isLoading?: boolean;
}

const COLORS = ['#0ea5e9', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'];

export function ChartBuilder({ data, isLoading }: ChartBuilderProps) {
  // Preparar dados para os gráficos
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];

    return data.map((item) => ({
      name: new Date(item.date).toLocaleDateString('pt-BR', { 
        day: '2-digit', 
        month: 'short' 
      }),
      value: item.value,
      category: item.category,
    }));
  }, [data]);

  // Dados agregados por categoria para gráfico de pizza
  const pieData = useMemo(() => {
    if (!data || data.length === 0) return [];

    const categoryTotals = data.reduce((acc, item) => {
      acc[item.category] = (acc[item.category] || 0) + item.value;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(categoryTotals).map(([name, value]) => ({
      name,
      value,
    }));
  }, [data]);

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-[400px]">
          <p className="text-muted-foreground">Carregando gráficos...</p>
        </div>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-[400px]">
          <p className="text-muted-foreground">Nenhum dado disponível para visualização</p>
        </div>
      </Card>
    );
  }

  return (
    <Tabs defaultValue="line" className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="line">📈 Linha</TabsTrigger>
        <TabsTrigger value="bar">📊 Barras</TabsTrigger>
        <TabsTrigger value="pie">🥧 Pizza</TabsTrigger>
      </TabsList>

      {/* Line Chart */}
      <TabsContent value="line">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Evolução Temporal</h3>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => 
                  new Intl.NumberFormat('pt-BR', {
                    notation: 'compact',
                    compactDisplay: 'short',
                  }).format(value)
                }
              />
              <Tooltip 
                formatter={(value: number) => 
                  new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL',
                  }).format(value)
                }
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#0ea5e9" 
                strokeWidth={2}
                name="Valor"
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </TabsContent>

      {/* Bar Chart */}
      <TabsContent value="bar">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Comparação por Período</h3>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => 
                  new Intl.NumberFormat('pt-BR', {
                    notation: 'compact',
                    compactDisplay: 'short',
                  }).format(value)
                }
              />
              <Tooltip 
                formatter={(value: number) => 
                  new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL',
                  }).format(value)
                }
              />
              <Legend />
              <Bar 
                dataKey="value" 
                fill="#8b5cf6" 
                name="Valor"
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </TabsContent>

      {/* Pie Chart */}
      <TabsContent value="pie">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Distribuição por Categoria</h3>
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => 
                  `${name}: ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={120}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value: number) => 
                  new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL',
                  }).format(value)
                }
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </TabsContent>
    </Tabs>
  );
}
