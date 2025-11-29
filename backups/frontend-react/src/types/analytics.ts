/**
 * Types para o módulo de Analytics
 */

export interface AnalyticsFilter {
  dateRange?: {
    start: Date;
    end: Date;
  };
  category?: string;
  segment?: string;
  minValue?: number;
  maxValue?: number;
}

export interface AnalyticsData {
  id: string;
  date: string;
  category: string;
  value: number;
  growth?: number;
  metadata?: Record<string, any>;
}

export interface AnalyticsMetric {
  label: string;
  value: number;
  format: 'currency' | 'number' | 'percentage';
  trend?: number;
  icon?: string;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
  }[];
}

export type ExportFormat = 'csv' | 'excel' | 'pdf';

export interface ExportOptions {
  format: ExportFormat;
  filename?: string;
  includeCharts?: boolean;
}
