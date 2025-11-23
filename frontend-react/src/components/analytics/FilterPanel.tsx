/**
 * FilterPanel Component
 * Painel de filtros dinâmicos para analytics
 */

'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { CalendarIcon, X } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import type { AnalyticsFilter } from '@/types/analytics';

interface FilterPanelProps {
  filters: AnalyticsFilter;
  onChange: (filters: AnalyticsFilter) => void;
}

export function FilterPanel({ filters, onChange }: FilterPanelProps) {
  const [startDate, setStartDate] = useState<Date | undefined>(filters.dateRange?.start);
  const [endDate, setEndDate] = useState<Date | undefined>(filters.dateRange?.end);

  const handleDateRangeChange = (start?: Date, end?: Date) => {
    setStartDate(start);
    setEndDate(end);
    
    onChange({
      ...filters,
      dateRange: start && end ? { start, end } : undefined,
    });
  };

  const handleCategoryChange = (category: string) => {
    onChange({
      ...filters,
      category: category === 'all' ? undefined : category,
    });
  };

  const handleSegmentChange = (segment: string) => {
    onChange({
      ...filters,
      segment: segment === 'all' ? undefined : segment,
    });
  };

  const handleClearFilters = () => {
    setStartDate(undefined);
    setEndDate(undefined);
    onChange({});
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Filtros</h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleClearFilters}
          className="h-8 px-2"
        >
          <X className="h-4 w-4 mr-1" />
          Limpar
        </Button>
      </div>

      {/* Date Range */}
      <div className="space-y-2">
        <Label>Período</Label>
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="outline" className="w-full justify-start text-left font-normal">
              <CalendarIcon className="mr-2 h-4 w-4" />
              {startDate && endDate ? (
                `${format(startDate, 'dd/MM/yyyy', { locale: ptBR })} - ${format(endDate, 'dd/MM/yyyy', { locale: ptBR })}`
              ) : (
                <span className="text-muted-foreground">Selecione o período</span>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="start">
            <div className="p-3 space-y-2">
              <div>
                <Label className="text-xs">Data Inicial</Label>
                <Calendar
                  mode="single"
                  selected={startDate}
                  onSelect={(date) => handleDateRangeChange(date, endDate)}
                  locale={ptBR}
                />
              </div>
              <div>
                <Label className="text-xs">Data Final</Label>
                <Calendar
                  mode="single"
                  selected={endDate}
                  onSelect={(date) => handleDateRangeChange(startDate, date)}
                  locale={ptBR}
                  disabled={(date) => startDate ? date < startDate : false}
                />
              </div>
            </div>
          </PopoverContent>
        </Popover>
      </div>

      {/* Category */}
      <div className="space-y-2">
        <Label>Categoria</Label>
        <Select
          value={filters.category || 'all'}
          onValueChange={handleCategoryChange}
        >
          <SelectTrigger>
            <SelectValue placeholder="Todas as categorias" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todas</SelectItem>
            <SelectItem value="vendas">Vendas</SelectItem>
            <SelectItem value="produtos">Produtos</SelectItem>
            <SelectItem value="clientes">Clientes</SelectItem>
            <SelectItem value="financeiro">Financeiro</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Segment */}
      <div className="space-y-2">
        <Label>Segmento</Label>
        <Select
          value={filters.segment || 'all'}
          onValueChange={handleSegmentChange}
        >
          <SelectTrigger>
            <SelectValue placeholder="Todos os segmentos" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos</SelectItem>
            <SelectItem value="armarinho">Armarinho</SelectItem>
            <SelectItem value="confeccao">Confecção</SelectItem>
            <SelectItem value="artesanato">Artesanato</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Value Range */}
      <div className="space-y-2">
        <Label>Valor Mínimo</Label>
        <Input
          type="number"
          placeholder="R$ 0,00"
          value={filters.minValue || ''}
          onChange={(e) =>
            onChange({
              ...filters,
              minValue: e.target.value ? parseFloat(e.target.value) : undefined,
            })
          }
        />
      </div>

      <div className="space-y-2">
        <Label>Valor Máximo</Label>
        <Input
          type="number"
          placeholder="R$ 999.999,99"
          value={filters.maxValue || ''}
          onChange={(e) =>
            onChange({
              ...filters,
              maxValue: e.target.value ? parseFloat(e.target.value) : undefined,
            })
          }
        />
      </div>
    </div>
  );
}
