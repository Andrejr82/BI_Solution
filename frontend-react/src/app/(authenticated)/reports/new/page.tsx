/**
 * New Report Page
 * Página de criação de novo relatório
 */

'use client';

import { useState } from 'react';
import { useReports } from '@/hooks/useReports';
import { TemplateSelector } from '@/components/reports/TemplateSelector';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { ArrowLeft, ArrowRight, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { ProtectedRoute } from '@/components/permissions';
import { Permission } from '@/lib/permissions';

export default function NewReportPage() {
  const { templates, createReport, isCreating } = useReports();
  const [step, setStep] = useState<'template' | 'details'>('template');
  const [selectedTemplate, setSelectedTemplate] = useState<string | undefined>();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
  });

  const handleCreate = () => {
    if (!formData.title) return;

    const template = templates?.find(t => t.id === selectedTemplate);

    createReport({
      title: formData.title,
      description: formData.description,
      templateId: selectedTemplate,
      content: template?.content,
    });
  };

  return (
    <ProtectedRoute permission={Permission.CREATE_REPORTS}>
      <div className="container mx-auto p-6 max-w-4xl space-y-6">
        <div className="flex items-center gap-4">
          <Link href="/reports">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Novo Relatório</h1>
            <p className="text-muted-foreground">
              {step === 'template' ? 'Escolha um modelo' : 'Defina os detalhes'}
            </p>
          </div>
        </div>

        {step === 'template' ? (
          <div className="space-y-6">
            <TemplateSelector
              templates={templates || []}
              selectedId={selectedTemplate}
              onSelect={setSelectedTemplate}
            />
            
            <div className="flex justify-end">
              <Button 
                onClick={() => setStep('details')}
                disabled={!selectedTemplate}
              >
                Continuar
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </div>
        ) : (
          <Card className="p-6 space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title">Título do Relatório</Label>
                <Input
                  id="title"
                  placeholder="Ex: Relatório Mensal de Vendas"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Descrição (Opcional)</Label>
                <Textarea
                  id="description"
                  placeholder="Breve descrição do conteúdo..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
            </div>

            <div className="flex justify-between pt-4">
              <Button variant="outline" onClick={() => setStep('template')}>
                Voltar
              </Button>
              <Button onClick={handleCreate} disabled={!formData.title || isCreating}>
                {isCreating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Criar Relatório
              </Button>
            </div>
          </Card>
        )}
      </div>
    </ProtectedRoute>
  );
}
