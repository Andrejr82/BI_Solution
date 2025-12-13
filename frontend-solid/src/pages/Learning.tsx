import { createSignal, onMount, Show, For } from 'solid-js';
import { BrainCircuit, ThumbsUp, ThumbsDown, AlertTriangle, TrendingUp, Search, BarChart3 } from 'lucide-solid';
import api from '../lib/api';

// Types
interface FeedbackStats {
  total_feedback: number;
  positive: number;
  negative: number;
  partial: number;
  success_rate: number;
  problematic_queries: Array<{
    query: string;
    feedback_type: string;
    timestamp: string;
  }>;
}

interface ErrorAnalysis {
  total_errors: number;
  error_types: Record<string, number>;
  error_details: Array<{
    error_type: string;
    count: number;
    suggestion: string;
  }>;
}

interface Pattern {
  id: number;
  keywords: string[];
  pattern: string;
  examples: string[];
  success_count: number;
}

interface PatternsResponse {
  total_patterns: number;
  patterns: Pattern[];
}

type TabType = 'feedback' | 'errors' | 'patterns';

export default function Learning() {
  const [activeTab, setActiveTab] = createSignal<TabType>('feedback');
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal<string | null>(null);

  // Data states
  const [feedbackStats, setFeedbackStats] = createSignal<FeedbackStats | null>(null);
  const [errorAnalysis, setErrorAnalysis] = createSignal<ErrorAnalysis | null>(null);
  const [patterns, setPatterns] = createSignal<PatternsResponse | null>(null);

  // Search
  const [searchTerm, setSearchTerm] = createSignal('');

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [feedbackRes, errorsRes, patternsRes] = await Promise.all([
        api.get<FeedbackStats>('/learning/feedback-stats'),
        api.get<ErrorAnalysis>('/learning/error-analysis'),
        api.get<PatternsResponse>('/learning/patterns')
      ]);

      setFeedbackStats(feedbackRes.data);
      setErrorAnalysis(errorsRes.data);
      setPatterns(patternsRes.data);
    } catch (err: any) {
      console.error('Erro ao carregar dados de aprendizado:', err);
      setError(err.response?.data?.detail || 'Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  const searchPatterns = async () => {
    if (!searchTerm()) {
      loadData();
      return;
    }

    try {
      const response = await api.get<PatternsResponse>(`/learning/patterns?search=${encodeURIComponent(searchTerm())}`);
      setPatterns(response.data);
    } catch (err: any) {
      console.error('Erro ao buscar padrões:', err);
    }
  };

  onMount(() => {
    loadData();
  });

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 80) return 'text-green-500';
    if (rate >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div class="flex flex-col h-full p-6 gap-6">
      {/* Header */}
      <div>
        <h2 class="text-2xl font-bold flex items-center gap-2">
          <BrainCircuit size={28} />
          Sistema de Aprendizado
        </h2>
        <p class="text-muted">Análise de feedback, erros e padrões de uso do assistente BI</p>
      </div>

      {/* Error State */}
      <Show when={error()}>
        <div class="card p-4 border-red-500 bg-red-500/10">
          <div class="flex items-center gap-2 text-red-500">
            <AlertTriangle size={20} />
            <span>{error()}</span>
          </div>
        </div>
      </Show>

      {/* Tabs */}
      <div class="border-b">
        <div class="flex gap-1">
          <button
            class={`px-4 py-2 font-medium transition-colors ${
              activeTab() === 'feedback'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted hover:text-foreground'
            }`}
            onClick={() => setActiveTab('feedback')}
          >
            <div class="flex items-center gap-2">
              <ThumbsUp size={16} />
              Feedback
            </div>
          </button>

          <button
            class={`px-4 py-2 font-medium transition-colors ${
              activeTab() === 'errors'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted hover:text-foreground'
            }`}
            onClick={() => setActiveTab('errors')}
          >
            <div class="flex items-center gap-2">
              <AlertTriangle size={16} />
              Erros
            </div>
          </button>

          <button
            class={`px-4 py-2 font-medium transition-colors ${
              activeTab() === 'patterns'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted hover:text-foreground'
            }`}
            onClick={() => setActiveTab('patterns')}
          >
            <div class="flex items-center gap-2">
              <TrendingUp size={16} />
              Padrões
            </div>
          </button>
        </div>
      </div>

      {/* Loading State */}
      <Show when={loading()}>
        <div class="flex-1 flex items-center justify-center">
          <div class="text-center">
            <BrainCircuit size={48} class="mx-auto mb-4 opacity-50 animate-pulse" />
            <p class="text-muted">Carregando dados...</p>
          </div>
        </div>
      </Show>

      {/* Content */}
      <Show when={!loading()}>
        {/* Tab: Feedback */}
        <Show when={activeTab() === 'feedback'}>
          <Show when={feedbackStats()}>
            <div class="space-y-6">
              {/* KPIs */}
              <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="card p-4 border">
                  <div class="text-sm text-muted mb-1">Total de Feedback</div>
                  <div class="text-2xl font-bold">{feedbackStats()!.total_feedback}</div>
                </div>

                <div class="card p-4 border border-green-500/30 bg-green-500/5">
                  <div class="text-sm text-muted mb-1">Positivos</div>
                  <div class="text-2xl font-bold text-green-500">
                    {feedbackStats()!.positive}
                  </div>
                </div>

                <div class="card p-4 border border-red-500/30 bg-red-500/5">
                  <div class="text-sm text-muted mb-1">Negativos</div>
                  <div class="text-2xl font-bold text-red-500">
                    {feedbackStats()!.negative}
                  </div>
                </div>

                <div class="card p-4 border border-yellow-500/30 bg-yellow-500/5">
                  <div class="text-sm text-muted mb-1">Parciais</div>
                  <div class="text-2xl font-bold text-yellow-500">
                    {feedbackStats()!.partial}
                  </div>
                </div>
              </div>

              {/* Success Rate Gauge */}
              <div class="card p-6 border">
                <h3 class="font-semibold mb-4">Taxa de Sucesso</h3>
                <div class="flex items-center justify-center">
                  <div class="text-center">
                    <div class={`text-6xl font-bold ${getSuccessRateColor(feedbackStats()!.success_rate)}`}>
                      {feedbackStats()!.success_rate}%
                    </div>
                    <div class="text-sm text-muted mt-2">
                      Baseado em {feedbackStats()!.total_feedback} feedbacks
                    </div>
                  </div>
                </div>
              </div>

              {/* Problematic Queries */}
              <Show when={feedbackStats()!.problematic_queries.length > 0}>
                <div class="card border">
                  <div class="p-4 border-b">
                    <h3 class="font-semibold">Queries Problemáticas (Top 10)</h3>
                    <p class="text-sm text-muted">Queries que receberam feedback negativo</p>
                  </div>
                  <div class="overflow-x-auto">
                    <table class="w-full">
                      <thead class="bg-muted/50">
                        <tr class="text-left text-xs font-medium text-muted uppercase">
                          <th class="p-3">Query</th>
                          <th class="p-3">Tipo</th>
                          <th class="p-3">Timestamp</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y">
                        <For each={feedbackStats()!.problematic_queries}>
                          {(query) => (
                            <tr class="hover:bg-muted/30">
                              <td class="p-3 text-sm">{query.query}</td>
                              <td class="p-3">
                                <span class="px-2 py-1 bg-red-500/10 text-red-500 text-xs rounded">
                                  {query.feedback_type}
                                </span>
                              </td>
                              <td class="p-3 text-sm text-muted font-mono">{query.timestamp}</td>
                            </tr>
                          )}
                        </For>
                      </tbody>
                    </table>
                  </div>
                </div>
              </Show>
            </div>
          </Show>
        </Show>

        {/* Tab: Errors */}
        <Show when={activeTab() === 'errors'}>
          <Show when={errorAnalysis()}>
            <div class="space-y-6">
              {/* Total Errors */}
              <div class="card p-6 border">
                <div class="text-sm text-muted mb-1">Total de Erros</div>
                <div class="text-4xl font-bold text-red-500">
                  {errorAnalysis()!.total_errors}
                </div>
              </div>

              {/* Error Types Bar Chart */}
              <div class="card p-6 border">
                <h3 class="font-semibold mb-4 flex items-center gap-2">
                  <BarChart3 size={20} />
                  Tipos de Erro
                </h3>
                <div class="space-y-3">
                  <For each={Object.entries(errorAnalysis()!.error_types)}>
                    {([type, count]) => {
                      const total = errorAnalysis()!.total_errors;
                      const percentage = (count / total) * 100;
                      return (
                        <div>
                          <div class="flex justify-between text-sm mb-1">
                            <span class="font-medium">{type}</span>
                            <span class="text-muted">{count} ({percentage.toFixed(1)}%)</span>
                          </div>
                          <div class="h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              class="h-full bg-red-500"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      );
                    }}
                  </For>
                </div>
              </div>

              {/* Error Details & Suggestions */}
              <div class="card border">
                <div class="p-4 border-b">
                  <h3 class="font-semibold">Detalhes e Sugestões</h3>
                </div>
                <div class="divide-y">
                  <For each={errorAnalysis()!.error_details}>
                    {(detail) => (
                      <div class="p-4">
                        <div class="flex items-start gap-3">
                          <div class="p-2 bg-red-500/10 rounded">
                            <AlertTriangle size={20} class="text-red-500" />
                          </div>
                          <div class="flex-1">
                            <div class="font-medium mb-1">{detail.error_type}</div>
                            <div class="text-sm text-muted mb-2">{detail.count} ocorrências</div>
                            <div class="text-sm bg-blue-500/10 text-blue-400 p-2 rounded">
                              💡 {detail.suggestion}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </For>
                </div>
              </div>
            </div>
          </Show>
        </Show>

        {/* Tab: Patterns */}
        <Show when={activeTab() === 'patterns'}>
          <Show when={patterns()}>
            <div class="space-y-6">
              {/* Search */}
              <div class="flex gap-2">
                <div class="flex-1 relative">
                  <Search size={20} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
                  <input
                    type="text"
                    class="input pl-10 w-full"
                    placeholder="Buscar padrões por palavra-chave..."
                    value={searchTerm()}
                    onInput={(e) => setSearchTerm(e.currentTarget.value)}
                    onKeyPress={(e) => e.key === 'Enter' && searchPatterns()}
                  />
                </div>
                <button class="btn btn-primary" onClick={searchPatterns}>
                  Buscar
                </button>
              </div>

              {/* Total Patterns */}
              <div class="card p-4 border">
                <div class="text-sm text-muted mb-1">Padrões Identificados</div>
                <div class="text-2xl font-bold">{patterns()!.total_patterns}</div>
              </div>

              {/* Patterns List */}
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <For each={patterns()!.patterns}>
                  {(pattern) => (
                    <div class="card p-4 border hover:border-primary/50 transition-colors">
                      <div class="flex items-start justify-between mb-3">
                        <h4 class="font-semibold">{pattern.pattern}</h4>
                        <span class="px-2 py-1 bg-primary/10 text-primary text-xs rounded">
                          {pattern.success_count} sucessos
                        </span>
                      </div>

                      <div class="mb-3">
                        <div class="text-xs text-muted mb-1">Palavras-chave:</div>
                        <div class="flex flex-wrap gap-1">
                          <For each={pattern.keywords}>
                            {(keyword) => (
                              <span class="px-2 py-0.5 bg-secondary text-xs rounded">
                                {keyword}
                              </span>
                            )}
                          </For>
                        </div>
                      </div>

                      <div>
                        <div class="text-xs text-muted mb-1">Exemplos:</div>
                        <ul class="text-sm space-y-1">
                          <For each={pattern.examples}>
                            {(example) => (
                              <li class="text-muted italic">• {example}</li>
                            )}
                          </For>
                        </ul>
                      </div>
                    </div>
                  )}
                </For>
              </div>

              <Show when={patterns()!.patterns.length === 0}>
                <div class="card p-12 text-center border-dashed">
                  <Search size={48} class="mx-auto mb-4 opacity-20" />
                  <p class="text-muted">Nenhum padrão encontrado</p>
                </div>
              </Show>
            </div>
          </Show>
        </Show>
      </Show>
    </div>
  );
}
