/**
 * UserTable Component
 * Tabela de gestão de usuários
 */

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { MoreHorizontal, Edit, Trash2, Shield } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import type { User } from '@/types/admin';
import { Role, roleLabels } from '@/lib/permissions';

interface UserTableProps {
  users: User[];
  onEdit: (user: User) => void;
  onDelete: (id: string) => void;
}

export function UserTable({ users, onEdit, onDelete }: UserTableProps) {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Usuário</TableHead>
            <TableHead>Role</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Último Acesso</TableHead>
            <TableHead className="text-right">Ações</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {users.map((user) => (
            <TableRow key={user.id}>
              <TableCell className="flex items-center gap-3">
                <Avatar className="h-8 w-8">
                  <AvatarFallback>
                    {user.username.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-medium">{user.username}</p>
                  <p className="text-xs text-muted-foreground">{user.email}</p>
                </div>
              </TableCell>
              <TableCell>
                <Badge variant="outline" className="gap-1">
                  {user.role === Role.ADMIN && <Shield className="h-3 w-3" />}
                  {roleLabels[user.role]}
                </Badge>
              </TableCell>
              <TableCell>
                <Badge variant={user.isActive ? 'default' : 'secondary'}>
                  {user.isActive ? 'Ativo' : 'Inativo'}
                </Badge>
              </TableCell>
              <TableCell>
                {user.lastLogin ? (
                  formatDistanceToNow(new Date(user.lastLogin), {
                    addSuffix: true,
                    locale: ptBR,
                  })
                ) : (
                  <span className="text-muted-foreground">-</span>
                )}
              </TableCell>
              <TableCell className="text-right">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="h-8 w-8 p-0">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuLabel>Ações</DropdownMenuLabel>
                    <DropdownMenuItem onClick={() => onEdit(user)}>
                      <Edit className="mr-2 h-4 w-4" />
                      Editar
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      className="text-destructive"
                      onClick={() => onDelete(user.id)}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Remover
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
