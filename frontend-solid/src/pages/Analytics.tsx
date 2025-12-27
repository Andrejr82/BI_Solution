import { createSignal, onMount, Show, createResource, For, createEffect } from 'solid-js';
import { BarChart3, TrendingUp, RefreshCw, Filter, X, Download, Eye } from 'lucide-solid';
import api, { analyticsApi, ABCDetailItem } from '../lib/api'; // Import analyticsApi and ABCDetailItem
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
    detalhes: Array<{
      PRODUTO: number;
      NOME: string;
      receita: number;
      perc_acumulada: number;
      classe: string;
    }>;
    receita_por_classe?: Record<string, number>;
  };
}

interface FilterOptions {
  categorias: string[];
  segmentos: string[];
  grupos: string[];
}

export default function Analytics() {
  const [data, setData] = createSignal<SalesAnalysis | null>(null);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal<string | null>(null);

  // Filtros
  const [categoria, setCategoria] = createSignal('');
  const [segmento, setSegmento] = createSignal('');
  const [grupo, setGrupo] = createSignal('');

  // Modal ABC Details
  const [showABCModal, setShowABCModal] = createSignal(false);
  const [selectedClasse, setSelectedClasse] = createSignal<'A' | 'B' | 'C' | null>(null);
  const [abcDetails, setAbcDetails] = createSignal<ABCDetailItem[]>([]);
  const [loadingABC, setLoadingABC] = createSignal(false);

  // Carregar opções de filtro (segmentos e todas as categorias)
  const [allFilterOptions] = createResource<FilterOptions>(async () => {
    const response = await analyticsApi.getFilterOptions();
    return response.data;
  });

  // Carregar categorias filtradas por segmento
  const [filteredCategoryOptions] = createResource(() => segmento(), async (seg) => {
    if (seg === '') {
      return allFilterOptions()?.categorias || [];
    }
    const response = await analyticsApi.getFilterOptions(seg);
    return response.data.categorias;
  });

  // Carregar grupos filtrados por segmento e categoria
  const [filteredGroupOptions] = createResource(() => ({ seg: segmento(), cat: categoria() }), async ({ seg, cat }) => {
    if (seg === '' && cat === '') {
      return allFilterOptions()?.grupos || [];
    }
    const response = await analyticsApi.getFilterOptions(seg || undefined, cat || undefined);
    return response.data.grupos;
  });

  // Efeito para resetar categoria quando o segmento muda
  createEffect(() => {
    if (segmento() !== undefined) {
      setCategoria('');
      setGrupo('');
    }
  });

  // Efeito para resetar grupo quando a categoria muda
  createEffect(() => {
    if (categoria() !== undefined) {
      setGrupo('');
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
      if (grupo()) params.append('grupo', grupo());

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

  // Carregar detalhes ABC ao clicar em uma classe
  const handleABCClick = async (classe: 'A' | 'B' | 'C') => {
    setSelectedClasse(classe);
    setShowABCModal(true);
    setLoadingABC(true);

    try {
      const response = await analyticsApi.getABCDetails(
        classe,
        segmento() || undefined,
        categoria() || undefined,
        grupo() || undefined
      );
      setAbcDetails(response.data);
    } catch (err: any) {
      console.error('Erro ao carregar detalhes ABC:', err);
      setAbcDetails([]);
    } finally {
      setLoadingABC(false);
    }
  };

  // Download CSV dos SKUs
  const downloadABCCSV = () => {
    const details = abcDetails();
    if (details.length === 0) return;

    const headers = ['PRODUTO', 'NOME', 'UNE', 'UNE_NOME', 'RECEITA', 'PERC_ACUMULADA', 'CLASSE'];
    const rows = details.map(item => [
      item.PRODUTO,
      item.NOME,
      item.UNE,
      item.UNE_NOME || '',
      item.receita.toFixed(2),
      item.perc_acumulada.toFixed(2),
      item.classe
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `abc_classe_${selectedClasse()}_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
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

    // 3. LOJAS CAÇULA - GRÁFICO DE PARETO REAL (ABC)
    const abc = analysisData.distribuicao_abc;
    if (abc.detalhes && abc.detalhes.length > 0) {
      const paretoSpec = {
        data: [
          {
            type: 'bar',
            x: abc.detalhes.map(p => p.NOME.substring(0, 20)),
            y: abc.detalhes.map(p => p.receita),
            name: 'Faturamento (R$)',
            marker: {
              color: abc.detalhes.map(p => 
                p.classe === 'A' ? '#166534' : (p.classe === 'B' ? '#CA8A04' : '#991B1B')
              ),
              line: { color: '#FFFFFF', width: 1 },
              opacity: 0.9
            },
            hovertemplate: '<b>%{x}</b><br>Receita: R$ %{y:,.2f}<br>Classe: %{customdata}<extra></extra>',
            customdata: abc.detalhes.map(p => p.classe)
          },
          {
            type: 'scatter',
            mode: 'lines+markers',
            x: abc.detalhes.map(p => p.NOME.substring(0, 20)),
            y: abc.detalhes.map(p => p.perc_acumulada),
            name: '% Acumulada',
            yaxis: 'y2',
            line: { color: '#1E293B', width: 3, shape: 'spline' },
            marker: { 
              color: '#1E293B', 
              size: 8,
              symbol: 'diamond'
            },
            hovertemplate: 'Contribuição Acumulada: %{y:.1f}%<extra></extra>'
          }
        ],
        layout: {
          title: {
            text: '<b>Curva de Pareto: Onde está o seu faturamento?</b><br><span style="font-size:12px;color:#64748B">A análise identifica os 20% de produtos que geram 80% do lucro</span>',
            font: { size: 18, color: '#0F172A', family: 'Inter, sans-serif' },
            x: 0.05
          },
          xaxis: {
            tickangle: -45,
            tickfont: { size: 10, color: '#475569', font: { weight: 'bold' } },
            gridcolor: '#F1F5F9'
          },
          yaxis: {
            title: 'Receita Individual (R$)',
            titlefont: { size: 12, color: '#64748B', font: { weight: 'bold' } },
            gridcolor: '#F1F5F9',
            zeroline: false
          },
          yaxis2: {
            title: '% Contribuição Acumulada',
            titlefont: { size: 12, color: '#64748B', font: { weight: 'bold' } },
            overlaying: 'y',
            side: 'right',
            range: [0, 105],
            showgrid: false,
            tickvals: [0, 20, 40, 60, 80, 95, 100],
            ticktext: ['0%', '20%', '40%', '60%', '80%', '95%', '100%'],
            tickfont: { size: 10, color: '#1E293B', font: { weight: 'bold' } }
          },
          legend: { 
            orientation: 'h', 
            x: 0.5, 
            y: -0.25, 
            xanchor: 'center',
            bgcolor: 'rgba(255,255,255,0.7)',
            bordercolor: '#E2E8F0',
            borderwidth: 1
          },
          plot_bgcolor: '#FFFFFF',
          paper_bgcolor: '#FAFAFA',
          margin: { l: 70, r: 70, t: 90, b: 130 },
          shapes: [
            // Linha de Corte de Pareto (80%)
            {
              type: 'line',
              xref: 'paper', yref: 'y2',
              x0: 0, x1: 1, y0: 80, y1: 80,
              line: { color: '#166534', width: 2, dash: 'dashdot' }
            },
            // Anotação "Vital Few"
            {
              type: 'rect',
              xref: 'paper', yref: 'paper',
              x0: 0, x1: 0.2, y0: 0.8, y1: 1,
              fillcolor: 'rgba(22, 101, 52, 0.05)',
              line: { width: 0 }
            }
          ],
          annotations: [
            {
              xref: 'paper', yref: 'y2',
              x: 0.02, y: 85,
              text: 'ZONA VITAL (80%)',
              showarrow: false,
              font: { color: '#166534', size: 10, weight: 'bold' }
            }
          ]
        },
        config: { responsive: true, displayModeBar: false }
      };
      setDistribuicaoABCChart(paretoSpec);
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
          <Show when={categoria() || segmento() || grupo()}>
            <button
              class="ml-auto text-sm text-muted hover:text-foreground flex items-center gap-1"
              onClick={() => {
                setCategoria('');
                setSegmento('');
                setGrupo('');
                loadData();
              }}
            >
              <X size={16} />
              Limpar Filtros
            </button>
          </Show>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
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

          {/* Grupo (filtro dinâmico) */}
          <select
            class="input"
            value={grupo()}
            onChange={(e) => setGrupo(e.currentTarget.value)}
            disabled={filteredGroupOptions.loading}
          >
            <option value="">Todos os Grupos</option>
            <Show when={filteredGroupOptions()}>
              <For each={filteredGroupOptions()}>
                {(grp) => <option value={grp}>{grp}</option>}
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
        <Show when={categoria() || segmento() || grupo()}>
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
            <Show when={grupo()}>
              <span class="px-2 py-1 bg-primary/20 text-primary rounded text-sm flex items-center gap-1">
                Grupo: {grupo()}
                <button
                  onClick={() => {
                    setGrupo('');
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
                <h3 class="font-semibold">Análise de Pareto (ABC por Receita)</h3>
                <ChartDownloadButton
                  chartId="analytics-abc-chart"
                  filename="analytics_distribuicao_abc"
                  label="Baixar"
                />
              </div>
              <Show
                when={data()!.distribuicao_abc.detalhes && data()!.distribuicao_abc.detalhes.length > 0}
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

              {/* Summary of ABC classes - CLICKABLE */}
              <Show when={data()!.distribuicao_abc.receita_por_classe}>
                <div class="grid grid-cols-3 gap-2 mt-4">
                  <button
                    onClick={() => handleABCClick('A')}
                    class="p-2 rounded bg-green-500/10 border border-green-500/20 text-center hover:bg-green-500/20 transition-colors cursor-pointer group"
                  >
                    <p class="text-[10px] text-green-700 font-bold uppercase">Classe A</p>
                    <p class="text-sm font-bold">{data()!.distribuicao_abc.A} SKUs</p>
                    <p class="text-[10px] text-muted-foreground">80% da Receita</p>
                    <p class="text-[9px] text-green-600 mt-1 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1">
                      <Eye size={10} /> Clique para detalhes
                    </p>
                  </button>
                  <button
                    onClick={() => handleABCClick('B')}
                    class="p-2 rounded bg-yellow-500/10 border border-yellow-500/20 text-center hover:bg-yellow-500/20 transition-colors cursor-pointer group"
                  >
                    <p class="text-[10px] text-yellow-700 font-bold uppercase">Classe B</p>
                    <p class="text-sm font-bold">{data()!.distribuicao_abc.B} SKUs</p>
                    <p class="text-[10px] text-muted-foreground">15% da Receita</p>
                    <p class="text-[9px] text-yellow-600 mt-1 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1">
                      <Eye size={10} /> Clique para detalhes
                    </p>
                  </button>
                  <button
                    onClick={() => handleABCClick('C')}
                    class="p-2 rounded bg-red-500/10 border border-red-500/20 text-center hover:bg-red-500/20 transition-colors cursor-pointer group"
                  >
                    <p class="text-[10px] text-red-700 font-bold uppercase">Classe C</p>
                    <p class="text-sm font-bold">{data()!.distribuicao_abc.C} SKUs</p>
                    <p class="text-[10px] text-muted-foreground">5% da Receita</p>
                    <p class="text-[9px] text-red-600 mt-1 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1">
                      <Eye size={10} /> Clique para detalhes
                    </p>
                  </button>
                </div>
              </Show>
            </div>
          </div>

          {/* Info Box */}
          <div class="card p-6 border bg-zinc-50 dark:bg-zinc-900/50">
            <div class="flex items-start gap-4">
              <div class="p-3 bg-primary/10 rounded-full text-primary">
                <BarChart3 size={24} />
              </div>
              <div>
                <h4 class="font-bold text-lg mb-2">Entendendo sua Curva ABC (Princípio de Pareto)</h4>
                <p class="text-sm text-muted-foreground leading-relaxed">
                  Diferente de uma análise simplista, sua Curva ABC é calculada com base na <strong>contribuição financeira real</strong> (Receita) de cada produto. 
                  Isso permite identificar onde o seu capital está gerando mais retorno:
                </p>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
                  <div class="space-y-2">
                    <div class="flex items-center gap-2">
                      <div class="w-3 h-3 rounded-full bg-green-500"></div>
                      <span class="font-bold text-sm">Classe A (Críticos)</span>
                    </div>
                    <p class="text-xs text-muted-foreground">
                      Representam os primeiros <strong>80% da sua receita</strong>. Geralmente são poucos produtos (aprox. 20%) que sustentam o negócio. <strong>Ruptura aqui é inaceitável.</strong>
                    </p>
                  </div>
                  <div class="space-y-2">
                    <div class="flex items-center gap-2">
                      <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
                      <span class="font-bold text-sm">Classe B (Estratégicos)</span>
                    </div>
                    <p class="text-xs text-muted-foreground">
                      Representam os próximos <strong>15% da receita</strong>. São produtos importantes que complementam o mix e possuem giro moderado.
                    </p>
                  </div>
                  <div class="space-y-2">
                    <div class="flex items-center gap-2">
                      <div class="w-3 h-3 rounded-full bg-red-500"></div>
                      <span class="font-bold text-sm">Classe C (Cauda Longa)</span>
                    </div>
                    <p class="text-xs text-muted-foreground">
                      Representam os <strong>5% finais da receita</strong>. Costumam ser a grande maioria dos produtos (aprox. 50% do mix). Devem ter estoque mínimo para não imobilizar capital.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Show>

      {/* Modal ABC Details */}
      <Show when={showABCModal()}>
        <div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setShowABCModal(false)}>
          <div class="bg-background rounded-lg shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div class="flex justify-between items-center p-6 border-b">
              <div>
                <h3 class="text-xl font-bold flex items-center gap-2">
                  <span class={`inline-block w-3 h-3 rounded-full ${
                    selectedClasse() === 'A' ? 'bg-green-500' :
                    selectedClasse() === 'B' ? 'bg-yellow-500' : 'bg-red-500'
                  }`}></span>
                  SKUs da Classe {selectedClasse()}
                </h3>
                <p class="text-sm text-muted-foreground mt-1">
                  {abcDetails().length} produtos encontrados
                </p>
              </div>
              <div class="flex gap-2">
                <button
                  onClick={downloadABCCSV}
                  class="btn btn-outline gap-2"
                  disabled={abcDetails().length === 0}
                >
                  <Download size={16} />
                  Baixar CSV
                </button>
                <button
                  onClick={() => setShowABCModal(false)}
                  class="btn btn-outline"
                >
                  <X size={16} />
                </button>
              </div>
            </div>

            {/* Content */}
            <div class="overflow-y-auto max-h-[calc(90vh-140px)]">
              <Show when={loadingABC()}>
                <div class="flex items-center justify-center py-12">
                  <RefreshCw class="animate-spin mr-2" size={24} />
                  <span>Carregando detalhes...</span>
                </div>
              </Show>

              <Show when={!loadingABC() && abcDetails().length === 0}>
                <div class="flex items-center justify-center py-12 text-muted-foreground">
                  Nenhum produto encontrado para esta classe.
                </div>
              </Show>

              <Show when={!loadingABC() && abcDetails().length > 0}>
                <table class="w-full">
                  <thead class="sticky top-0 bg-secondary border-b">
                    <tr>
                      <th class="text-left p-3 text-xs font-semibold uppercase">Produto</th>
                      <th class="text-left p-3 text-xs font-semibold uppercase">Nome</th>
                      <th class="text-left p-3 text-xs font-semibold uppercase">UNE</th>
                      <th class="text-left p-3 text-xs font-semibold uppercase">Loja</th>
                      <th class="text-right p-3 text-xs font-semibold uppercase">Receita</th>
                      <th class="text-right p-3 text-xs font-semibold uppercase">% Acumulada</th>
                    </tr>
                  </thead>
                  <tbody>
                    <For each={abcDetails()}>
                      {(item) => (
                        <tr class="border-b hover:bg-secondary/50 transition-colors">
                          <td class="p-3 font-mono text-sm">{item.PRODUTO}</td>
                          <td class="p-3 text-sm">{item.NOME}</td>
                          <td class="p-3 font-mono text-sm">{item.UNE}</td>
                          <td class="p-3 text-sm text-muted-foreground">{item.UNE_NOME || '-'}</td>
                          <td class="p-3 text-sm text-right font-medium">
                            R$ {item.receita.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </td>
                          <td class="p-3 text-sm text-right">
                            {item.perc_acumulada.toFixed(2)}%
                          </td>
                        </tr>
                      )}
                    </For>
                  </tbody>
                </table>
              </Show>
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
}
