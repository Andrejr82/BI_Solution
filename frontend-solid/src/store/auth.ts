import { createSignal, createRoot } from 'solid-js';
import api from '@/lib/api';

function createAuthStore() {
  const [user, setUser] = createSignal<any>(null);
  const [token, setToken] = createSignal<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = createSignal<boolean>(false);
  const [loading, setLoading] = createSignal<boolean>(false);
  const [error, setError] = createSignal<string | null>(null);

  // Função para validar e decodificar token
  const validateAndDecodeToken = (tokenString: string): any | null => {
    try {
      // Verificar formato JWT (deve ter 3 partes separadas por .)
      const parts = tokenString.split('.');
      if (parts.length !== 3) {
        console.error('❌ Token inválido: formato incorreto');
        return null;
      }

      // Decodificar payload
      const payload = JSON.parse(atob(parts[1]));

      // Verificar expiração
      if (payload.exp) {
        const now = Math.floor(Date.now() / 1000);
        if (payload.exp < now) {
          console.error('❌ Token expirado');
          return null;
        }
      }

      return payload;
    } catch (e) {
      console.error('❌ Erro ao validar token:', e);
      return null;
    }
  };

  // Restaurar user do token ao inicializar (com proteção para SSR)
  const initializeAuth = () => {
    try {
      if (typeof window === 'undefined' || !window.localStorage) {
        return;
      }
      
      const initToken = localStorage.getItem('token');
      if (initToken) {
        const payload = validateAndDecodeToken(initToken);
        if (payload) {
          const userData = {
            username: payload.username || payload.sub || 'user',
            role: payload.role || 'user',
            email: payload.email || `${payload.username || payload.sub}@agentbi.com`,
          };
          setUser(userData);
          setToken(initToken);
          setIsAuthenticated(true);
          console.log('🔄 User restaurado do token:', userData);
        } else {
          // Token inválido ou expirado - limpar
          console.warn('⚠️ Token inválido ou expirado - removendo');
          localStorage.removeItem('token');
          setIsAuthenticated(false);
          setUser(null);
          setToken(null);
        }
      }
    } catch (error) {
      console.error('❌ Erro ao inicializar autenticação:', error);
    }
  };

  // Executar inicialização
  initializeAuth();

  const login = async (username: string, password: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      // Endpoint correto do FastAPI (/auth/login -> recebe LoginRequest JSON)
      const response = await api.post('/auth/login', { username, password });

      const { access_token } = response.data;

      if (access_token) {
        // Validar token antes de salvar
        const payload = validateAndDecodeToken(access_token);

        if (!payload) {
          setError("Token inválido recebido do servidor");
          return false;
        }

        localStorage.setItem('token', access_token);
        setToken(access_token);
        setIsAuthenticated(true);

        // Definir dados do usuário baseado no payload do JWT
        const userData = {
          username: payload.username || payload.sub || username,
          role: payload.role || 'user',
          email: payload.email || `${payload.username || username}@agentbi.com`,
        };

        console.log('✅ Login successful. User:', userData);
        setUser(userData);

        return true;
      }
      return false;
    } catch (err: any) {
      console.error("❌ Login error:", err);
      const errorMsg = err.response?.data?.detail || "Erro ao realizar login";
      setError(errorMsg);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    window.location.href = '/login';
  };

  return { user, token, isAuthenticated, login, logout, loading, error };
}

export default createRoot(createAuthStore);
