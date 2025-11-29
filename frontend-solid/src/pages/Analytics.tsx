import { For, Show } from 'solid-js';
import dashboard from '@/store/dashboard';
import { BarChart3, TrendingUp, ArrowUpRight, Activity, Zap } from 'lucide-solid';

export default function Analytics() {
  const { state } = dashboard;

  // Agregar dados reais por UNE para o gráfico
  const getUneData = () => {
    const unes: Record<string, number> = {};
    state.data.forEach(item => {
      unes[item.une] = (unes[item.une] || 0) + item.revenue;
    });
    
    // Pegar Top 5 UNEs
    return Object.entries(unes)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([name, value]) => ({ name, value }));
  };

  const chartData = () => getUneData();
  const maxValue = () => Math.max(...chartData().map(d => d.value)) || 1;

  return (
    <div class="flex flex-col h-full p-6 gap-6 max-w-6xl mx-auto">
      <div>
        <h2 class="text-2xl font-bold tracking-tight">Analytics Avançado</h2>
        <p class="text-muted">Análise de distribuição e tendências em tempo real.</p>
      </div>

      <Show when={!state.isLoading && state.data.length > 0} fallback={
        <div class="p-12 text-center border rounded-xl bg-card text-muted">Carregando dados analíticos...</div>
      }>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Gráfico de Barras Real (Top 5 UNEs por Receita) */}
          <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
            <div class="flex items-center justify-between mb-6">
              <h3 class="font-semibold flex items-center gap-2">
                <BarChart3 size={18} />
                Top 5 Lojas (Receita)
              </h3>
              <span class="text-xs text-muted">Base: MES_01</span>
            </div>
            
            <div class="h-[300px] flex items-end justify-around gap-4 pt-4">
              <For each={chartData()}>
                {(item) => {
                  const height = () => `${(item.value / maxValue()) * 100}%`;
                  
                  return (
                    <div class="flex-1 flex flex-col items-center gap-2 group cursor-pointer">
                      <div class="relative w-full flex items-end justify-center h-full">
                        <div 
                          class="w-full max-w-[60px] bg-primary/80 hover:bg-primary rounded-t-md transition-all duration-500 ease-out relative group-hover:shadow-[0_0_20px_rgba(56,189,248,0.3)]"
                          style={{ height: height() }}
                        >
                          <div class="absolute -top-8 left-1/2 -translate-x-1/2 bg-popover border px-2 py-1 rounded text-xs font-bold opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                            R$ {(item.value / 1000).toFixed(1)}k
                          </div>
                        </div>
                      </div>
                      <span class="text-xs font-medium text-muted group-hover:text-foreground transition-colors truncate max-w-[60px]">{item.name}</span>
                    </div>
                  );
                }}
              </For>
            </div>
          </div>

          {/* Resumo de Inteligência */}
          <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm flex flex-col">
            <h3 class="font-semibold flex items-center gap-2 mb-4">
              <TrendingUp size={18} />
              Insights do Sistema
            </h3>
            
            <div class="space-y-4">
              <div class="p-4 bg-secondary/30 rounded-lg border border-secondary">
                <div class="flex items-center gap-2 text-sm font-medium text-primary mb-2">
                  <ArrowUpRight size={16} />
                  Crescimento de Vendas
                </div>
                <p class="text-xs text-muted">
                  O faturamento total é de <b>R$ {(state.summary?.revenue || 0).toLocaleString()}</b>. 
                  {state.summary?.salesGrowth ? 
                    ` Isso representa uma variação de ${state.summary.salesGrowth.toFixed(1)}% comparado ao mês anterior.` : 
                    ' Sem dados históricos suficientes para comparação.'}
                </p>
              </div>

              <div class="p-4 bg-secondary/30 rounded-lg border border-secondary">
                <div class="flex items-center gap-2 text-sm font-medium text-yellow-500 mb-2">
                  <Activity size={16} />
                  Cobertura de Lojas
                </div>
                <p class="text-xs text-muted">
                  Atualmente monitorando <b>{state.summary?.totalUsers}</b> unidades de negócio (UNEs) ativas com vendas registradas nos últimos 30 dias.
                </p>
              </div>

              <div class="p-4 bg-secondary/30 rounded-lg border border-secondary">
                <div class="flex items-center gap-2 text-sm font-medium text-green-500 mb-2">
                  <Zap size={16} />
                  Eficiência
                </div>
                <p class="text-xs text-muted">
                  Média de vendas por produto ativo: <b>R$ {(state.summary?.revenue / (state.summary?.productsCount || 1)).toFixed(2)}</b>.
                </p>
              </div>
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
}