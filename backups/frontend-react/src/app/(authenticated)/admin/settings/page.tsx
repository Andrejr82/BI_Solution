/**
 * Settings Page
 * Página de configurações do sistema
 */

'use client';

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAdmin } from '@/hooks/useAdmin';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowLeft, Save, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { RoleBasedRender } from '@/components/permissions';
import { Role } from '@/lib/permissions';

const settingsSchema = z.object({
  siteName: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  maintenanceMode: z.boolean(),
  allowRegistration: z.boolean(),
  defaultRole: z.enum([Role.USER, Role.VIEWER]),
  sessionTimeout: z.coerce.number().min(5, 'Mínimo de 5 minutos'),
});

export default function SettingsPage() {
  const { settings, updateSettings, isSavingSettings } = useAdmin();
  
  const form = useForm<z.infer<typeof settingsSchema>>({
    resolver: zodResolver(settingsSchema),
    defaultValues: {
      siteName: '',
      maintenanceMode: false,
      allowRegistration: false,
      defaultRole: Role.VIEWER,
      sessionTimeout: 30,
    },
  });

  useEffect(() => {
    if (settings) {
      form.reset({
        siteName: settings.siteName,
        maintenanceMode: settings.maintenanceMode,
        allowRegistration: settings.allowRegistration,
        defaultRole: settings.defaultRole as Role.USER | Role.VIEWER,
        sessionTimeout: settings.sessionTimeout,
      });
    }
  }, [settings, form]);

  const onSubmit = (values: z.infer<typeof settingsSchema>) => {
    updateSettings(values);
  };

  return (
    <RoleBasedRender allowedRoles={Role.ADMIN} fallback={<div className="p-6">Acesso negado</div>}>
      <div className="container mx-auto p-6 max-w-3xl space-y-6">
        <div className="flex items-center gap-4">
          <Link href="/admin">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Configurações do Sistema</h1>
            <p className="text-muted-foreground">
              Gerencie parâmetros globais da aplicação
            </p>
          </div>
        </div>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Geral</CardTitle>
                <CardDescription>Informações básicas do sistema</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <FormField
                  control={form.control}
                  name="siteName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Nome da Aplicação</FormLabel>
                      <FormControl>
                        <Input {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Acesso e Segurança</CardTitle>
                <CardDescription>Controle de registro e sessões</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <FormField
                  control={form.control}
                  name="allowRegistration"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                      <div className="space-y-0.5">
                        <FormLabel className="text-base">Permitir Registro</FormLabel>
                        <FormDescription>
                          Novos usuários podem criar conta
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="defaultRole"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Role Padrão</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione um role" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value={Role.USER}>Usuário</SelectItem>
                          <SelectItem value={Role.VIEWER}>Visualizador</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormDescription>
                        Atribuído a novos usuários registrados
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="sessionTimeout"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Timeout de Sessão (minutos)</FormLabel>
                      <FormControl>
                        <Input type="number" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Manutenção</CardTitle>
                <CardDescription>Controle de disponibilidade</CardDescription>
              </CardHeader>
              <CardContent>
                <FormField
                  control={form.control}
                  name="maintenanceMode"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                      <div className="space-y-0.5">
                        <FormLabel className="text-base">Modo de Manutenção</FormLabel>
                        <FormDescription>
                          Restringe acesso apenas a administradores
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
              </CardContent>
            </Card>

            <div className="flex justify-end">
              <Button type="submit" disabled={isSavingSettings}>
                {isSavingSettings && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Salvar Alterações
              </Button>
            </div>
          </form>
        </Form>
      </div>
    </RoleBasedRender>
  );
}
