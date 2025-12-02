import axios from 'axios';

// --- Types ---

export interface MetricsSummary {
  totalSales: number;
  totalUsers: number;
  revenue: number;
  productsCount: number;
  salesGrowth: number;
  usersGrowth: number;
}

export interface SaleItem {
  date: string;
  product: string;
  value: number;
  quantity: number;
}

export interface TopProduct {
  product: string;
  productName: string;
  totalSales: number;
  revenue: number;
}

export interface AnalyticsDataPoint {
  date: string;
  product: string;
  sales: number;
  revenue: number;
  une: string;
}

export interface AnalyticsResponse {
  data: AnalyticsDataPoint[];
  totalRecords: number;
  summary: {
    totalSales: number;
    totalRevenue: number;
    uniqueProducts: number;
    uniqueUnes: number;
    avgSalesPerProduct: number;
  };
}

export interface Report {
  id: string;
  title: string;
  description: string;
  content: string;
  status: string;
  author_id: string;
  author_name?: string;
  created_at: string;
  updated_at: string;
}

// --- API Client ---

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use((response) => {
  return response;
}, (error) => {
  // Não redirecionar automaticamente para login em caso de 401
  // Deixar que cada componente trate o erro como preferir
  if (error.response && error.response.status === 401) {
    console.warn('⚠️ 401 Unauthorized - Token pode estar inválido ou expirado');
    // NÃO fazer redirect automático - causa loop de logout
  }
  return Promise.reject(error);
});

// --- API Methods ---

export const metricsApi = {
  getSummary: () => api.get<MetricsSummary>('/metrics/summary'),
  getRecentSales: (limit = 20) => api.get<SaleItem[]>(`/metrics/recent-sales?limit=${limit}`),
  getTopProducts: (limit = 5) => api.get<TopProduct[]>(`/metrics/top-products?limit=${limit}`),
};

export const analyticsApi = {
  getData: (limit = 100) => api.get<AnalyticsResponse>(`/analytics/data?limit=${limit}`),
};

export const reportsApi = {
  getAll: () => api.get<Report[]>('/reports'),
};

export const adminApi = {
  syncParquet: () => api.post('/admin/sync-parquet'),
};

export default api;