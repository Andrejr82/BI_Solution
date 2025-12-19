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
  const user = auth.user;

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
      case 'anomaly': return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
      case 'opportunity': return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
      case 'risk': return 'text-rose-500 bg-rose-500/10 border-rose-500/20';
      default: return 'text-gray-500 bg-gray-500/10 border-gray-500/20';
    }
  };

  const getSeverityBadge = (severity: string) => {
    const colors = {
      low: 'bg-green-500/20 text-green-600 border-green-500/30',
      medium: 'bg-yellow-500/20 text-yellow-600 border-yellow-500/30',
      high: 'bg-red-500/20 text-red-600 border-red-500/30 font-bold'
    };

    return colors[severity as keyof typeof colors] || colors.low;
  };

  return (
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex flex-col">
          <div class="flex items-center gap-2">
            <Sparkles class="text-primary" size={24} />
            <h3 class="text-xl font-bold tracking-tight">IA Retail Insights</h3>
            <Show when={user()}>
              <span class="text-[10px] px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20 uppercase font-bold ml-2">
                {user()?.role === 'admin' ? 'Visão Global' : 'Filtro por Segmento'}
              </span>
            </Show>
          </div>
          <p class="text-xs text-muted-foreground mt-1">
            Análise em tempo real baseada em tendências de varejo e estoque.
          </p>
        </div>
        <button
          onClick={refreshInsights}
          disabled={isRefreshing() || insights.loading}
          class="flex items-center gap-2 px-3 py-2 text-sm rounded-lg border hover:bg-muted transition-colors disabled:opacity-50 shadow-sm"
          title="Atualizar insights"
        >
          <RefreshCw size={16} class={isRefreshing() ? 'animate-spin' : ''} />
          <span>Atualizar</span>
        </button>
      </div>

      <Show when={insights.loading}>
        <div class="flex flex-col items-center justify-center py-16 border rounded-xl bg-muted/10 border-dashed">
          <div class="relative">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <Sparkles class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-primary/40" size={16} />
          </div>
          <p class="text-muted-foreground font-medium animate-pulse">O cérebro da IA está analisando seus dados...</p>
        </div>
      </Show>

      <Show when={insights.error}>
        <div class="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-500 flex items-center gap-3">
          <AlertTriangle size={24} />
          <div>
            <p class="font-semibold">Erro na análise de IA</p>
            <p class="text-sm">{insights.error.message}</p>
          </div>
        </div>
      </Show>

      <Show when={!insights.loading && !insights.error && insights()}>
        <div class="grid grid-cols-1 gap-4">
          <Show when={insights()!.insights.length === 0}>
            <div class="p-12 text-center text-muted-foreground border-2 border-dashed rounded-xl">
              <Lightbulb size={48} class="mx-auto mb-3 opacity-20" />
              <p class="text-lg font-medium">Nenhum insight detectado</p>
              <p class="text-sm mt-1">A IA não encontrou anomalias ou oportunidades significativas no momento.</p>
            </div>
          </Show>

          <For each={insights()!.insights}>
            {(insight) => (
              <div class={`group relative p-5 rounded-xl border transition-all hover:shadow-lg ${getCategoryColor(insight.category)} bg-white dark:bg-zinc-900`}>
                <div class="flex items-start gap-4">
                  <div class={`p-3 rounded-lg ${getCategoryColor(insight.category)} border bg-opacity-10`}>
                    {getCategoryIcon(insight.category)}
                  </div>
                  <div class="flex-1">
                    <div class="flex items-start justify-between gap-2 mb-2">
                      <h4 class="font-bold text-lg text-foreground group-hover:text-primary transition-colors">
                        {insight.title}
                      </h4>
                      <span class={`text-[10px] px-2 py-1 rounded-md border shadow-sm ${getSeverityBadge(insight.severity)}`}>
                        {insight.severity.toUpperCase()}
                      </span>
                    </div>
                    <p class="text-sm text-muted-foreground leading-relaxed mb-4">
                      {insight.description}
                    </p>

                    <Show when={insight.recommendation}>
                      <div class="relative mt-2 p-4 rounded-lg bg-primary/5 border border-primary/10 overflow-hidden">
                        <div class="absolute left-0 top-0 w-1 h-full bg-primary" />
                        <div class="flex items-center gap-2 mb-1">
                          <Target size={14} class="text-primary" />
                          <span class="text-xs font-bold text-primary uppercase tracking-widest">Plano de Ação</span>
                        </div>
                        <p class="text-sm font-medium text-foreground italic">
                          "{insight.recommendation}"
                        </p>
                      </div>
                    </Show>

                    <div class="flex items-center justify-between mt-4 pt-4 border-t border-dashed">
                      <div class="flex items-center gap-2 text-[10px] text-muted-foreground font-mono uppercase">
                        <Sparkles size={10} />
                        Gerado via Gemini 2.5
                      </div>
                      <div class="text-[10px] text-muted-foreground">
                        {new Date(insight.created_at).toLocaleString('pt-BR')}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </For>
        </div>

        <div class="text-xs text-muted-foreground text-center pt-6 opacity-60">
          Processados {insights()!.total} indicadores estratégicos • {new Date(insights()!.generated_at).toLocaleTimeString('pt-BR')}
        </div>
      </Show>
    </div>
  );
}

