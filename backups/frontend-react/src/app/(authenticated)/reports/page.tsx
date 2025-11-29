/**
 * Reports Page
 * Página de listagem de relatórios
 */

'use client';

import { useReports } from '@/hooks/useReports';
import { ReportCard } from '@/components/reports/ReportCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plus, Search, Filter } from 'lucide-react';
import Link from 'next/link';
import { ProtectedRoute, PermissionGate } from '@/components/permissions';
import { Permission } from '@/lib/permissions';
import { useState } from 'react';

export default function ReportsPage() {
  const { reports, isLoading, deleteReport } = useReports();
  const [searchTerm, setSearchTerm] = useState('');

  const filteredReports = reports?.filter(report => 
    report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    report.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <ProtectedRoute permission={Permission.VIEW_REPORTS}>
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">📄 Relatórios</h1>
            <p className="text-muted-foreground mt-1">
              Gerencie, crie e compartilhe relatórios de inteligência
            </p>
          </div>

          <PermissionGate permission={Permission.CREATE_REPORTS}>
            <Link href="/reports/new">
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Novo Relatório
              </Button>
            </Link>
          </PermissionGate>
        </div>

        {/* Filters */}
        <div className="flex gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar relatórios..."
              className="pl-8"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Button variant="outline">
            <Filter className="mr-2 h-4 w-4" />
            Filtros
          </Button>
        </div>

        {/* Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-[200px] bg-muted/20 animate-pulse rounded-lg" />
            ))}
          </div>
        ) : filteredReports?.length === 0 ? (
          <div className="text-center py-12 bg-muted/10 rounded-lg border border-dashed">
            <h3 className="text-lg font-medium">Nenhum relatório encontrado</h3>
            <p className="text-muted-foreground mt-1">
              Comece criando seu primeiro relatório de análise.
            </p>
            <PermissionGate permission={Permission.CREATE_REPORTS}>
              <Link href="/reports/new">
                <Button className="mt-4" variant="outline">
                  Criar Relatório
                </Button>
              </Link>
            </PermissionGate>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredReports?.map((report) => (
              <ReportCard 
                key={report.id} 
                report={report} 
                onDelete={deleteReport}
              />
            ))}
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
}
