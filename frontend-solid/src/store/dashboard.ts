import { createRoot, batch } from 'solid-js';
import { createStore } from 'solid-js/store';
import { metricsApi, analyticsApi, MetricsSummary, AnalyticsDataPoint } from '@/lib/api';

interface DashboardState {
  // Grid Data
  data: AnalyticsDataPoint[];
  
  // KPI Data
  summary: MetricsSummary | null;
  
  // System State
  isLoading: boolean;
  error: string | null;
  lastUpdate: Date | null;
  isLive: boolean; // Controle do polling
}

function createDashboardStore() {
  const [state, setState] = createStore<DashboardState>({
    data: [],
    summary: null,
    isLoading: false,
    error: null,
    lastUpdate: null,
    isLive: true
  });

  let intervalId: number;

  const fetchData = async () => {
    if (!state.data.length) setState('isLoading', true); // Só mostra loading no primeiro load
    
    try {
      // Buscar dados em paralelo
      const [summaryRes, analyticsRes] = await Promise.all([
        metricsApi.getSummary(),
        analyticsApi.getData(100) // Top 100 registros para a grid
      ]);

      batch(() => {
        setState('summary', summaryRes.data);
        setState('data', analyticsRes.data.data); // Dados reais do backend
        setState('lastUpdate', new Date());
        setState('error', null);
        setState('isLoading', false);
      });
    } catch (err) {
      console.error("Dashboard fetch error:", err);
      setState('error', "Falha ao atualizar dados.");
      setState('isLoading', false);
      // Se falhar, para o polling para não floodar erros
      stopPolling(); 
    }
  };

  const startPolling = () => {
    fetchData(); // Busca imediata
    if (intervalId) clearInterval(intervalId);
    intervalId = setInterval(fetchData, 5000); // Atualiza a cada 5s
    setState('isLive', true);
  };

  const stopPolling = () => {
    clearInterval(intervalId);
    setState('isLive', false);
  };

  const togglePolling = () => {
    if (state.isLive) stopPolling();
    else startPolling();
  };

  // Iniciar polling automaticamente apenas se estiver logado (verificação feita na view)
  
  return { state, startPolling, stopPolling, togglePolling, fetchData };
}

export default createRoot(createDashboardStore);