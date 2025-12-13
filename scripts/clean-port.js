/**
 * Script para limpar portas específicas no Windows
 * Mata processos que estão usando as portas 8000 e 3000
 */

const { execSync } = require('child_process');

const PORTS = [8000, 3000];

console.log('🧹 Limpando portas...\n');

PORTS.forEach(port => {
  try {
    console.log(`[${port}] Verificando porta ${port}...`);

    // Encontra o PID usando a porta
    const result = execSync(`netstat -ano | findstr :${port} | findstr LISTENING`, {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'ignore']
    });

    if (!result) {
      console.log(`[${port}] ✅ Porta livre\n`);
      return;
    }

    // Extrai PIDs únicos
    const pids = [...new Set(
      result
        .split('\n')
        .filter(line => line.trim())
        .map(line => {
          const parts = line.trim().split(/\s+/);
          return parts[parts.length - 1];
        })
        .filter(pid => pid && pid !== '0')
    )];

    if (pids.length === 0) {
      console.log(`[${port}] ✅ Porta livre\n`);
      return;
    }

    // Mata cada processo
    pids.forEach(pid => {
      try {
        console.log(`[${port}] 🔪 Encerrando processo ${pid}...`);
        execSync(`taskkill /F /PID ${pid}`, { stdio: 'ignore' });
        console.log(`[${port}] ✅ Processo ${pid} encerrado`);
      } catch (err) {
        console.log(`[${port}] ⚠️  Não foi possível encerrar processo ${pid}`);
      }
    });

    console.log(`[${port}] ✅ Porta ${port} liberada\n`);

  } catch (err) {
    // Porta já está livre
    console.log(`[${port}] ✅ Porta livre\n`);
  }
});

console.log('✅ Limpeza concluída!\n');
