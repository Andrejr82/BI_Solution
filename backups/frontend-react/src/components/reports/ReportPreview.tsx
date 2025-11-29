/**
 * ReportPreview Component
 * Visualização de relatório em modo leitura
 */

import { ReportEditor } from './ReportEditor';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Calendar, User } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import type { Report } from '@/types/reports';

interface ReportPreviewProps {
  report: Report;
}

export function ReportPreview({ report }: ReportPreviewProps) {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="space-y-4 text-center">
        <h1 className="text-4xl font-bold text-foreground">{report.title}</h1>
        {report.description && (
          <p className="text-xl text-muted-foreground">{report.description}</p>
        )}
        
        <div className="flex items-center justify-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <User className="h-4 w-4" />
            <span>{report.authorName || 'Autor desconhecido'}</span>
          </div>
          <div className="flex items-center gap-1">
            <Calendar className="h-4 w-4" />
            <span>
              {format(new Date(report.createdAt), "d 'de' MMMM 'de' yyyy", { locale: ptBR })}
            </span>
          </div>
          <Badge variant="outline">{report.status}</Badge>
        </div>
      </div>

      <Card className="p-8 min-h-[500px]">
        <ReportEditor 
          content={report.content} 
          onChange={() => {}} 
          editable={false} 
        />
      </Card>
    </div>
  );
}
