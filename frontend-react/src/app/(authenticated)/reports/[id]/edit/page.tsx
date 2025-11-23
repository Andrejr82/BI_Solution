/**
 * Edit Report Page
 * Página de edição de relatório existente
 */

'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useReport, useReports } from '@/hooks/useReports';
import { ReportEditor } from '@/components/reports/ReportEditor';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Save, Loader2, FileDown } from 'lucide-react';
import Link from 'next/link';
import { ProtectedRoute } from '@/components/permissions';
import { Permission } from '@/lib/permissions';
import { useToast } from '@/hooks/use-toast';

export default function EditReportPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const id = params.id as string;

  const { data: report, isLoading } = useReport(id);
  const { updateReport, generatePDF, isSaving, isGenerating } = useReports();

  const [title, setTitle] = useState('');
  const [content, setContent] = useState<any>(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  useEffect(() => {
    if (report) {
      setTitle(report.title);
      setContent(report.content);
    }
  }, [report]);

  const handleSave = () => {
    updateReport(
      { id, data: { title, content } },
      {
        onSuccess: () => {
          setHasUnsavedChanges(false);
        },
      }
    );
  };

  const handleContentChange = (newContent: any) => {
    setContent(newContent);
    setHasUnsavedChanges(true);
  };

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTitle(e.target.value);
    setHasUnsavedChanges(true);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!report) {
    return (
      <div className="container mx-auto p-6 text-center">
        <h1 className="text-2xl font-bold">Relatório não encontrado</h1>
        <Link href="/reports">
          <Button className="mt-4">Voltar para lista</Button>
        </Link>
      </div>
    );
  }

  return (
    <ProtectedRoute permission={Permission.EDIT_REPORTS}>
      <div className="container mx-auto p-6 space-y-6 h-[calc(100vh-4rem)] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Link href="/reports">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            </Link>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Input
                  value={title}
                  onChange={handleTitleChange}
                  className="text-lg font-bold h-auto py-1 px-2 w-[300px] lg:w-[500px]"
                />
                {hasUnsavedChanges && (
                  <Badge variant="secondary" className="text-xs">
                    Não salvo
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground px-2">
                <span>Status: {report.status}</span>
                <span>•</span>
                <span>Autor: {report.authorName}</span>
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => generatePDF(id)}
              disabled={isGenerating || hasUnsavedChanges}
            >
              {isGenerating ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <FileDown className="mr-2 h-4 w-4" />
              )}
              Exportar PDF
            </Button>

            <Button onClick={handleSave} disabled={!hasUnsavedChanges || isSaving}>
              {isSaving ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Save className="mr-2 h-4 w-4" />
              )}
              Salvar
            </Button>
          </div>
        </div>

        {/* Editor */}
        <div className="flex-1 border rounded-lg overflow-hidden bg-background">
          <ReportEditor
            content={content}
            onChange={handleContentChange}
          />
        </div>
      </div>
    </ProtectedRoute>
  );
}
