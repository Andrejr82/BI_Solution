/**
 * Analytics Page
 * Página principal de análise de dados
 */

'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';
import { ProtectedRoute } from '@/components/permissions';
import { Permission } from '@/lib/permissions';
import { useAnalytics } from '@/hooks/useAnalytics';
import { FilterPanel } from '@/components/analytics/FilterPanel';
import { ChartBuilder } from '@/components/analytics/ChartBuilder';
import { ExportButton } from '@/components/analytics/ExportButton';
import type { AnalyticsFilter } from '@/types/analytics';

export default function AnalyticsPage() {
  const [filters, setFilters] = useState<AnalyticsFilter>({});
  
  const {
    data,
    metrics,
    isLoading,
    isError,
    refetch,
    exportData,
    isExporting,
  } = useAnalytics(filters);

  return (
    <ProtectedRoute permission={Permission.VIEW_ANALYTICS}>
      <div className="container mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">📊 Análise de Dados</h1>
            <p className="text-muted-foreground mt-1">
              Explore e analise seus dados de forma interativa
            </p>
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetch()}
              disabled={isLoading}
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              Atualizar
            </Button>

            <ExportButton
              onExport={(format) => exportData(format, filters)}
              isExporting={isExporting}
              disabled={!data || data.length === 0}
            />
          </div>
        </div>

        {/* Metrics Cards */}
        {metrics && metrics.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {metrics.map((metric, index) => (
              <Card key={index} className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      {metric.label}
                    </p>
                    <h3 className="text-2xl font-bold mt-2">
                      {metric.format === 'currency' && 'R$ '}
                      {metric.value.toLocaleString('pt-BR')}
                      {metric.format === 'percentage' && '%'}
                    </h3>
                    {metric.trend !== undefined && (
                      <p className={`text-sm mt-1 ${metric.trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {metric.trend >= 0 ? '↑' : '↓'} {Math.abs(metric.trend)}%
                      </p>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Panel */}
          <Card className="lg:col-span-1 p-4">
            <FilterPanel filters={filters} onChange={setFilters} />
          </Card>

          {/* Data Visualization */}
          <div className="lg:col-span-3">
            <Tabs defaultValue="table" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="table">📋 Tabela</TabsTrigger>
                <TabsTrigger value="charts">📈 Gráficos</TabsTrigger>
              </TabsList>

              <TabsContent value="table" className="mt-4">
                <Card className="p-6">
                  {isLoading && (
                    <div className="flex items-center justify-center py-12">
                      <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
                    </div>
                  )}

                  {isError && (
                    <div className="text-center py-12">
                      <p className="text-destructive">Erro ao carregar dados</p>
                    </div>
                  )}

                  {data && data.length === 0 && (
                    <div className="text-center py-12">
                      <p className="text-muted-foreground">Nenhum dado encontrado</p>
                    </div>
                  )}

                  {data && data.length > 0 && (
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left p-2">Data</th>
                            <th className="text-left p-2">Categoria</th>
                            <th className="text-right p-2">Valor</th>
                            <th className="text-right p-2">Crescimento</th>
                          </tr>
                        </thead>
                        <tbody>
                          {data.map((item) => (
                            <tr key={item.id} className="border-b hover:bg-muted/50">
                              <td className="p-2">{new Date(item.date).toLocaleDateString('pt-BR')}</td>
                              <td className="p-2">{item.category}</td>
                              <td className="p-2 text-right">
                                R$ {item.value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                              </td>
                              <td className={`p-2 text-right ${item.growth && item.growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {item.growth !== undefined ? `${item.growth >= 0 ? '+' : ''}${item.growth}%` : '-'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </Card>
              </TabsContent>

              <TabsContent value="charts" className="mt-4">
                <ChartBuilder data={data} isLoading={isLoading} />
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
