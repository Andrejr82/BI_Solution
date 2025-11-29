/**
 * ReportCard Component
 * Card para exibir resumo de um relatório na lista
 */

import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { FileText, Calendar, Edit, Trash2, Eye } from 'lucide-react';
import type { Report } from '@/types/reports';
import { PermissionGate } from '@/components/permissions';
import { Permission } from '@/lib/permissions';

interface ReportCardProps {
  report: Report;
  onDelete?: (id: string) => void;
}

export function ReportCard({ report, onDelete }: ReportCardProps) {
  const statusColors = {
    draft: 'bg-yellow-100 text-yellow-800',
    published: 'bg-green-100 text-green-800',
    archived: 'bg-gray-100 text-gray-800',
  };

  const statusLabels = {
    draft: 'Rascunho',
    published: 'Publicado',
    archived: 'Arquivado',
  };

  return (
    <Card className="flex flex-col h-full hover:shadow-md transition-shadow">
      <CardHeader className="p-4 pb-2">
        <div className="flex justify-between items-start">
          <div className="p-2 bg-primary/10 rounded-lg">
            <FileText className="h-6 w-6 text-primary" />
          </div>
          <Badge variant="secondary" className={statusColors[report.status]}>
            {statusLabels[report.status]}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="p-4 flex-1">
        <h3 className="font-semibold text-lg mb-2 line-clamp-1">{report.title}</h3>
        <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
          {report.description || 'Sem descrição'}
        </p>
        
        <div className="flex items-center text-xs text-muted-foreground gap-2">
          <Calendar className="h-3 w-3" />
          <span>
            Atualizado {formatDistanceToNow(new Date(report.updatedAt), { 
              addSuffix: true, 
              locale: ptBR 
            })}
          </span>
        </div>
      </CardContent>

      <CardFooter className="p-4 pt-0 flex justify-between gap-2">
        <Link href={`/reports/${report.id}`} className="flex-1">
          <Button variant="outline" size="sm" className="w-full">
            <Eye className="h-4 w-4 mr-2" />
            Ver
          </Button>
        </Link>

        <PermissionGate permission={Permission.EDIT_REPORTS}>
          <Link href={`/reports/${report.id}/edit`}>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <Edit className="h-4 w-4" />
            </Button>
          </Link>
        </PermissionGate>

        <PermissionGate permission={Permission.DELETE_REPORTS}>
          {onDelete && (
            <Button 
              variant="ghost" 
              size="icon" 
              className="h-8 w-8 text-destructive hover:text-destructive"
              onClick={() => onDelete(report.id)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </PermissionGate>
      </CardFooter>
    </Card>
  );
}
