import { createSignal, Show, createEffect } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import auth from '@/store/auth';
import { LogIn, Loader2 } from 'lucide-solid';

export default function Login() {
  console.log('🔵 Login component mounting...');
  const [username, setUsername] = createSignal('');
  const [password, setPassword] = createSignal('');
  const navigate = useNavigate();
  
  // Log when rendering
  createEffect(() => {
    console.log('🔵 Login component rendered. Auth loading:', auth.loading());
  });

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    console.log('🔐 Login attempt:', { username: username(), passwordLength: password().length });
    
    if (!username() || !password()) {
      console.error('❌ Username or password empty');
      return;
    }
    
    try {
      console.log('📡 Calling auth.login...');
      const success = await auth.login(username(), password());
      console.log('✅ Login result:', success);
      
      if (success) {
        console.log('🎉 Login successful! Navigating to dashboard...');
        // Usar window.location.href para forçar reload completo e garantir que o estado seja propagado
        window.location.href = '/dashboard';
      } else {
        console.error('❌ Login failed');
      }
    } catch (error) {
      console.error('💥 Login error:', error);
    }
  };

  return (
    <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-4">
      {/* Background Effects */}
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-pulse"></div>
        <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s"></div>
      </div>

      {/* Login Card */}
      <div class="relative w-full max-w-md">
        <div class="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-2xl p-8 space-y-6">
          {/* Header */}
          <div class="text-center space-y-2">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary to-indigo-500 rounded-2xl mb-4">
              <LogIn size={32} class="text-white" />
            </div>
            <h1 class="text-3xl font-bold bg-gradient-to-r from-primary to-indigo-400 bg-clip-text text-transparent">
              Agent BI
            </h1>
            <p class="text-slate-400 text-sm">
              Entre para acessar seus dados analíticos
            </p>
          </div>

          {/* Error Message */}
          <Show when={auth.error()}>
            <div class="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-start gap-3">
              <svg class="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="flex-1">
                <p class="text-sm text-red-200 font-medium">Erro de Autenticação</p>
                <p class="text-xs text-red-300/80 mt-1">{auth.error()}</p>
              </div>
            </div>
          </Show>

          {/* Form */}
          <form onSubmit={handleSubmit} class="space-y-4">
            {/* Username Field */}
            <div class="space-y-2">
              <label for="username" class="block text-sm font-medium text-slate-300">
                Usuário
              </label>
              <input
                id="username"
                type="text"
                value={username()}
                onInput={(e) => setUsername(e.currentTarget.value)}
                placeholder="Digite seu usuário"
                required
                autocomplete="username"
                class="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
              />
            </div>

            {/* Password Field */}
            <div class="space-y-2">
              <label for="password" class="block text-sm font-medium text-slate-300">
                Senha
              </label>
              <input
                id="password"
                type="password"
                value={password()}
                onInput={(e) => setPassword(e.currentTarget.value)}
                placeholder="Digite sua senha"
                required
                autocomplete="current-password"
                class="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={auth.loading()}
              class="w-full py-3 px-4 bg-gradient-to-r from-primary to-indigo-500 hover:from-primary/90 hover:to-indigo-500/90 text-white font-semibold rounded-lg shadow-lg shadow-primary/25 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <Show when={auth.loading()} fallback={<>Entrar</>}>
                <Loader2 size={20} class="animate-spin" />
                <span>Entrando...</span>
              </Show>
            </button>
          </form>

          {/* Footer */}
          <div class="pt-4 border-t border-slate-800">
            <div class="text-center space-y-2">
              <p class="text-xs text-slate-500">Credenciais de Teste</p>
              <div class="flex flex-col gap-1 text-xs">
                <div class="flex items-center justify-center gap-2 text-slate-400">
                  <span class="font-mono bg-slate-800 px-2 py-1 rounded">admin</span>
                  <span>/</span>
                  <span class="font-mono bg-slate-800 px-2 py-1 rounded">Admin@2024</span>
                </div>
                <div class="flex items-center justify-center gap-2 text-slate-400">
                  <span class="font-mono bg-slate-800 px-2 py-1 rounded text-xs">comprador</span>
                  <span>/</span>
                  <span class="font-mono bg-slate-800 px-2 py-1 rounded text-xs">comprador123</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Version Info */}
        <div class="text-center mt-6 text-xs text-slate-600">
          Agent BI v1.0.0 • Powered by SolidJS
        </div>
      </div>
    </div>
  );
}
