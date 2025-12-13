import { createSignal, onMount, Show, For } from 'solid-js';
import { rupturasApi, Ruptura, RupturasSummary } from '@/lib/api';
import { AlertTriangle, RefreshCw, PackageX, ShoppingCart, Archive, Download, Filter, X, TrendingUp, Package, BarChart3, PieChart } from 'lucide-solid';
import { PlotlyChart } from '@/components/PlotlyChart';
import { ChartDownloadButton } from '@/components/ChartDownloadButton';

export default function Rupturas() {
  const [data, setData] = createSignal<Ruptura[]>([]);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal<string | null>(null);
  const [summary, setSummary] = createSignal<RupturasSummary>({ total: 0, criticos: 0, valor_estimado: 0 });

  // Chart specs
  const [criticidadeChart, setCriticidadeChart] = createSignal<any>({});
  const [topRupturasChart, setTopRupturasChart] = createSignal<any>({});
  const [necessidadeSegmentoChart, setNecessidadeSegmentoChart] = createSignal<any>({});
  const [selectedProduct, setSelectedProduct] = createSignal<Ruptura | null>(null);

  // Filtros
  const [segmentos, setSegmentos] = createSignal<string[]>([]);
  const [unes, setUnes] = createSignal<string[]>([]);
  const [selectedSegmento, setSelectedSegmento] = createSignal<string>('');
  const [selectedUne, setSelectedUne] = createSignal<string>('');
  const [showFilters, setShowFilters] = createSignal(false);
  const [filtersLoading, setFiltersLoading] = createSignal(false);

  const loadFilters = async () => {
    setFiltersLoading(true);
    try {
      const [segmentosRes, unesRes] = await Promise.all([
        rupturasApi.getSegmentos(),
        rupturasApi.getUnes()
      ]);
      setSegmentos(Array.isArray(segmentosRes.data) ? segmentosRes.data : []);
      setUnes(Array.isArray(unesRes.data) ? unesRes.data : []);
    } catch (err) {
      console.error("Error loading filters:", err);
      setSegmentos([]);
      setUnes([]);
    } finally {
      setFiltersLoading(false);
    }
  };

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const segmento = selectedSegmento() || undefined;
      const une = selectedUne() || undefined;

      const [rupturaRes, summaryRes] = await Promise.all([
        rupturasApi.getCritical(50, segmento, une),
        rupturasApi.getSummary(segmento, une)
      ]);

      setData(rupturaRes.data);
      setSummary(summaryRes.data);

      // Gerar gráficos
      generateCharts(rupturaRes.data);
    } catch (err: any) {
      console.error("Error loading rupturas:", err);
      setError("Falha ao carregar rupturas críticas.");
    } finally {
      setLoading(false);
    }
  };

  const generateCharts = (rupturas: Ruptura[]) => {
    if (rupturas.length === 0) return;

    // 1. Gráfico de Pizza - Distribuição de Criticidade
    const criticidade = {
      critico: rupturas.filter(r => r.CRITICIDADE_PCT >= 75).length,
      alto: rupturas.filter(r => r.CRITICIDADE_PCT >= 50 && r.CRITICIDADE_PCT < 75).length,
      medio: rupturas.filter(r => r.CRITICIDADE_PCT >= 25 && r.CRITICIDADE_PCT < 50).length,
      baixo: rupturas.filter(r => r.CRITICIDADE_PCT < 25).length
    };

    setCriticidadeChart({
      data: [{
        type: 'pie',
        labels: ['CRÍTICO (≥75%)', 'ALTO (50-75%)', 'MÉDIO (25-50%)', 'BAIXO (<25%)'],
        values: [criticidade.critico, criticidade.alto, criticidade.medio, criticidade.baixo],
        marker: {
          colors: ['#ef4444', '#f97316', '#f59e0b', '#3b82f6']
        },
        textinfo: 'label+value+percent',
        textposition: 'inside',
        textfont: { size: 11, color: '#ffffff' },
        hovertemplate: '<b>%{label}</b><br>Produtos: %{value}<br>%{percent}<extra></extra>'
      }],
      layout: {
        title: {
          text: 'Distribuição por Criticidade',
          font: { size: 16, color: '#e5e7eb' }
        },
        plot_bgcolor: '#1f2937',
        paper_bgcolor: '#1f2937',
        margin: { l: 20, r: 20, t: 60, b: 20 },
        font: { color: '#e5e7eb' },
        showlegend: false
      },
      config: { responsive: true }
    });

    // 2. Gráfico de Barras - Top 10 Produtos em Ruptura
    const top10 = rupturas
      .sort((a, b) => b.NECESSIDADE - a.NECESSIDADE)
      .slice(0, 10);

    setTopRupturasChart({
      data: [{
        type: 'bar',
        x: top10.map(r => r.NOME.substring(0, 30) + '...'),
        y: top10.map(r => r.NECESSIDADE),
        marker: {
          color: top10.map(r => {
            if (r.CRITICIDADE_PCT >= 75) return '#ef4444';
            if (r.CRITICIDADE_PCT >= 50) return '#f97316';
            if (r.CRITICIDADE_PCT >= 25) return '#f59e0b';
            return '#3b82f6';
          }),
          line: { color: '#1e40af', width: 1 }
        },
        text: top10.map(r => Math.round(r.NECESSIDADE)),
        textposition: 'outside',
        hovertemplate: '<b>%{x}</b><br>Necessidade: %{y:.0f} un<br>Código: ' +
          top10.map(r => r.PRODUTO).join('<br>Código: ') + '<extra></extra>',
        customdata: top10.map(r => r.PRODUTO)
      }],
      layout: {
        title: {
          text: 'Top 10 Produtos - Maior Necessidade',
          font: { size: 16, color: '#e5e7eb' }
        },
        xaxis: {
          title: '',
          tickangle: -45,
          tickfont: { size: 9, color: '#9ca3af' },
          gridcolor: '#374151'
        },
        yaxis: {
          title: 'Necessidade (unidades)',
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
    });

    // 3. Gráfico de Barras Empilhadas - Necessidade por Segmento
    const segmentoData: { [key: string]: { critico: number, alto: number, medio: number, baixo: number } } = {};

    rupturas.forEach(r => {
      const seg = r.NOMESEGMENTO || 'SEM SEGMENTO';
      if (!segmentoData[seg]) {
        segmentoData[seg] = { critico: 0, alto: 0, medio: 0, baixo: 0 };
      }

      const necessidade = r.NECESSIDADE;
      if (r.CRITICIDADE_PCT >= 75) segmentoData[seg].critico += necessidade;
      else if (r.CRITICIDADE_PCT >= 50) segmentoData[seg].alto += necessidade;
      else if (r.CRITICIDADE_PCT >= 25) segmentoData[seg].medio += necessidade;
      else segmentoData[seg].baixo += necessidade;
    });

    const segmentos = Object.keys(segmentoData);

    setNecessidadeSegmentoChart({
      data: [
        {
          type: 'bar',
          name: 'CRÍTICO',
          x: segmentos,
          y: segmentos.map(s => segmentoData[s].critico),
          marker: { color: '#ef4444' },
          hovertemplate: '<b>%{x}</b><br>Crítico: %{y:.0f} un<extra></extra>'
        },
        {
          type: 'bar',
          name: 'ALTO',
          x: segmentos,
          y: segmentos.map(s => segmentoData[s].alto),
          marker: { color: '#f97316' },
          hovertemplate: '<b>%{x}</b><br>Alto: %{y:.0f} un<extra></extra>'
        },
        {
          type: 'bar',
          name: 'MÉDIO',
          x: segmentos,
          y: segmentos.map(s => segmentoData[s].medio),
          marker: { color: '#f59e0b' },
          hovertemplate: '<b>%{x}</b><br>Médio: %{y:.0f} un<extra></extra>'
        },
        {
          type: 'bar',
          name: 'BAIXO',
          x: segmentos,
          y: segmentos.map(s => segmentoData[s].baixo),
          marker: { color: '#3b82f6' },
          hovertemplate: '<b>%{x}</b><br>Baixo: %{y:.0f} un<extra></extra>'
        }
      ],
      layout: {
        title: {
          text: 'Necessidade por Segmento e Criticidade',
          font: { size: 16, color: '#e5e7eb' }
        },
        barmode: 'stack',
        xaxis: {
          title: '',
          tickangle: -45,
          tickfont: { size: 10, color: '#9ca3af' },
          gridcolor: '#374151'
        },
        yaxis: {
          title: 'Necessidade Total (unidades)',
          titlefont: { color: '#9ca3af' },
          tickfont: { color: '#9ca3af' },
          gridcolor: '#374151'
        },
        plot_bgcolor: '#1f2937',
        paper_bgcolor: '#1f2937',
        margin: { l: 60, r: 20, t: 60, b: 100 },
        font: { color: '#e5e7eb' },
        showlegend: true,
        legend: {
          orientation: 'h',
          x: 0.5,
          y: 1.1,
          xanchor: 'center',
          font: { size: 10, color: '#9ca3af' }
        }
      },
      config: { responsive: true }
    });
  };

  const handleChartClick = (clickData: any) => {
    if (clickData && clickData.points && clickData.points[0]) {
      const point = clickData.points[0];
      // Se tem customdata, é o código do produto
      if (point.customdata) {
        const produto = data().find(r => r.PRODUTO === point.customdata);
        if (produto) {
          setSelectedProduct(produto);
        }
      }
    }
  };

  const clearFilters = () => {
    setSelectedSegmento('');
    setSelectedUne('');
    loadData();
  };

  const exportCSV = () => {
    const items = data();
    if (items.length === 0) return;

    const headers = ['Produto', 'Nome', 'UNE', 'Segmento', 'Venda 30d', 'Estoque UNE', 'Estoque CD', 'Linha Verde', 'Criticidade %', 'Necessidade'];
    const rows = items.map(item => [
      item.PRODUTO,
      item.NOME,
      item.UNE,
      item.NOMESEGMENTO || '',
      item.VENDA_30DD,
      item.ESTOQUE_UNE,
      item.ESTOQUE_CD,
      item.ESTOQUE_LV,
      item.CRITICIDADE_PCT.toFixed(1),
      item.NECESSIDADE
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rupturas_criticas_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  onMount(() => {
    loadFilters();
    loadData();
  });

  const getCriticidadeColor = (pct: number) => {
    if (pct >= 75) return 'bg-red-500/20 text-red-500 border-red-500/30';
    if (pct >= 50) return 'bg-orange-500/20 text-orange-500 border-orange-500/30';
    if (pct >= 25) return 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30';
    return 'bg-blue-500/20 text-blue-500 border-blue-500/30';
  };

  const getCriticidadeLabel = (pct: number) => {
    if (pct >= 75) return 'CRÍTICO';
    if (pct >= 50) return 'ALTO';
    if (pct >= 25) return 'MÉDIO';
    return 'BAIXO';
  };

  return (
    <div class="flex flex-col h-full p-6 gap-6 max-w-7xl mx-auto">
      {/* Header */}
      <div class="flex justify-between items-start">
        <div>
          <h2 class="text-2xl font-bold tracking-tight text-red-500 flex items-center gap-2">
            <AlertTriangle size={24} />
            Rupturas Críticas
          </h2>
          <p class="text-muted mt-1">CD zerado + Estoque loja abaixo da Linha Verde</p>
        </div>
        <div class="flex gap-2">
          <button onClick={() => {
            console.log("Toggling filters:", !showFilters());
            setShowFilters(!showFilters());
          }} class="btn btn-outline gap-2">
            <Filter size={16} />
            Filtros
          </button>
          <button onClick={exportCSV} class="btn btn-outline gap-2" disabled={data().length === 0}>
            <Download size={16} />
            Exportar CSV
          </button>
          <button onClick={loadData} class="btn btn-outline gap-2" disabled={loading()}>
            <RefreshCw size={16} class={loading() ? 'animate-spin' : ''} />
            Atualizar
          </button>
        </div>
      </div>

      {/* Filtros */}
      <Show when={showFilters()}>
        <div class="p-4 bg-card border rounded-lg">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-semibold">Filtros</h3>
            <button onClick={() => setShowFilters(false)} class="text-muted-foreground hover:text-foreground">
              <X size={18} />
            </button>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium mb-2">Segmento</label>
              <select
                class="w-full px-3 py-2 bg-background border rounded-lg disabled:opacity-50"
                value={selectedSegmento()}
                onChange={(e) => setSelectedSegmento(e.target.value)}
                disabled={filtersLoading()}
              >
                <Show when={!filtersLoading()} fallback={<option>Carregando filtros...</option>}>
                  <option value="">Todos</option>
                  <For each={segmentos()} fallback={<option disabled>Nenhum segmento disponível</option>}>
                    {(seg) => <option value={seg}>{seg}</option>}
                  </For>
                </Show>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-2">UNE</label>
              <select
                class="w-full px-3 py-2 bg-background border rounded-lg disabled:opacity-50"
                value={selectedUne()}
                onChange={(e) => setSelectedUne(e.target.value)}
                disabled={filtersLoading()}
              >
                <Show when={!filtersLoading()} fallback={<option>Carregando filtros...</option>}>
                  <option value="">Todas</option>
                  <For each={unes()} fallback={<option disabled>Nenhuma UNE disponível</option>}>
                    {(une) => <option value={une}>{une}</option>}
                  </For>
                </Show>
              </select>
            </div>
            <div class="flex items-end gap-2">
              <button onClick={loadData} class="btn btn-primary flex-1">
                Aplicar Filtros
              </button>
              <button onClick={clearFilters} class="btn btn-outline">
                <X size={16} />
              </button>
            </div>
          </div>
        </div>
      </Show>

      {/* Resumo de Métricas */}
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="p-4 bg-card border rounded-lg">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-red-500/10 rounded-lg">
              <PackageX size={24} class="text-red-500" />
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Total de Rupturas</p>
              <p class="text-2xl font-bold">{summary().total}</p>
            </div>
          </div>
        </div>
        <div class="p-4 bg-card border rounded-lg">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-orange-500/10 rounded-lg">
              <AlertTriangle size={24} class="text-orange-500" />
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Criticidade Alta (≥75%)</p>
              <p class="text-2xl font-bold">{summary().criticos}</p>
            </div>
          </div>
        </div>
        <div class="p-4 bg-card border rounded-lg">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-blue-500/10 rounded-lg">
              <TrendingUp size={24} class="text-blue-500" />
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Taxa Crítica</p>
              <p class="text-2xl font-bold">
                {summary().total > 0 ? ((summary().criticos / summary().total) * 100).toFixed(0) : 0}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Explicação */}
      <div class="p-4 bg-blue-500/5 border border-blue-500/20 rounded-lg">
        <h3 class="font-semibold text-blue-500 mb-2">O que é Ruptura Crítica?</h3>
        <p class="text-sm text-muted-foreground">
          Produtos com <strong>estoque no CD zerado (ESTOQUE_CD = 0)</strong> e <strong>estoque da loja abaixo da Linha Verde (ESTOQUE_UNE &lt; ESTOQUE_LV)</strong> que tiveram vendas nos últimos 30 dias. A criticidade é calculada pela razão entre vendas e linha verde.
        </p>
      </div>

      {/* Gráficos Interativos */}
      <Show when={!loading() && data().length > 0}>
        <div class="space-y-6">
          {/* Primeira linha - 2 colunas */}
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Gráfico de Pizza - Criticidade */}
            <div class="card p-6 border">
              <div class="flex justify-between items-center mb-4">
                <h3 class="font-semibold flex items-center gap-2">
                  <PieChart size={20} class="text-blue-500" />
                  Distribuição de Criticidade
                </h3>
                <ChartDownloadButton
                  chartId="criticidade-chart"
                  filename="rupturas_criticidade"
                  label="Baixar"
                />
              </div>
              <PlotlyChart
                chartSpec={criticidadeChart}
                chartId="criticidade-chart"
                enableDownload={true}
                height="350px"
              />
            </div>

            {/* Gráfico de Barras - Top 10 */}
            <div class="card p-6 border">
              <div class="flex justify-between items-center mb-4">
                <h3 class="font-semibold flex items-center gap-2">
                  <BarChart3 size={20} class="text-orange-500" />
                  Top 10 Produtos em Ruptura
                </h3>
                <ChartDownloadButton
                  chartId="top-rupturas-chart"
                  filename="rupturas_top10"
                  label="Baixar"
                />
              </div>
              <PlotlyChart
                chartSpec={topRupturasChart}
                chartId="top-rupturas-chart"
                enableDownload={true}
                height="350px"
                onDataClick={handleChartClick}
              />
              <p class="text-xs text-muted mt-2">💡 Clique nas barras para ver detalhes do produto</p>
            </div>
          </div>

          {/* Segunda linha - 1 coluna */}
          <div class="card p-6 border">
            <div class="flex justify-between items-center mb-4">
              <h3 class="font-semibold flex items-center gap-2">
                <TrendingUp size={20} class="text-green-500" />
                Necessidade por Segmento
              </h3>
              <ChartDownloadButton
                chartId="necessidade-segmento-chart"
                filename="rupturas_por_segmento"
                label="Baixar"
              />
            </div>
            <PlotlyChart
              chartSpec={necessidadeSegmentoChart}
              chartId="necessidade-segmento-chart"
              enableDownload={true}
              height="400px"
            />
          </div>
        </div>
      </Show>

      {/* Modal de Detalhes do Produto */}
      <Show when={selectedProduct()}>
        <div
          class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedProduct(null)}
        >
          <div
            class="bg-card border rounded-lg p-6 max-w-2xl w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <div class="flex justify-between items-start mb-4">
              <h3 class="text-xl font-bold">Detalhes da Ruptura</h3>
              <button
                onClick={() => setSelectedProduct(null)}
                class="text-muted hover:text-foreground"
              >
                <X size={20} />
              </button>
            </div>

            <div class="space-y-4">
              <div>
                <p class="text-sm text-muted">Produto</p>
                <p class="font-mono font-medium">{selectedProduct()!.PRODUTO}</p>
              </div>
              <div>
                <p class="text-sm text-muted">Nome</p>
                <p class="font-medium">{selectedProduct()!.NOME}</p>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-sm text-muted">UNE</p>
                  <p class="font-medium">{selectedProduct()!.UNE}</p>
                </div>
                <div>
                  <p class="text-sm text-muted">Segmento</p>
                  <p class="font-medium">{selectedProduct()!.NOMESEGMENTO || 'N/A'}</p>
                </div>
              </div>
              <div class="grid grid-cols-3 gap-4">
                <div class="p-3 bg-green-500/10 border border-green-500/30 rounded">
                  <p class="text-xs text-muted">Vendas (30d)</p>
                  <p class="text-xl font-bold text-green-500">{Math.round(selectedProduct()!.VENDA_30DD)}</p>
                </div>
                <div class="p-3 bg-red-500/10 border border-red-500/30 rounded">
                  <p class="text-xs text-muted">Estoque Loja</p>
                  <p class="text-xl font-bold text-red-500">{Math.round(selectedProduct()!.ESTOQUE_UNE)}</p>
                </div>
                <div class="p-3 bg-blue-500/10 border border-blue-500/30 rounded">
                  <p class="text-xs text-muted">Linha Verde</p>
                  <p class="text-xl font-bold text-blue-500">{Math.round(selectedProduct()!.ESTOQUE_LV)}</p>
                </div>
              </div>
              <div class="p-4 bg-orange-500/10 border border-orange-500/30 rounded">
                <p class="text-sm text-muted mb-2">Necessidade de Reposição</p>
                <p class="text-3xl font-bold text-orange-500">{Math.round(selectedProduct()!.NECESSIDADE)} unidades</p>
                <div class="mt-3">
                  <div class="flex justify-between text-sm mb-1">
                    <span>Criticidade</span>
                    <span class="font-medium">{selectedProduct()!.CRITICIDADE_PCT.toFixed(0)}%</span>
                  </div>
                  <div class="w-full bg-gray-700 rounded-full h-2">
                    <div
                      class={`h-2 rounded-full ${
                        selectedProduct()!.CRITICIDADE_PCT >= 75 ? 'bg-red-500' :
                        selectedProduct()!.CRITICIDADE_PCT >= 50 ? 'bg-orange-500' :
                        selectedProduct()!.CRITICIDADE_PCT >= 25 ? 'bg-yellow-500' : 'bg-blue-500'
                      }`}
                      style={`width: ${selectedProduct()!.CRITICIDADE_PCT}%`}
                    />
                  </div>
                </div>
              </div>
            </div>

            <div class="mt-6 flex justify-end">
              <button
                onClick={() => setSelectedProduct(null)}
                class="btn btn-primary"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      </Show>

      {/* Tabela */}
      <Show when={!loading()} fallback={
        <div class="p-12 text-center border rounded-xl bg-card text-muted animate-pulse">
          <PackageX class="animate-spin mx-auto mb-4" size={32} />
          Identificando rupturas críticas...
        </div>
      }>
        <Show when={!error()} fallback={
          <div class="p-6 bg-red-900/10 border border-red-900/30 rounded-lg text-red-300 flex items-center gap-3">
            <AlertTriangle size={24} />
            <div>
              <h3 class="font-bold">Erro ao carregar dados</h3>
              <p class="text-sm opacity-80">{error()}</p>
            </div>
          </div>
        }>
          <Show when={data().length > 0} fallback={
            <div class="p-12 text-center border border-dashed rounded-xl text-muted">
              <Package size={48} class="mx-auto mb-4 opacity-20 text-green-500" />
              <p class="text-lg font-medium text-green-500">Nenhuma ruptura crítica detectada!</p>
              <p class="text-sm mt-2">Todos os produtos de alta venda possuem estoque adequado.</p>
            </div>
          }>
            <div class="border rounded-lg overflow-hidden bg-card shadow-sm">
              <div class="overflow-x-auto">
                <table class="w-full text-sm text-left">
                  <thead class="bg-muted/50 text-xs uppercase font-medium text-muted-foreground border-b">
                    <tr>
                      <th class="px-4 py-3">Produto</th>
                      <th class="px-4 py-3">UNE</th>
                      <th class="px-4 py-3 text-right">Venda (30d)</th>
                      <th class="px-4 py-3 text-right">Est. Loja</th>
                      <th class="px-4 py-3 text-right">Est. CD</th>
                      <th class="px-4 py-3 text-right">Linha Verde</th>
                      <th class="px-4 py-3 text-right">Necessidade</th>
                      <th class="px-4 py-3 text-center">Criticidade</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y">
                    <For each={data()}>
                      {(item) => (
                        <tr class="hover:bg-muted/30 transition-colors">
                          <td class="px-4 py-3">
                            <div class="font-medium">{item.NOME}</div>
                            <div class="text-xs text-muted-foreground font-mono">{item.PRODUTO}</div>
                          </td>
                          <td class="px-4 py-3">
                            <span class="px-2 py-1 bg-secondary rounded text-xs font-mono">{item.UNE}</span>
                          </td>
                          <td class="px-4 py-3 text-right font-medium">
                            <div class="flex items-center justify-end gap-1 text-green-500">
                              <ShoppingCart size={14} />
                              {Math.round(item.VENDA_30DD)}
                            </div>
                          </td>
                          <td class="px-4 py-3 text-right font-medium text-red-500">
                            <div class="flex items-center justify-end gap-1">
                              <Archive size={14} />
                              {Math.round(item.ESTOQUE_UNE)}
                            </div>
                          </td>
                          <td class="px-4 py-3 text-right font-medium text-red-500">
                            {Math.round(item.ESTOQUE_CD)}
                          </td>
                          <td class="px-4 py-3 text-right font-medium text-blue-500">
                            {Math.round(item.ESTOQUE_LV)}
                          </td>
                          <td class="px-4 py-3 text-right font-bold text-orange-500">
                            {Math.round(item.NECESSIDADE)} un
                          </td>
                          <td class="px-4 py-3 text-center">
                            <div class="flex flex-col items-center gap-1">
                              <span class={`px-2 py-1 rounded-full text-xs font-bold border ${getCriticidadeColor(item.CRITICIDADE_PCT)}`}>
                                {getCriticidadeLabel(item.CRITICIDADE_PCT)}
                              </span>
                              <div class="w-full bg-gray-700 rounded-full h-1.5 mt-1">
                                <div
                                  class={`h-1.5 rounded-full ${item.CRITICIDADE_PCT >= 75 ? 'bg-red-500' : item.CRITICIDADE_PCT >= 50 ? 'bg-orange-500' : item.CRITICIDADE_PCT >= 25 ? 'bg-yellow-500' : 'bg-blue-500'}`}
                                  style={`width: ${item.CRITICIDADE_PCT}%`}
                                />
                              </div>
                              <span class="text-xs text-muted-foreground">{item.CRITICIDADE_PCT.toFixed(0)}%</span>
                            </div>
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
      </Show>
    </div>
  );
}
