import { createSignal, onMount, Show, For } from 'solid-js';
import { ShoppingCart, Package, AlertTriangle, DollarSign, RefreshCw, TrendingUp, X } from 'lucide-solid';
import api from '../lib/api';
import { PlotlyChart } from '../components/PlotlyChart';
import { ChartDownloadButton } from '../components/ChartDownloadButton';
import { AIInsightsPanel } from '../components/AIInsightsPanel';

interface BusinessKPIs {
  total_produtos: number;
  total_unes: number;
  produtos_ruptura: number;
  valor_estoque: number;
  top_produtos: Array<{
    produto: string;
    nome: string;
    vendas: number;
  }>;
  vendas_por_categoria: Array<{
    categoria: string;
    vendas: number;
    produtos: number;
  }>;
}

export default function Dashboard() {
  const [kpis, setKpis] = createSignal<BusinessKPIs | null>(null);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal<string | null>(null);
  const [lastUpdate, setLastUpdate] = createSignal<Date | null>(null);
  const [selectedProductInfo, setSelectedProductInfo] = createSignal<{
    produto: string;
    nome: string;
    vendas: number;
  } | null>(null);

  // Chart specs para Plotly
  const [topProdutosChart, setTopProdutosChart] = createSignal<any>({});
  const [vendasCategoriaChart, setVendasCategoriaChart] = createSignal<any>({});

  const loadKPIs = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.get<BusinessKPIs>('/metrics/business-kpis');
      setKpis(response.data);
      setLastUpdate(new Date());

      // Gerar gráfico de Top 10 Produtos
      if (response.data.top_produtos.length > 0) {
        const topProdutosSpec = {
          data: [{
            type: 'bar',
            x: response.data.top_produtos.map(p => p.nome),
            y: response.data.top_produtos.map(p => p.vendas),
            marker: {
              color: '#3b82f6',
              line: {
                color: '#1e40af',
                width: 1
              }
            },
            text: response.data.top_produtos.map(p => p.vendas.toLocaleString()),
            textposition: 'outside',
            hovertemplate: '<b>%{x}</b><br>Vendas: %{y:,}<extra></extra>',
            customdata: response.data.top_produtos.map(p => ({ produto: p.produto, nome: p.nome, vendas: p.vendas }))
          }],
          layout: {
            title: {
              text: 'Top 10 Produtos Mais Vendidos',
              font: { size: 16, color: '#e5e7eb' }
            },
            xaxis: {
              title: '',
              tickangle: -45,
              tickfont: { size: 10, color: '#9ca3af' },
              gridcolor: '#374151'
            },
            yaxis: {
              title: 'Vendas (30 dias)',
              titlefont: { color: '#9ca3af' },
              tickfont: { color: '#9ca3af' },
              gridcolor: '#374151'
            },
            plot_bgcolor: '#1f2937',
            paper_bgcolor: '#1f2937',
            margin: { l: 60, r: 20, t: 60, b: 120 },
            font: { color: '#e5e7eb' }
          },
          config: { responsive: true }
        };
        setTopProdutosChart(topProdutosSpec);
      }

      // Gerar gráfico de Vendas por Categoria
      if (response.data.vendas_por_categoria.length > 0) {
        const vendasCategoriaSpec = {
          data: [{
            type: 'pie',
            labels: response.data.vendas_por_categoria.map(c => c.categoria),
            values: response.data.vendas_por_categoria.map(c => c.vendas),
            hovertemplate: '<b>%{label}</b><br>Vendas: %{value:,}<br>%{percent}<extra></extra>',
            marker: {
              colors: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
            },
            textinfo: 'label+percent',
            textposition: 'inside',
            textfont: { size: 11 }
          }],
          layout: {
            title: {
              text: 'Vendas por Categoria',
              font: { size: 16, color: '#e5e7eb' }
            },
            plot_bgcolor: '#1f2937',
            paper_bgcolor: '#1f2937',
            margin: { l: 20, r: 20, t: 60, b: 20 },
            font: { color: '#e5e7eb' },
            showlegend: true,
            legend: {
              orientation: 'v',
              x: 1,
              y: 1,
              font: { size: 10, color: '#9ca3af' }
            }
          },
          config: { responsive: true }
        };
        setVendasCategoriaChart(vendasCategoriaSpec);
      }

    } catch (err: any) {
      console.error('Erro ao carregar KPIs:', err);
      setError(err.response?.data?.detail || 'Erro ao carregar métricas');
    } finally {
      setLoading(false);
    }
  };

  onMount(() => {
    loadKPIs();

    // Auto-refresh a cada 30 segundos
    const interval = setInterval(() => {
      loadKPIs();
    }, 30000);

    return () => clearInterval(interval);
  });

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const handleProductClick = (clickData: any) => {
    if (clickData && clickData.points && clickData.points[0]) {
      const point = clickData.points[0];
      if (point.customdata) {
        setSelectedProductInfo(point.customdata);
      }
    }
  };

  return (
    <div class="flex flex-col h-full p-6 gap-6">
      {/* Header */}
      <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h2 class="text-2xl font-bold tracking-tight">Dashboard de Negócios</h2>
          <p class="text-muted">
            Métricas em tempo real do seu estoque e vendas
            {lastUpdate() && (
              <span class="ml-2 text-xs opacity-70">
                Última atualização: {lastUpdate()!.toLocaleTimeString()}
              </span>
            )}
          </p>
        </div>
        <button
          onClick={loadKPIs}
          class="btn btn-outline gap-2"
          disabled={loading()}
        >
          <RefreshCw size={16} class={loading() ? 'animate-spin' : ''} />
          Atualizar
        </button>
      </div>

      {/* Loading State */}
      <Show when={loading() && !kpis()}>
        <div class="flex-1 flex items-center justify-center text-muted">
          <div class="text-center">
            <RefreshCw size={32} class="animate-spin mx-auto mb-2" />
            <span>Carregando métricas...</span>
          </div>
        </div>
      </Show>

      {/* Error State */}
      <Show when={error()}>
        <div class="card p-4 border-red-500 bg-red-500/10">
          <div class="flex items-center gap-2 text-red-500">
            <AlertTriangle size={20} />
            <span class="font-medium">{error()}</span>
          </div>
        </div>
      </Show>

      {/* KPIs and Charts */}
      <Show when={kpis() && !loading()}>
        {/* KPI Cards */}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Total Produtos */}
          <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm border-l-4 border-l-primary hover:shadow-lg transition-shadow">
            <div class="flex flex-row items-center justify-between space-y-0 pb-2">
              <span class="text-sm font-medium text-muted">Total de Produtos</span>
              <Package size={16} class="text-primary" />
            </div>
            <div class="text-2xl font-bold">
              {kpis()!.total_produtos.toLocaleString()}
            </div>
            <p class="text-xs text-muted mt-1">Produtos únicos no catálogo</p>
          </div>

          {/* Total UNEs */}
          <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm border-l-4 border-l-primary hover:shadow-lg transition-shadow">
            <div class="flex flex-row items-center justify-between space-y-0 pb-2">
              <span class="text-sm font-medium text-muted">Total de UNEs</span>
              <ShoppingCart size={16} class="text-accent" />
            </div>
            <div class="text-2xl font-bold">
              {kpis()!.total_unes.toLocaleString()}
            </div>
            <p class="text-xs text-muted mt-1">Unidades/lojas ativas</p>
          </div>

          {/* Produtos em Ruptura */}
          <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm border-l-4 border-l-primary hover:shadow-lg transition-shadow">
            <div class="flex flex-row items-center justify-between space-y-0 pb-2">
              <span class="text-sm font-medium text-muted">Produtos em Ruptura</span>
              <AlertTriangle size={16} class="text-destructive" />
            </div>
            <div class="text-2xl font-bold text-destructive">
              {kpis()!.produtos_ruptura.toLocaleString()}
            </div>
            <p class="text-xs text-muted mt-1">CD zerado + Loja abaixo da LV</p>
          </div>

          {/* Valor do Estoque */}
          <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm border-l-4 border-l-primary hover:shadow-lg transition-shadow">
            <div class="flex flex-row items-center justify-between space-y-0 pb-2">
              <span class="text-sm font-medium text-muted">Valor do Estoque</span>
              <DollarSign size={16} class="text-accent" />
            </div>
            <div class="text-2xl font-bold">
              {kpis()!.valor_estoque.toLocaleString('pt-BR')}
            </div>
            <p class="text-xs text-muted mt-1">Unidades em estoque (Loja + CD)</p>
          </div>
        </div>

        {/* Charts Grid */}
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top 10 Produtos Chart */}
          <div class="card p-6 border">
            <div class="flex justify-between items-center mb-4">
              <h3 class="font-semibold">Top 10 Produtos Mais Vendidos</h3>
              <ChartDownloadButton
                chartId="top-produtos-chart"
                filename="dashboard_top_produtos"
                label="Baixar"
              />
            </div>
            <Show
              when={kpis()!.top_produtos.length > 0}
              fallback={
                <div class="h-[400px] flex items-center justify-center text-muted">
                  <div class="text-center">
                    <TrendingUp size={48} class="mx-auto mb-4 opacity-50" />
                    <p>Nenhum dado de vendas disponível</p>
                  </div>
                </div>
              }
            >
              <PlotlyChart
                chartSpec={topProdutosChart}
                chartId="top-produtos-chart"
                enableDownload={true}
                onDataClick={handleProductClick}
              />
              <p class="text-xs text-muted mt-2">💡 Clique nas barras para ver detalhes do produto</p>
            </Show>
          </div>

          {/* Vendas por Categoria Chart */}
          <div class="card p-6 border">
            <div class="flex justify-between items-center mb-4">
              <h3 class="font-semibold">Vendas por Categoria</h3>
              <ChartDownloadButton
                chartId="vendas-categoria-chart"
                filename="dashboard_vendas_categoria"
                label="Baixar"
              />
            </div>
            <Show
              when={kpis()!.vendas_por_categoria.length > 0}
              fallback={
                <div class="h-[400px] flex items-center justify-center text-muted">
                  <div class="text-center">
                    <TrendingUp size={48} class="mx-auto mb-4 opacity-50" />
                    <p>Nenhum dado de categorias disponível</p>
                  </div>
                </div>
              }
            >
              <PlotlyChart
                chartSpec={vendasCategoriaChart}
                chartId="vendas-categoria-chart"
                enableDownload={true}
              />
            </Show>
          </div>
        </div>

        {/* AI Insights Panel */}
        <div class="card border p-6">
          <AIInsightsPanel />
        </div>

        {/* Top Produtos Table */}
        <Show when={kpis()!.top_produtos.length > 0}>
          <div class="card border">
            <div class="p-4 border-b">
              <h3 class="font-semibold text-lg">Ranking de Vendas (30 dias)</h3>
              <p class="text-sm text-muted">Produtos mais vendidos no último mês</p>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead class="bg-muted/50">
                  <tr class="text-left text-xs font-medium text-muted uppercase tracking-wider">
                    <th class="p-3">#</th>
                    <th class="p-3">Código</th>
                    <th class="p-3">Nome do Produto</th>
                    <th class="p-3 text-right">Vendas</th>
                  </tr>
                </thead>
                <tbody class="divide-y">
                  <For each={kpis()!.top_produtos}>
                    {(produto, index) => (
                      <tr class="hover:bg-muted/30 transition-colors">
                        <td class="p-3 font-mono text-sm text-muted">
                          {index() + 1}
                        </td>
                        <td class="p-3 font-mono text-sm">
                          {produto.produto}
                        </td>
                        <td class="p-3 text-sm">
                          {produto.nome}
                        </td>
                        <td class="p-3 text-sm font-semibold text-right">
                          {produto.vendas.toLocaleString()}
                        </td>
                      </tr>
                    )}
                  </For>
                </tbody>
              </table>
            </div>
          </div>
        </Show>
      </Show>

      {/* Modal de Detalhes do Produto */}
      <Show when={selectedProductInfo()}>
        <div
          class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedProductInfo(null)}
        >
          <div
            class="bg-card border rounded-lg p-6 max-w-lg w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <div class="flex justify-between items-start mb-4">
              <h3 class="text-xl font-bold">Informações do Produto</h3>
              <button
                onClick={() => setSelectedProductInfo(null)}
                class="text-muted hover:text-foreground"
              >
                <X size={20} />
              </button>
            </div>

            <div class="space-y-4">
              <div>
                <p class="text-sm text-muted">Código do Produto</p>
                <p class="font-mono font-medium text-lg">{selectedProductInfo()!.produto}</p>
              </div>
              <div>
                <p class="text-sm text-muted">Nome do Produto</p>
                <p class="font-medium">{selectedProductInfo()!.nome}</p>
              </div>
              <div class="p-4 bg-green-500/10 border border-green-500/30 rounded">
                <p class="text-sm text-muted mb-2">Vendas nos últimos 30 dias</p>
                <p class="text-3xl font-bold text-green-500">
                  {selectedProductInfo()!.vendas.toLocaleString()} unidades
                </p>
              </div>
            </div>

            <div class="mt-6 flex justify-end gap-2">
              <button
                onClick={() => setSelectedProductInfo(null)}
                class="btn btn-outline"
              >
                Fechar
              </button>
              <button
                onClick={() => {
                  // Aqui você pode implementar navegação para página de detalhes
                  console.log('Navegar para detalhes:', selectedProductInfo()!.produto);
                  setSelectedProductInfo(null);
                }}
                class="btn btn-primary"
              >
                Ver Mais Detalhes
              </button>
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
}
