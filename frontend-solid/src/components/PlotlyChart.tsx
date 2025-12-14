// frontend-solid/src/components/PlotlyChart.tsx

import { createEffect, onCleanup, Accessor, createSignal, Show } from 'solid-js';
import Plotly from 'plotly.js-dist-min';
import { Maximize, Minimize } from 'lucide-solid';

// ===== PALETA LOJAS CAÇULA - 40 ANOS DE TRADIÇÃO =====
// Cores terrosas/neutras para consistência visual
const CACULA_CHART_COLORS = [
  '#8B7355',  // Marrom Caçula (principal)
  '#C9A961',  // Dourado/Bronze (tradição)
  '#6B7A5A',  // Verde oliva
  '#A68968',  // Marrom claro
  '#CC8B3C',  // Laranja terroso
  '#5B7B9A',  // Azul acinzentado
  '#9B8875',  // Bege médio
  '#B8984E',  // Dourado escuro
  '#7A8B6F',  // Verde acinzentado
  '#B59B7A',  // Bege quente
];

interface PlotlyChartProps {
  chartSpec: Accessor<any>;
  chartId?: string;
  onDataClick?: (data: any) => void;
  onHover?: (data: any) => void;
  height?: string;
  enableDownload?: boolean;
}

export const PlotlyChart = (props: PlotlyChartProps) => {
  let chartDiv: HTMLDivElement | undefined;
  const chartId = props.chartId || `chart-${Math.random().toString(36).substr(2, 9)}`;
  const [isExpanded, setIsExpanded] = createSignal(false);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded());
    // Force resize after state change and DOM update
    setTimeout(() => {
      if (chartDiv) {
        Plotly.Plots.resize(chartDiv);
      }
    }, 50);
  };

  createEffect(() => {
    const spec = props.chartSpec();
    if (chartDiv && spec && Object.keys(spec).length > 0) {
      console.log('Rendering Plotly Chart with spec:', spec);
      try {
        // ===== APLICAR TEMA CAÇULA - LIGHT MODE =====
        // Merge layout com tema Lojas Caçula
        const caculaLayout = {
          paper_bgcolor: '#FAFAFA',  // Light background
          plot_bgcolor: '#FFFFFF',   // White plot area
          font: {
            color: '#2D2D2D',        // Cinza escuro quente
            family: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            size: 12
          },
          colorway: CACULA_CHART_COLORS, // Paleta terrosa Caçula

          // Eixos com cores suaves
          xaxis: {
            gridcolor: '#E5E5E5',
            linecolor: '#E5E5E5',
            zerolinecolor: '#E5E5E5',
            tickfont: { color: '#2D2D2D' },
            ...(spec.layout?.xaxis || {})
          },
          yaxis: {
            gridcolor: '#E5E5E5',
            linecolor: '#E5E5E5',
            zerolinecolor: '#E5E5E5',
            tickfont: { color: '#2D2D2D' },
            ...(spec.layout?.yaxis || {})
          },

          // Hover info estilizado
          hoverlabel: {
            bgcolor: '#FFFFFF',
            bordercolor: '#8B7355', // Marrom Caçula
            font: { color: '#2D2D2D', family: 'Inter, sans-serif' }
          },

          // Legend (legenda)
          legend: {
            font: { color: '#2D2D2D' },
            bgcolor: 'rgba(255,255,255,0.9)',
            bordercolor: '#E5E5E5',
            borderwidth: 1,
            ...(spec.layout?.legend || {})
          },

          // Merge com layout original (permite override)
          ...spec.layout
        };

        // Merge config com opções de download se habilitado
        const config = {
          responsive: true,
          displayModeBar: props.enableDownload ?? false,
          displaylogo: false,
          showLink: false,
          modeBarButtonsToRemove: ['sendDataToCloud', 'editInChartStudio', 'lasso2d', 'select2d'],
          modeBarButtonsToAdd: props.enableDownload ? ['downloadImage'] : [],
          toImageButtonOptions: props.enableDownload ? {
            format: 'png',
            filename: `grafico_cacula_${new Date().toISOString().split('T')[0]}`,
            height: 800,
            width: 1200,
            scale: 2
          } : undefined,
          ...spec.config
        };

        Plotly.newPlot(chartDiv, spec.data, caculaLayout, config);

        // Adicionar eventos de interação
        if (props.onDataClick) {
          chartDiv.on('plotly_click', (data) => {
            props.onDataClick!(data);
          });
        }

        if (props.onHover) {
          chartDiv.on('plotly_hover', (data) => {
            props.onHover!(data);
          });
        }
      } catch (error: any) {
        console.error("Error rendering Plotly chart:", error);
        chartDiv.innerHTML = `<div class="text-red-500">Erro ao renderizar gráfico: ${error.message}</div>`;
      }
    } else if (chartDiv && (!spec || Object.keys(spec).length === 0)) {
      chartDiv.innerHTML = `<div class="text-gray-500">Nenhuma especificação de gráfico fornecida.</div>`;
    }
  });

  onCleanup(() => {
    if (chartDiv) {
      Plotly.purge(chartDiv);
    }
  });

  return (
    <div class={`relative transition-all duration-300 ${isExpanded() ? 'fixed inset-0 z-50 bg-background p-6 flex flex-col' : ''}`}>
      <div class="absolute top-2 right-2 z-10 flex gap-2">
        <button
          onClick={toggleExpand}
          class="p-2 bg-background/80 hover:bg-muted rounded-full shadow-sm border backdrop-blur-sm transition-colors"
          title={isExpanded() ? "Restaurar tamanho" : "Expandir tela cheia"}
        >
          <Show when={isExpanded()} fallback={<Maximize size={16} />}>
            <Minimize size={16} />
          </Show>
        </button>
      </div>
      <div
        ref={chartDiv}
        id={chartId}
        class="w-full"
        style={{ height: isExpanded() ? '100%' : (props.height || '400px') }}
      >
        {/* Chart will be rendered here by Plotly.js */}
      </div>
    </div>
  );
};
