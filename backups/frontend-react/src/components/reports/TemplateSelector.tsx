/**
 * TemplateSelector Component
 * Seletor de templates para novos relatórios
 */

import { Card } from '@/components/ui/card';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ReportTemplate } from '@/types/reports';

interface TemplateSelectorProps {
  templates: ReportTemplate[];
  selectedId?: string;
  onSelect: (id: string) => void;
}

export function TemplateSelector({ templates, selectedId, onSelect }: TemplateSelectorProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {templates.map((template) => (
        <Card
          key={template.id}
          className={cn(
            "cursor-pointer transition-all hover:border-primary relative overflow-hidden",
            selectedId === template.id ? "border-primary ring-2 ring-primary/20" : ""
          )}
          onClick={() => onSelect(template.id)}
        >
          {selectedId === template.id && (
            <div className="absolute top-2 right-2 bg-primary text-primary-foreground rounded-full p-1">
              <Check className="h-3 w-3" />
            </div>
          )}
          
          <div className="aspect-video bg-muted/50 flex items-center justify-center text-muted-foreground text-sm">
            {template.thumbnail ? (
              <img src={template.thumbnail} alt={template.name} className="w-full h-full object-cover" />
            ) : (
              "Preview"
            )}
          </div>
          
          <div className="p-4">
            <h4 className="font-medium">{template.name}</h4>
            <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
              {template.description}
            </p>
          </div>
        </Card>
      ))}
    </div>
  );
}
