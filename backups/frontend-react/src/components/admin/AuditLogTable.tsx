/**
 * AuditLogTable Component
 * Tabela de logs de auditoria
 */

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import type { AuditLog } from '@/types/admin';

interface AuditLogTableProps {
  logs: AuditLog[];
}

export function AuditLogTable({ logs }: AuditLogTableProps) {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Data/Hora</TableHead>
            <TableHead>Usuário</TableHead>
            <TableHead>Ação</TableHead>
            <TableHead>Recurso</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>IP</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {logs.map((log) => (
            <TableRow key={log.id}>
              <TableCell className="whitespace-nowrap">
                {format(new Date(log.timestamp), 'dd/MM/yyyy HH:mm:ss', {
                  locale: ptBR,
                })}
              </TableCell>
              <TableCell>{log.userName}</TableCell>
              <TableCell className="font-medium">{log.action}</TableCell>
              <TableCell className="font-mono text-xs">{log.resource}</TableCell>
              <TableCell>
                <Badge 
                  variant={log.status === 'success' ? 'outline' : 'destructive'}
                  className={log.status === 'success' ? 'text-green-600 border-green-600' : ''}
                >
                  {log.status === 'success' ? 'Sucesso' : 'Falha'}
                </Badge>
              </TableCell>
              <TableCell className="text-muted-foreground text-xs">
                {log.ipAddress}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
