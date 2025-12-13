// frontend-solid/src/components/PlotlyChart.tsx

import { createEffect, onCleanup, Accessor, createSignal, Show } from 'solid-js';
import Plotly from 'plotly.js-dist-min';
import { Maximize, Minimize } from 'lucide-solid';

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
            filename: `grafico_${new Date().toISOString().split('T')[0]}`,
            height: 800,
            width: 1200,
            scale: 2
          } : undefined,
          ...spec.config
        };

        Plotly.newPlot(chartDiv, spec.data, spec.layout, config);

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
