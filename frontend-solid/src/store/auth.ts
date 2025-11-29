import { createSignal, createRoot } from 'solid-js';
import api from '@/lib/api';

function createAuthStore() {
  const [user, setUser] = createSignal<any>(null);
  const [token, setToken] = createSignal<string | null>(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = createSignal<boolean>(!!localStorage.getItem('token'));
  const [loading, setLoading] = createSignal<boolean>(false);
  const [error, setError] = createSignal<string | null>(null);

  // Restaurar user do token ao inicializar
  const initToken = localStorage.getItem('token');
  if (initToken) {
    try {
      const payload = JSON.parse(atob(initToken.split('.')[1]));
      const userData = {
        username: payload.sub || 'user',
        role: payload.role || 'admin',
        email: payload.email || `${payload.sub}@agentbi.com`,
      };
      setUser(userData);
      console.log('🔄 User restaurado do token:', userData);
    } catch (e) {
      console.error('Erro ao restaurar user do token:', e);
      localStorage.removeItem('token');
      setToken(null);
      setIsAuthenticated(false);
    }
  }

  const login = async (username: string, password: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      // Endpoint correto do FastAPI (/auth/login -> recebe LoginRequest JSON)
      const response = await api.post('/auth/login', { username, password });
      
      const { access_token } = response.data;
      
      if (access_token) {
        localStorage.setItem('token', access_token);
        setToken(access_token);
        setIsAuthenticated(true);
        
        // Decodificar JWT para obter dados do usuário
        // JWT format: header.payload.signature
        try {
          const payload = JSON.parse(atob(access_token.split('.')[1]));
          console.log('📦 JWT Payload:', payload);
          
          // Definir dados do usuário baseado no payload do JWT
          const userData = {
            username: payload.sub || username,
            role: payload.role || 'admin', // Assumir admin se não especificado
            email: payload.email || `${username}@agentbi.com`,
          };
          
          console.log('👤 User data set:', userData);
          setUser(userData);
        } catch (jwtError) {
          console.error('Erro ao decodificar JWT:', jwtError);
          // Fallback: definir usuário com dados básicos
          setUser({
            username: username,
            role: 'admin',
            email: `${username}@agentbi.com`,
          });
        }
        
        return true;
      }
      return false;
    } catch (err: any) {
      console.error("Login error:", err);
      setError(err.response?.data?.detail || "Erro ao realizar login");
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
