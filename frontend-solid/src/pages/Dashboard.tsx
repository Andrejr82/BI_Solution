import { createSignal, onMount, Show, For, createMemo } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import { ShoppingCart, Package, AlertTriangle, DollarSign, RefreshCw, TrendingUp, X, CheckCircle, Info } from 'lucide-solid';
import api from '../lib/api';
import { PlotlyChart } from '../components/PlotlyChart';
import { ChartDownloadButton } from '../components/ChartDownloadButton';
import { AIInsightsPanel } from '../components/AIInsightsPanel';
import auth from '@/store/auth';

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
  const navigate = useNavigate();
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

  // Context7 Logic: Derived State
  const businessStatus = createMemo(() => {
    if (!kpis()) return 'loading';
    const ruptureRate = kpis()!.produtos_ruptura / (kpis()!.total_produtos || 1);
    if (kpis()!.produtos_ruptura > 50 || ruptureRate > 0.1) return 'critical';
    if (kpis()!.produtos_ruptura > 0) return 'warning';
    return 'healthy';
  });

  const handleProductClick = (clickData: any) => {
    if (clickData && clickData.points && clickData.points[0]) {
      const point = clickData.points[0];
      if (point.customdata) {
        setSelectedProductInfo(point.customdata);
      }
    }
  };

  const loadKPIs = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.get<BusinessKPIs>('/metrics/business-kpis');
      setKpis(response.data);
      setLastUpdate(new Date());

      // Context7 Storytelling: Chart 1 - "Who is leading?"
      if (response.data.top_produtos.length > 0) {
        const topProduct = response.data.top_produtos[0];
        // LOJAS CAÇULA - LIGHT THEME
        const topProdutosSpec = {
          data: [{
            type: 'bar',
            x: response.data.top_produtos.map(p => p.nome),
            y: response.data.top_produtos.map(p => p.vendas),
            marker: {
              color: response.data.top_produtos.map((_, i) => i === 0 ? '#8B7355' : '#C9A961'), // Marrom Caçula, Dourado
              line: { color: '#E5E5E5', width: 1 }
            },
            text: response.data.top_produtos.map(p => p.vendas.toLocaleString()),
            textposition: 'outside',
            textfont: { color: '#2D2D2D' },
            hovertemplate: '<b>%{x}</b><br>Vendas: %{y:,}<extra></extra>',
            customdata: response.data.top_produtos.map(p => ({ produto: p.produto, nome: p.nome, vendas: p.vendas }))
          }],
          layout: {
            title: {
              text: '<b>Quais produtos impulsionam as vendas?</b><br><span style="font-size:12px;color:#6B6B6B">O líder de vendas representa ' + Math.round((topProduct.vendas / response.data.top_produtos.reduce((a, b) => a + b.vendas, 0)) * 100) + '% do volume total do top 10</span>',
              font: { size: 16, color: '#2D2D2D', family: 'Inter, sans-serif' },
              x: 0.05,
            },
            annotations: [
              {
                x: topProduct.nome,
                y: topProduct.vendas,
                xref: 'x',
                yref: 'y',
                text: '🏆 Líder',
                showarrow: true,
                arrowhead: 2,
                ax: 0,
                ay: -40,
                font: { color: '#8B7355', size: 12, family: 'Inter, sans-serif' }
              }
            ],
            xaxis: {
              title: '',
              tickangle: -45,
              tickfont: { size: 10, color: '#6B6B6B', family: 'Inter, sans-serif' },
              gridcolor: '#E5E5E5',
              linecolor: '#E5E5E5'
            },
            yaxis: {
              title: 'Volume de Vendas (30 dias)',
              titlefont: { color: '#6B6B6B', size: 10, family: 'Inter, sans-serif' },
              tickfont: { color: '#6B6B6B', family: 'Inter, sans-serif' },
              gridcolor: '#E5E5E5',
              linecolor: '#E5E5E5'
            },
            plot_bgcolor: '#FFFFFF',
            paper_bgcolor: '#FAFAFA',
            margin: { l: 60, r: 20, t: 80, b: 120 },
            font: { color: '#2D2D2D', family: 'Inter, sans-serif' }
          },
          config: { responsive: true, displayModeBar: false }
        };
        setTopProdutosChart(topProdutosSpec);
      }

      // Context7 Storytelling: Chart 2 - "Composition"
      if (response.data.vendas_por_categoria.length > 0) {
        // LOJAS CAÇULA - LIGHT THEME (Cores Terrosas)
        const vendasCategoriaSpec = {
          data: [{
            type: 'pie',
            labels: response.data.vendas_por_categoria.map(c => c.categoria),
            values: response.data.vendas_por_categoria.map(c => c.vendas),
            hovertemplate: '<b>%{label}</b><br>Vendas: %{value:,}<br>%{percent}<extra></extra>',
            marker: {
              colors: [
                '#8B7355',  // Marrom Caçula
                '#C9A961',  // Dourado/Bronze
                '#6B7A5A',  // Verde oliva
                '#A68968',  // Marrom claro
                '#CC8B3C',  // Laranja terroso
                '#5B7B9A',  // Azul acinzentado
                '#9B8875',  // Bege médio
                '#B8984E',  // Dourado escuro
                '#7A8B6F',  // Verde acinzentado
                '#B59B7A'   // Bege quente
              ],
              line: { color: '#FFFFFF', width: 2 }
            },
            textinfo: 'label+percent',
            textposition: 'inside',
            textfont: { size: 11, color: '#FFFFFF', family: 'Inter, sans-serif' },
            hole: 0.4
          }],
          layout: {
            title: {
              text: '<b>Como as vendas estão distribuídas?</b><br><span style="font-size:12px;color:#6B6B6B">Participação por categoria de produto</span>',
              font: { size: 16, color: '#2D2D2D', family: 'Inter, sans-serif' },
              x: 0.05
            },
            plot_bgcolor: '#FFFFFF',
            paper_bgcolor: '#FAFAFA',
            margin: { l: 20, r: 20, t: 80, b: 20 },
            font: { color: '#2D2D2D', family: 'Inter, sans-serif' },
            showlegend: true,
            legend: {
              orientation: 'v',
              x: 1,
              y: 1,
              font: { size: 10, color: '#6B6B6B', family: 'Inter, sans-serif' },
              bgcolor: 'rgba(255,255,255,0.9)',
              bordercolor: '#E5E5E5',
              borderwidth: 1
            }
          },
          config: { responsive: true, displayModeBar: false }
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
    // Auto-refresh removido conforme solicitado
    // const interval = setInterval(() => loadKPIs(), 30000);
    // return () => clearInterval(interval);
  });

  return (
    <div class="flex flex-col h-full p-6 gap-6 max-w-[1600px] mx-auto">
      {/* 1. Context7: Executive Summary Header */}
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b pb-6">
        <div>
          <h2 class="text-3xl font-bold tracking-tight text-foreground">
            Olá, {auth.user()?.username || 'Usuário'}
          </h2>
          <div class="flex items-center gap-2 mt-2">
            <Show when={businessStatus() === 'healthy'}>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                <CheckCircle size={12} class="mr-1" /> Operação Saudável
              </span>
            </Show>
            <Show when={businessStatus() === 'warning'}>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                <AlertTriangle size={12} class="mr-1" /> Atenção Necessária
              </span>
            </Show>
            <Show when={businessStatus() === 'critical'}>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                <AlertTriangle size={12} class="mr-1" /> Situação Crítica
              </span>
            </Show>
            <span class="text-sm text-muted ml-2">
              Visão geral do desempenho do negócio
            </span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs text-muted text-right hidden md:block">
            Dados atualizados<br />{lastUpdate()?.toLocaleTimeString()}
          </span>
          <button
            onClick={loadKPIs}
            class="btn btn-outline btn-icon"
            disabled={loading()}
            title="Atualizar dados"
          >
            <RefreshCw size={18} class={loading() ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Loading State */}
      <Show when={loading() && !kpis()}>
        <div class="flex-1 flex flex-col items-center justify-center text-muted gap-4">
          <RefreshCw size={48} class="animate-spin opacity-20" />
          <p>Analisando dados do negócio...</p>
        </div>
      </Show>

      {/* Error State */}
      <Show when={error()}>
        <div class="p-4 border border-red-500/50 bg-red-500/10 rounded-lg text-red-500 flex items-center gap-3">
          <AlertTriangle size={24} />
          <div>
            <h3 class="font-bold">Falha ao carregar dashboard</h3>
            <p class="text-sm opacity-80">{error()}</p>
          </div>
        </div>
      </Show>

      <Show when={kpis() && !loading()}>
        {/* 2. Context7: Key Performance Indicators (The "What") */}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="kpi-card bg-card border rounded-xl p-5 shadow-sm hover:shadow-md transition-all relative overflow-hidden group">
            <div class="absolute right-0 top-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <DollarSign size={48} />
            </div>
            <p class="text-sm font-medium text-muted uppercase tracking-wider">Valor em Estoque</p>
            <h3 class="text-3xl font-bold mt-1">{kpis()!.valor_estoque.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</h3>
            <p class="text-xs text-muted mt-2 flex items-center gap-1">
              <TrendingUp size={12} class="text-green-500" /> Capital imobilizado
            </p>
          </div>

          <div class="kpi-card bg-card border rounded-xl p-5 shadow-sm hover:shadow-md transition-all relative overflow-hidden group">
            <div class="absolute right-0 top-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <AlertTriangle size={48} />
            </div>
            <p class="text-sm font-medium text-muted uppercase tracking-wider">Rupturas</p>
            <h3 class={`text-3xl font-bold mt-1 ${kpis()!.produtos_ruptura > 0 ? 'text-destructive' : 'text-foreground'}`}>
              {kpis()!.produtos_ruptura}
            </h3>
            <p class="text-xs text-muted mt-2">
              {kpis()!.produtos_ruptura > 0 ? 'Produtos precisam de atenção imediata' : 'Estoque saudável'}
            </p>
          </div>

          <div class="kpi-card bg-card border rounded-xl p-5 shadow-sm hover:shadow-md transition-all relative overflow-hidden group">
            <div class="absolute right-0 top-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Package size={48} />
            </div>
            <p class="text-sm font-medium text-muted uppercase tracking-wider">Mix de Produtos</p>
            <h3 class="text-3xl font-bold mt-1">{kpis()!.total_produtos}</h3>
            <p class="text-xs text-muted mt-2">SKUs ativos no catálogo</p>
          </div>

          <div class="kpi-card bg-card border rounded-xl p-5 shadow-sm hover:shadow-md transition-all relative overflow-hidden group">
            <div class="absolute right-0 top-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <ShoppingCart size={48} />
            </div>
            <p class="text-sm font-medium text-muted uppercase tracking-wider">Cobertura</p>
            <h3 class="text-3xl font-bold mt-1">{kpis()!.total_unes}</h3>
            <p class="text-xs text-muted mt-2">Lojas/UNEs monitoradas</p>
          </div>
        </div>

        {/* 3. Context7: Narrative Charts (The "Why") */}
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* ✅ CORREÇÃO: Removido h-[400px] fixo para permitir fullscreen correto */}
          <div class="card bg-card border rounded-xl p-1 shadow-sm overflow-hidden flex flex-col" style="min-height: 400px;">
            <div class="flex-1 min-h-0">
              <PlotlyChart
                chartSpec={topProdutosChart}
                chartId="top-produtos-chart"
                enableDownload={false} // Clean look
                onDataClick={handleProductClick}
                height="380px"
              />
            </div>
            <div class="px-4 py-2 bg-muted/30 border-t text-xs text-muted flex justify-between items-center">
              <span>Clique nas barras para detalhes</span>
              <ChartDownloadButton chartId="top-produtos-chart" filename="top_produtos" label="" size="sm" />
            </div>
          </div>

          {/* ✅ CORREÇÃO: Removido h-[400px] fixo para permitir fullscreen correto */}
          <div class="card bg-card border rounded-xl p-1 shadow-sm overflow-hidden flex flex-col" style="min-height: 400px;">
            <div class="flex-1 min-h-0">
              <PlotlyChart
                chartSpec={vendasCategoriaChart}
                chartId="vendas-categoria-chart"
                enableDownload={false}
                height="380px"
              />
            </div>
            <div class="px-4 py-2 bg-muted/30 border-t text-xs text-muted flex justify-between items-center">
              <span>Distribuição de volume</span>
              <ChartDownloadButton chartId="vendas-categoria-chart" filename="vendas_categoria" label="" size="sm" />
            </div>
          </div>
        </div>

        {/* 4. Context7: AI Analysis (The "So What?") */}
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2">
            <AIInsightsPanel />
          </div>

          {/* Actionable List */}
          <div class="card bg-card border rounded-xl flex flex-col">
            <div class="p-4 border-b flex items-center justify-between">
              <h3 class="font-bold flex items-center gap-2">
                <TrendingUp size={18} class="text-primary" />
                Destaques
              </h3>
              <span class="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">Top 5</span>
            </div>
            <div class="flex-1 overflow-y-auto">
              <table class="w-full text-sm">
                <tbody>
                  <For each={kpis()!.top_produtos.slice(0, 5)}>
                    {(produto, i) => (
                      <tr class="border-b last:border-0 hover:bg-muted/50 transition-colors cursor-pointer" onClick={() => setSelectedProductInfo(produto)}>
                        <td class="p-3 font-mono text-muted w-8 text-center">{i() + 1}</td>
                        <td class="p-3">
                          <div class="font-medium">{produto.nome}</div>
                          <div class="text-xs text-muted">{produto.produto}</div>
                        </td>
                        <td class="p-3 text-right font-bold text-foreground">
                          {produto.vendas.toLocaleString()}
                        </td>
                      </tr>
                    )}
                  </For>
                </tbody>
              </table>
            </div>
            {/* ✅ CORREÇÃO: Adicionado onClick para navegar ao Chat com query */}
            <div class="p-3 bg-muted/20 border-t text-center">
              <button
                class="text-xs font-medium text-primary hover:underline"
                onClick={() => {
                  localStorage.setItem('example_query', 'Mostre o ranking completo dos top 20 produtos mais vendidos com análise detalhada');
                  navigate('/chat');
                }}
              >
                Ver ranking completo
              </button>
            </div>
          </div>
        </div>
      </Show>

      {/* Detail Modal */}
      <Show when={selectedProductInfo()}>
        <div
          class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4 animate-in fade-in duration-200"
          onClick={() => setSelectedProductInfo(null)}
        >
          <div
            class="bg-card border rounded-xl shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            <div class="relative h-32 bg-gradient-to-r from-primary/20 to-accent/20 flex items-center justify-center">
              <Package size={64} class="text-primary opacity-50" />
              <button
                onClick={() => setSelectedProductInfo(null)}
                class="absolute top-4 right-4 p-2 bg-black/20 hover:bg-black/40 rounded-full text-white transition-colors"
              >
                <X size={16} />
              </button>
            </div>

            <div class="p-6">
              <div class="mb-6">
                <h3 class="text-lg font-bold leading-tight">{selectedProductInfo()!.nome}</h3>
                <p class="text-sm font-mono text-muted mt-1">SKU: {selectedProductInfo()!.produto}</p>
              </div>

              <div class="grid grid-cols-2 gap-4 mb-6">
                <div class="p-3 bg-secondary rounded-lg">
                  <p class="text-xs text-muted uppercase">Vendas (30d)</p>
                  <p class="text-xl font-bold text-foreground">{selectedProductInfo()!.vendas.toLocaleString()}</p>
                </div>
                <div class="p-3 bg-green-500/10 rounded-lg">
                  <p class="text-xs text-green-700 dark:text-green-400 uppercase">Status</p>
                  <p class="text-xl font-bold text-green-700 dark:text-green-400">Ativo</p>
                </div>
              </div>

              <div class="flex gap-3">
                <button class="flex-1 btn btn-primary" onClick={() => {
                  const product = selectedProductInfo();
                  if (product) {
                    localStorage.setItem('example_query', `Analise detalhadamente o desempenho de vendas do produto "${product.nome}" (SKU: ${product.produto})`);
                    navigate('/chat');
                  }
                }}>
                  Ver Análise Completa
                </button>
              </div>
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
}