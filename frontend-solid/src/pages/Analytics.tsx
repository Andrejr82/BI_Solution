import { createSignal, onMount, Show, createResource, For, createEffect } from 'solid-js';
import { BarChart3, TrendingUp, RefreshCw, Filter, X } from 'lucide-solid';
import api, { analyticsApi } from '../lib/api'; // Import analyticsApi
import { PlotlyChart } from '../components/PlotlyChart';
import { ChartDownloadButton } from '../components/ChartDownloadButton';

interface SalesAnalysis {
  vendas_por_categoria: Array<{
    categoria: string;
    vendas: number;
  }>;
  giro_estoque: Array<{
    produto: string;
    nome: string;
    giro: number;
  }>;
  distribuicao_abc: {
    A: number;
    B: number;
    C: number;
  };
}

interface FilterOptions {
  categorias: string[];
  segmentos: string[];
}

export default function Analytics() {
  const [data, setData] = createSignal<SalesAnalysis | null>(null);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal<string | null>(null);

  // Filtros
  const [categoria, setCategoria] = createSignal('');
  const [segmento, setSegmento] = createSignal('');

  // Carregar opções de filtro (segmentos e todas as categorias)
  const [allFilterOptions] = createResource<FilterOptions>(async () => {
    const response = await analyticsApi.getFilterOptions(); // Use analyticsApi
    return response.data;
  });

  // Carregar categorias filtradas por segmento
  const [filteredCategoryOptions] = createResource(() => segmento(), async (segmento) => {
    if (segmento === '') {
      return allFilterOptions()?.categorias || [];
    }
    const response = await analyticsApi.getFilterOptions({ segmento: segmento });
    return response.data.categorias;
  });

  // Efeito para resetar categoria quando o segmento muda
  createEffect(() => {
    // Apenas se o segmento realmente mudou e não é a inicialização
    if (segmento() !== undefined) {
      setCategoria('');
    }
  });


  // Chart specs
  const [vendasCategoriaChart, setVendasCategoriaChart] = createSignal<any>({});
  const [giroEstoqueChart, setGiroEstoqueChart] = createSignal<any>({});
  const [distribuicaoABCChart, setDistribuicaoABCChart] = createSignal<any>({});

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (categoria()) params.append('categoria', categoria());
      if (segmento()) params.append('segmento', segmento());

      const response = await api.get<SalesAnalysis>(`/analytics/sales-analysis?${params.toString()}`);
      setData(response.data);

      // Gerar gráficos
      generateCharts(response.data);
    } catch (err: any) {
      console.error('Erro ao carregar análise:', err);
      setError(err.response?.data?.detail || 'Erro ao carregar análise de vendas');
    } finally {
      setLoading(false);
    }
  };

  const generateCharts = (analysisData: SalesAnalysis) => {
    // 1. LOJAS CAÇULA - LIGHT THEME: Vendas por Categoria
    if (analysisData.vendas_por_categoria.length > 0) {
      const vendasSpec = {
        data: [{
          type: 'bar',
          x: analysisData.vendas_por_categoria.map(c => c.categoria),
          y: analysisData.vendas_por_categoria.map(c => c.vendas),
          marker: {
            color: '#8B7355', // Marrom Caçula
            line: { color: '#E5E5E5', width: 1 }
          },
          text: analysisData.vendas_por_categoria.map(c => c.vendas.toLocaleString()),
          textposition: 'outside',
          textfont: { color: '#2D2D2D', family: 'Inter, sans-serif' },
          hovertemplate: '<b>%{x}</b><br>Vendas: %{y:,}<extra></extra>'
        }],
        layout: {
          title: {
            text: 'Vendas por Categoria (Top 10)',
            font: { size: 16, color: '#2D2D2D', family: 'Inter, sans-serif' }
          },
          xaxis: {
            title: '',
            tickangle: -45,
            tickfont: { size: 10, color: '#6B6B6B', family: 'Inter, sans-serif' },
            gridcolor: '#E5E5E5',
            linecolor: '#E5E5E5'
          },
          yaxis: {
            title: 'Vendas (30 dias)',
            titlefont: { color: '#6B6B6B', family: 'Inter, sans-serif' },
            tickfont: { color: '#6B6B6B', family: 'Inter, sans-serif' },
            gridcolor: '#E5E5E5',
            linecolor: '#E5E5E5'
          },
          plot_bgcolor: '#FFFFFF',
          paper_bgcolor: '#FAFAFA',
          margin: { l: 60, r: 20, t: 60, b: 100 },
          font: { color: '#2D2D2D', family: 'Inter, sans-serif' }
        },
        config: { responsive: true }
      };
      setVendasCategoriaChart(vendasSpec);
    }

    // 2. LOJAS CAÇULA - LIGHT THEME: Giro de Estoque
    if (analysisData.giro_estoque.length > 0) {
      const giroSpec = {
        data: [{
          type: 'scatter',
          mode: 'lines+markers',
          x: analysisData.giro_estoque.map((_, i) => i + 1),
          y: analysisData.giro_estoque.map(p => p.giro),
          text: analysisData.giro_estoque.map(p => p.nome),
          marker: {
            color: '#2D7A3E', // Verde oliva
            size: 8
          },
          line: {
            color: '#6B7A5A', // Verde oliva claro
            width: 2
          },
          hovertemplate: '<b>%{text}</b><br>Giro: %{y:.2f}<extra></extra>'
        }],
        layout: {
          title: {
            text: 'Giro de Estoque (Top 15 Produtos)',
            font: { size: 16, color: '#2D2D2D', family: 'Inter, sans-serif' }
          },
          xaxis: {
            title: 'Ranking',
            titlefont: { color: '#6B6B6B', family: 'Inter, sans-serif' },
            tickfont: { color: '#6B6B6B', family: 'Inter, sans-serif' },
            gridcolor: '#E5E5E5',
            linecolor: '#E5E5E5'
          },
          yaxis: {
            title: 'Taxa de Giro',
            titlefont: { color: '#6B6B6B', family: 'Inter, sans-serif' },
            tickfont: { color: '#6B6B6B', family: 'Inter, sans-serif' },
            gridcolor: '#E5E5E5',
            linecolor: '#E5E5E5'
          },
          plot_bgcolor: '#FFFFFF',
          paper_bgcolor: '#FAFAFA',
          margin: { l: 60, r: 20, t: 60, b: 60 },
          font: { color: '#2D2D2D', family: 'Inter, sans-serif' }
        },
        config: { responsive: true }
      };
      setGiroEstoqueChart(giroSpec);
    }

    // 3. LOJAS CAÇULA - LIGHT THEME: Distribuição ABC
    const abc = analysisData.distribuicao_abc;
    if (abc.A + abc.B + abc.C > 0) {
      const abcSpec = {
        data: [{
          type: 'pie',
          labels: ['Classe A (20%)', 'Classe B (30%)', 'Classe C (50%)'],
          values: [abc.A, abc.B, abc.C],
          marker: {
            colors: ['#2D7A3E', '#C9A961', '#B94343'], // Verde success, Dourado, Vermelho terroso
            line: { color: '#FFFFFF', width: 2 }
          },
          textinfo: 'label+percent+value',
          textposition: 'inside',
          textfont: { size: 12, color: '#FFFFFF', family: 'Inter, sans-serif' },
          hovertemplate: '<b>%{label}</b><br>Produtos: %{value}<br>%{percent}<extra></extra>'
        }],
        layout: {
          title: {
            text: 'Distribuição ABC (Curva de Pareto)',
            font: { size: 16, color: '#2D2D2D', family: 'Inter, sans-serif' }
          },
          plot_bgcolor: '#FFFFFF',
          paper_bgcolor: '#FAFAFA',
          margin: { l: 20, r: 20, t: 60, b: 20 },
          font: { color: '#2D2D2D', family: 'Inter, sans-serif' },
          showlegend: true,
          legend: {
            orientation: 'h',
            x: 0.5,
            y: -0.1,
            xanchor: 'center',
            font: { size: 10, color: '#6B6B6B', family: 'Inter, sans-serif' },
            bgcolor: 'rgba(255,255,255,0.9)',
            bordercolor: '#E5E5E5',
            borderwidth: 1
          }
        },
        config: { responsive: true }
      };
      setDistribuicaoABCChart(abcSpec);
    }
  };

  onMount(() => {
    loadData();
  });

  return (
    <div class="flex flex-col h-full p-6 gap-6">
      {/* Header */}
      <div class="flex justify-between items-end">
        <div>
          <h2 class="text-2xl font-bold flex items-center gap-2">
            <BarChart3 size={28} />
            Analytics Avançado
          </h2>
          <p class="text-muted">Análise de vendas, estoque e distribuição ABC</p>
        </div>
        <button
          onClick={loadData}
          class="btn btn-outline gap-2"
          disabled={loading()}
        >
          <RefreshCw size={16} class={loading() ? 'animate-spin' : ''} />
          Atualizar
        </button>
      </div>

      {/* Filters */}
      <div class="card p-4 border">
        <div class="flex items-center gap-2 mb-3">
          <Filter size={20} />
          <h3 class="font-semibold">Filtros</h3>
          <Show when={categoria() || segmento()}>
            <button
              class="ml-auto text-sm text-muted hover:text-foreground flex items-center gap-1"
              onClick={() => {
                setCategoria('');
                setSegmento('');
                loadData();
              }}
            >
              <X size={16} />
              Limpar Filtros
            </button>
          </Show>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Segmento */}
          <select
            class="input"
            value={segmento()}
            onChange={(e) => setSegmento(e.currentTarget.value)}
            disabled={allFilterOptions.loading}
          >
            <option value="">Todos os Segmentos</option>
            <Show when={allFilterOptions()}>
              <For each={allFilterOptions()!.segmentos}>
                {(seg) => <option value={seg}>{seg}</option>}
              </For>
            </Show>
          </select>

          {/* Categoria (filtro dinâmico) */}
          <select
            class="input"
            value={categoria()}
            onChange={(e) => setCategoria(e.currentTarget.value)}
            disabled={filteredCategoryOptions.loading}
          >
            <option value="">Todas as Categorias</option>
            <Show when={filteredCategoryOptions()}>
              <For each={filteredCategoryOptions()}>
                {(cat) => <option value={cat}>{cat}</option>}
              </For>
            </Show>
          </select>

          <button
            class="btn btn-primary"
            onClick={loadData}
            disabled={loading()}
          >
            Aplicar Filtros
          </button>
        </div>

        {/* Active Filters Display */}
        <Show when={categoria() || segmento()}>
          <div class="flex gap-2 mt-3 flex-wrap">
            <span class="text-sm text-muted">Filtros ativos:</span>
            <Show when={segmento()}>
              <span class="px-2 py-1 bg-primary/20 text-primary rounded text-sm flex items-center gap-1">
                Segmento: {segmento()}
                <button
                  onClick={() => {
                    setSegmento('');
                    loadData();
                  }}
                  class="hover:bg-primary/30 rounded"
                >
                  <X size={14} />
                </button>
              </span>
            </Show>
            <Show when={categoria()}>
              <span class="px-2 py-1 bg-primary/20 text-primary rounded text-sm flex items-center gap-1">
                Categoria: {categoria()}
                <button
                  onClick={() => {
                    setCategoria('');
                    loadData();
                  }}
                  class="hover:bg-primary/30 rounded"
                >
                  <X size={14} />
                </button>
              </span>
            </Show>
          </div>
        </Show>
      </div>

      {/* Error State */}
      <Show when={error()}>
        <div class="card p-4 border-red-500 bg-red-500/10">
          <p class="text-red-500">{error()}</p>
        </div>
      </Show>

      {/* Loading State */}
      <Show when={loading()}>
        <div class="flex-1 flex items-center justify-center">
          <div class="text-center">
            <BarChart3 size={48} class="mx-auto mb-4 opacity-50 animate-pulse" />
            <p class="text-muted">Carregando análise...</p>
          </div>
        </div>
      </Show>

      {/* Charts Grid */}
      <Show when={!loading() && data()}>
        <div class="space-y-6">
          {/* Row 1: Vendas por Categoria */}
          <div class="card p-6 border">
            <div class="flex justify-between items-center mb-4">
              <h3 class="font-semibold">Vendas por Categoria (Top 10)</h3>
              <ChartDownloadButton
                chartId="analytics-vendas-categoria-chart"
                filename="analytics_vendas_categoria"
                label="Baixar"
              />
            </div>
            <Show
              when={data()!.vendas_por_categoria.length > 0}
              fallback={
                <div class="h-[400px] flex items-center justify-center text-muted">
                  <p>Nenhum dado de vendas por categoria disponível</p>
                </div>
              }
            >
              <PlotlyChart
                chartSpec={vendasCategoriaChart}
                chartId="analytics-vendas-categoria-chart"
                enableDownload={true}
              />
            </Show>
          </div>

          {/* Row 2: Two columns */}
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Giro de Estoque */}
            <div class="card p-6 border">
              <div class="flex justify-between items-center mb-4">
                <h3 class="font-semibold">Giro de Estoque (Top 15)</h3>
                <ChartDownloadButton
                  chartId="analytics-giro-estoque-chart"
                  filename="analytics_giro_estoque"
                  label="Baixar"
                />
              </div>
              <Show
                when={data()!.giro_estoque.length > 0}
                fallback={
                  <div class="h-[400px] flex items-center justify-center text-muted">
                    <p>Nenhum dado de giro de estoque disponível</p>
                  </div>
                }
              >
                <PlotlyChart
                  chartSpec={giroEstoqueChart}
                  chartId="analytics-giro-estoque-chart"
                  enableDownload={true}
                />
              </Show>
            </div>

            {/* Distribuição ABC */}
            <div class="card p-6 border">
              <div class="flex justify-between items-center mb-4">
                <h3 class="font-semibold">Distribuição ABC (Curva de Pareto)</h3>
                <ChartDownloadButton
                  chartId="analytics-abc-chart"
                  filename="analytics_distribuicao_abc"
                  label="Baixar"
                />
              </div>
              <Show
                when={(data()!.distribuicao_abc.A + data()!.distribuicao_abc.B + data()!.distribuicao_abc.C) > 0}
                fallback={
                  <div class="h-[400px] flex items-center justify-center text-muted">
                    <p>Nenhum dado de distribuição ABC disponível</p>
                  </div>
                }
              >
                <PlotlyChart
                  chartSpec={distribuicaoABCChart}
                  chartId="analytics-abc-chart"
                  enableDownload={true}
                />
              </Show>
            </div>
          </div>

          {/* Info Box */}
          <div class="card p-4 border bg-blue-500/5 border-blue-500/30">
            <div class="text-sm">
              <strong>📊 Sobre a Curva ABC:</strong> A classificação ABC segue o princípio de Pareto (80/20):
              <ul class="list-disc list-inside mt-2 space-y-1 text-muted">
                <li><strong class="text-green-500">Classe A (20%):</strong> Produtos de alto valor/rotatividade - prioridade máxima</li>
                <li><strong class="text-yellow-500">Classe B (30%):</strong> Produtos de valor/rotatividade média</li>
                <li><strong class="text-red-500">Classe C (50%):</strong> Produtos de baixo valor/rotatividade</li>
              </ul>
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
}
