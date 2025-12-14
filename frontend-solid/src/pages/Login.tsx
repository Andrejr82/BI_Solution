import { createSignal, Show, createEffect } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import auth from '@/store/auth';
import { LogIn, Loader2 } from 'lucide-solid';
import { Logo } from '@/components/Logo';

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
    <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-amber-50 via-orange-50 to-stone-100 p-4">
      {/* Background Effects - Lojas Caçula (warm tones) */}
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl animate-pulse"></div>
        <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/5 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s"></div>
      </div>

      {/* Login Card - Lojas Caçula */}
      <div class="relative w-full max-w-md">
        <div class="bg-white/95 backdrop-blur-xl border-2 border-primary/20 rounded-2xl shadow-2xl p-8 space-y-6">
          {/* Header */}
          <div class="text-center space-y-4">
            <div class="flex justify-center mb-4">
              <Logo size="xl" className="filter drop-shadow-lg" />
            </div>
            <div class="space-y-2">
              <h1 class="text-3xl font-bold text-primary">
                CAÇULINHA BI
              </h1>
              <p class="text-sm text-muted-foreground">
                Entre para acessar seus dados analíticos
              </p>
            </div>
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
              <label for="username" class="block text-sm font-medium text-foreground">
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
                class="w-full px-4 py-3 bg-white border-2 border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              />
            </div>

            {/* Password Field */}
            <div class="space-y-2">
              <label for="password" class="block text-sm font-medium text-foreground">
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
                class="w-full px-4 py-3 bg-white border-2 border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              />
            </div>

            {/* Submit Button - Lojas Caçula */}
            <button
              type="submit"
              disabled={auth.loading()}
              class="w-full py-3 px-4 bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white font-semibold rounded-lg shadow-lg shadow-primary/20 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <Show when={auth.loading()} fallback={<>Entrar</>}>
                <Loader2 size={20} class="animate-spin" />
                <span>Entrando...</span>
              </Show>
            </button>
          </form>
        </div>

        {/* Version Info - Lojas Caçula */}
        <div class="text-center mt-6 space-y-2">
          <div class="flex justify-center">
            <Logo size="sm" className="opacity-60" />
          </div>
          <div class="text-xs text-muted-foreground">
            Caçulinha BI v1.0.0 • Powered by SolidJS
          </div>
        </div>
      </div>
    </div>
  );
}
