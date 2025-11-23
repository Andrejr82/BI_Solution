/**
 * Types para o módulo de Relatórios
 */

export type ReportStatus = 'draft' | 'published' | 'archived';
export type ReportFrequency = 'daily' | 'weekly' | 'monthly' | 'once';

export interface Report {
  id: string;
  title: string;
  description?: string;
  content: any; // JSON content from TipTap
  status: ReportStatus;
  authorId: string;
  authorName?: string;
  createdAt: string;
  updatedAt: string;
  tags?: string[];
  thumbnail?: string;
}

export interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  content: any; // JSON structure
  thumbnail?: string;
  category: 'sales' | 'financial' | 'operational' | 'custom';
}

export interface ReportSchedule {
  id: string;
  reportId: string;
  frequency: ReportFrequency;
  recipients: string[]; // emails
  nextRun?: string;
  lastRun?: string;
  active: boolean;
  format: 'pdf' | 'html';
}

export interface CreateReportDTO {
  title: string;
  description?: string;
  content?: any;
  templateId?: string;
}

export interface UpdateReportDTO {
  title?: string;
  description?: string;
  content?: any;
  status?: ReportStatus;
  tags?: string[];
}
