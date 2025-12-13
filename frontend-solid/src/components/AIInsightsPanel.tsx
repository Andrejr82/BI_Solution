import { createSignal, createResource, For, Show } from 'solid-js';
import { Lightbulb, TrendingUp, AlertTriangle, Target, Sparkles, RefreshCw } from 'lucide-solid';
import auth from '@/store/auth';

interface Insight {
  id: string;
  title: string;
  description: string;
  category: 'trend' | 'anomaly' | 'opportunity' | 'risk';
  severity: 'low' | 'medium' | 'high';
  recommendation: string | null;
  data_points: any[] | null;
  created_at: string;
}

interface InsightsData {
  insights: Insight[];
  total: number;
  generated_at: string;
}

export function AIInsightsPanel() {
  const [isRefreshing, setIsRefreshing] = createSignal(false);

  const fetchInsights = async (): Promise<InsightsData> => {
    const token = auth.token();
    if (!token) throw new Error('Not authenticated');

    const response = await fetch('/api/v1/insights/proactive', {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch insights');
    }

    return response.json();
  };

  const [insights, { refetch }] = createResource(fetchInsights);

  const refreshInsights = async () => {
    setIsRefreshing(true);
    await refetch();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'trend': return <TrendingUp size={20} />;
      case 'anomaly': return <AlertTriangle size={20} />;
      case 'opportunity': return <Target size={20} />;
      case 'risk': return <AlertTriangle size={20} />;
      default: return <Lightbulb size={20} />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'trend': return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
      case 'anomaly': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
      case 'opportunity': return 'text-green-500 bg-green-500/10 border-green-500/20';
      case 'risk': return 'text-red-500 bg-red-500/10 border-red-500/20';
      default: return 'text-gray-500 bg-gray-500/10 border-gray-500/20';
    }
  };

  const getSeverityBadge = (severity: string) => {
    const colors = {
      low: 'bg-green-500/20 text-green-500 border-green-500/30',
      medium: 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30',
      high: 'bg-red-500/20 text-red-500 border-red-500/30'
    };

    return colors[severity as keyof typeof colors] || colors.low;
  };

  return (
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Sparkles class="text-primary" size={24} />
          <h3 class="text-xl font-semibold">AI Insights</h3>
        </div>
        <button
          onClick={refreshInsights}
          disabled={isRefreshing() || insights.loading}
          class="flex items-center gap-2 px-3 py-2 text-sm rounded-lg border hover:bg-muted transition-colors disabled:opacity-50"
          title="Atualizar insights"
        >
          <RefreshCw size={16} class={isRefreshing() ? 'animate-spin' : ''} />
          <span>Atualizar</span>
        </button>
      </div>

      <Show when={insights.loading}>
        <div class="flex items-center justify-center py-12">
          <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p class="text-muted-foreground">Gerando insights com IA...</p>
          </div>
        </div>
      </Show>

      <Show when={insights.error}>
        <div class="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-500">
          <p class="font-semibold mb-1">Erro ao carregar insights</p>
          <p class="text-sm">{insights.error.message}</p>
        </div>
      </Show>

      <Show when={!insights.loading && !insights.error && insights()}>
        <div class="space-y-3">
          <Show when={insights()!.insights.length === 0}>
            <div class="p-6 text-center text-muted-foreground border rounded-lg">
              <Lightbulb size={48} class="mx-auto mb-3 opacity-50" />
              <p>Nenhum insight disponível no momento.</p>
              <p class="text-sm mt-2">Tente novamente mais tarde ou adicione mais dados.</p>
            </div>
          </Show>

          <For each={insights()!.insights}>
            {(insight) => (
              <div class={`p-4 rounded-lg border ${getCategoryColor(insight.category)}`}>
                <div class="flex items-start gap-3">
                  <div class="mt-1">
                    {getCategoryIcon(insight.category)}
                  </div>
                  <div class="flex-1">
                    <div class="flex items-start justify-between gap-2 mb-2">
                      <h4 class="font-semibold">{insight.title}</h4>
                      <span class={`text-xs px-2 py-1 rounded border ${getSeverityBadge(insight.severity)}`}>
                        {insight.severity.toUpperCase()}
                      </span>
                    </div>
                    <p class="text-sm mb-3">{insight.description}</p>

                    <Show when={insight.recommendation}>
                      <div class="mt-3 p-3 rounded bg-background/50 border">
                        <p class="text-xs font-semibold mb-1">💡 Recomendação:</p>
                        <p class="text-sm">{insight.recommendation}</p>
                      </div>
                    </Show>

                    <Show when={insight.data_points && insight.data_points.length > 0}>
                      <details class="mt-3">
                        <summary class="text-xs text-muted-foreground cursor-pointer hover:text-foreground">
                          Ver dados ({insight.data_points!.length} pontos)
                        </summary>
                        <div class="mt-2 p-2 rounded bg-background/30 text-xs font-mono max-h-32 overflow-auto">
                          <pre>{JSON.stringify(insight.data_points, null, 2)}</pre>
                        </div>
                      </details>
                    </Show>

                    <div class="text-xs text-muted-foreground mt-3">
                      {new Date(insight.created_at).toLocaleString('pt-BR')}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </For>
        </div>

        <div class="text-xs text-muted-foreground text-center pt-2">
          {insights()!.total} insights gerados em {new Date(insights()!.generated_at).toLocaleTimeString('pt-BR')}
        </div>
      </Show>
    </div>
  );
}
