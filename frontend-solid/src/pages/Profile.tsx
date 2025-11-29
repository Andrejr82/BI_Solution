import { createSignal, onMount } from 'solid-js';
import { Lock, CheckCircle, AlertCircle } from 'lucide-solid';
import auth from '@/store/auth';

export default function Profile() {
  const [currentPass, setCurrentPass] = createSignal('');
  const [newPass, setNewPass] = createSignal('');
  const [confirmPass, setConfirmPass] = createSignal('');
  const [message, setMessage] = createSignal<{ type: 'success' | 'error', text: string } | null>(null);

  const handleChangePassword = (e: Event) => {
    e.preventDefault();
    
    if (newPass() !== confirmPass()) {
      setMessage({ type: 'error', text: 'As senhas não coincidem.' });
      return;
    }

    if (newPass().length < 8) {
      setMessage({ type: 'error', text: 'A senha deve ter pelo menos 8 caracteres.' });
      return;
    }

    // Simulação - Conectar ao endpoint real
    setMessage({ type: 'success', text: 'Senha alterada com sucesso!' });
    setCurrentPass('');
    newPass('');
    setConfirmPass('');
  };

  return (
    <div class="p-6 max-w-2xl mx-auto">
      <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
        <Lock /> Perfil e Segurança
      </h2>

      <div class="card border p-6 space-y-6">
        <div>
          <h3 class="text-lg font-medium">Dados do Usuário</h3>
          <div class="mt-4 grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs text-muted">Nome de Usuário</label>
              <div class="font-medium">{auth.user()?.username}</div>
            </div>
            <div>
              <label class="text-xs text-muted">Função (Role)</label>
              <div class="font-medium capitalize">{auth.user()?.role}</div>
            </div>
            <div class="col-span-2">
              <label class="text-xs text-muted">Segmentos Permitidos</label>
              <div class="font-mono text-xs bg-secondary p-2 rounded mt-1">
                {JSON.stringify(auth.user()?.allowed_segments || [], null, 2)}
              </div>
            </div>
          </div>
        </div>

        <hr class="border-border" />

        <form onSubmit={handleChangePassword} class="space-y-4">
          <h3 class="text-lg font-medium">Alterar Senha</h3>
          
          {message() && (
            <div class={`p-3 rounded text-sm flex items-center gap-2 ${
              message()?.type === 'success' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
            }`}>
              {message()?.type === 'success' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
              {message()?.text}
            </div>
          )}

          <div>
            <label class="label">Senha Atual</label>
            <input type="password" class="input" value={currentPass()} onInput={(e) => setCurrentPass(e.currentTarget.value)} required />
          </div>
          <div>
            <label class="label">Nova Senha</label>
            <input type="password" class="input" value={newPass()} onInput={(e) => setNewPass(e.currentTarget.value)} required />
          </div>
          <div>
            <label class="label">Confirmar Nova Senha</label>
            <input type="password" class="input" value={confirmPass()} onInput={(e) => setConfirmPass(e.currentTarget.value)} required />
          </div>

          <button type="submit" class="btn btn-primary">Salvar Nova Senha</button>
        </form>
      </div>
    </div>
  );
}
