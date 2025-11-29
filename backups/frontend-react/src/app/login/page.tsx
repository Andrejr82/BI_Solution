'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth.store';
import { authService } from '@/services/auth.service';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((state) => state.login);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    const formData = new FormData(e.currentTarget);
    const credentials = {
      username: formData.get('username') as string,
      password: formData.get('password') as string,
    };

    try {
      const response = await authService.login(credentials);

      // Temporarily store tokens to enable authenticated requests
      const setToken = useAuthStore.getState().setToken;
      setToken(response.access_token, response.refresh_token);

      // Fetch real user data from the server
      const user = await authService.getCurrentUser();

      // Complete login with real user data
      login(user, response.access_token, response.refresh_token);

      router.push('/dashboard');
    } catch (err: any) {
      // Detect network errors specifically
      if (err.code === 'ERR_NETWORK' || err.message?.includes('Network Error')) {
        setError('Backend não está disponível. Certifique-se de que o servidor está rodando na porta 8000.');
      } else if (err.response?.status === 401 || err.response?.status === 403) {
        setError('Credenciais inválidas. Tente novamente. (Dica: Senha padrão é Admin@2024)');
      } else {
        setError('Erro ao fazer login. Tente novamente.');
      }
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center text-2xl font-bold">
            Agent Solution BI
          </CardTitle>
          <p className="text-center text-sm text-muted-foreground">
            Interface de Produção
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Usuário</Label>
              <Input
                id="username"
                name="username"
                type="text"
                required
                autoComplete="username"
                disabled={isLoading}
                placeholder="Digite seu usuário"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                name="password"
                type="password"
                required
                autoComplete="current-password"
                disabled={isLoading}
                placeholder="Digite sua senha"
              />
            </div>
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
