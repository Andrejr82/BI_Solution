import { createSignal, For, Show } from 'solid-js';
import { HelpCircle, Book, AlertCircle, Database, Search, ChevronDown, ChevronUp } from 'lucide-solid';

type TabType = 'guia' | 'faq' | 'troubleshooting' | 'dados';

interface FAQItem {
  pergunta: string;
  resposta: string;
}

interface TroubleshootingItem {
  problema: string;
  solucao: string[];
}

export default function Help() {
  const [activeTab, setActiveTab] = createSignal<TabType>('guia');
  const [searchTerm, setSearchTerm] = createSignal('');
  const [expandedFAQ, setExpandedFAQ] = createSignal<number | null>(null);

  const FAQ_ITEMS: FAQItem[] = [
    {
      pergunta: 'Como faço para consultar produtos em ruptura?',
      resposta: 'Navegue até a página "Rupturas Críticas" no menu Dashboards. Você verá uma lista completa de produtos em situação crítica, com filtros por segmento e UNE. Alternativamente, pergunte no Chat BI: "Quais produtos estão em ruptura crítica?"'
    },
    {
      pergunta: 'Como solicitar uma transferência de estoque?',
      resposta: 'Acesse a página "Transferências" no menu Operacional. Selecione o modo de transferência (1→1, 1→N ou N→N), escolha o produto, UNE origem e destino, e adicione ao carrinho. O sistema validará automaticamente e mostrará alertas de prioridade.'
    },
    {
      pergunta: 'O que significa "Linha Verde" e "Linha Vermelha"?',
      resposta: 'Linha Verde (LV) é o estoque mínimo recomendado. Linha Vermelha (LR) é o estoque crítico de segurança. Produtos abaixo da LV precisam de atenção. Abaixo da LR indicam ruptura iminente.'
    },
    {
      pergunta: 'Como interpretar a criticidade % nas rupturas?',
      resposta: 'A criticidade % representa o quão grave é a ruptura. Valores acima de 80% indicam situação URGENTE. Entre 50-80% é ALTA prioridade. 20-50% é MÉDIA. Abaixo de 20% é BAIXA. Baseia-se em vendas, estoque e histórico.'
    },
    {
      pergunta: 'Posso exportar dados para Excel?',
      resposta: 'Sim! Todas as páginas com tabelas (Rupturas, Transfers, Reports) possuem botão "Download CSV". No Chat BI, você pode solicitar dados e baixá-los usando o botão de download que aparece nas respostas tabulares.'
    },
    {
      pergunta: 'Como funciona o sistema de aprendizado?',
      resposta: 'O sistema aprende com feedbacks (👍 👎) dados nas respostas do Chat BI. Acesse a página "Aprendizado" para ver estatísticas de feedback, análise de erros e padrões identificados. Isso ajuda a melhorar continuamente as respostas.'
    },
    {
      pergunta: 'Qual a diferença entre "Metrics" e "Analytics"?',
      resposta: 'Metrics mostra KPIs do sistema (cache, queries, tempo de resposta). Analytics mostra análises de negócio (vendas por categoria, giro de estoque, curva ABC). Use Metrics para monitorar performance técnica e Analytics para insights de negócio.'
    },
    {
      pergunta: 'Posso testar o modelo Gemini sem afetar dados reais?',
      resposta: 'Sim! Use a página "Playground" no menu Inteligência. Lá você pode testar o modelo com parâmetros customizados (temperature, max tokens, JSON mode) sem impactar queries reais ou dados de produção.'
    },
    {
      pergunta: 'Como alterar minha senha?',
      resposta: 'Acesse "Alterar Senha" no menu Sistema. Digite a senha atual, nova senha (mínimo 8 caracteres, com maiúsculas, minúsculas, números e caracteres especiais) e confirme. Você será deslogado automaticamente após a troca.'
    },
    {
      pergunta: 'Administradores podem gerenciar usuários?',
      resposta: 'Sim! Usuários admin têm acesso à página "Administração" onde podem criar, editar, ativar/desativar e excluir usuários, além de gerenciar roles (admin, user, viewer) e sincronizar dados Parquet.'
    }
  ];

  const TROUBLESHOOTING_ITEMS: TroubleshootingItem[] = [
    {
      problema: 'Chat BI não está respondendo ou demora muito',
      solucao: [
        'Verifique sua conexão com a internet',
        'Confirme que o backend está rodando (veja indicador de status)',
        'Limpe o histórico do chat e tente novamente',
        'Se persistir, acesse Diagnóstico DB para verificar conexão com banco de dados',
        'Verifique logs do sistema em /diagnostics'
      ]
    },
    {
      problema: 'Erro 401 - Não autorizado',
      solucao: [
        'Seu token de autenticação expirou. Faça logout e login novamente',
        'Limpe o localStorage do navegador (F12 > Application > Local Storage)',
        'Verifique se seu usuário está ativo (peça a um admin verificar)',
        'Se problema persistir, contate o administrador do sistema'
      ]
    },
    {
      problema: 'Dados não aparecem ou estão desatualizados',
      solucao: [
        'Clique no botão "Atualizar" (ícone ⟳) no topo da página',
        'Acesse Admin > Sincronização para sincronizar dados SQL Server → Parquet',
        'Verifique se você tem permissão para acessar os dados (role necessária)',
        'Limpe cache do navegador (Ctrl+Shift+Delete)',
        'Verifique diagnóstico DB para status da conexão'
      ]
    },
    {
      problema: 'Gráficos não são exibidos corretamente',
      solucao: [
        'Atualize a página (F5)',
        'Verifique se JavaScript está habilitado no navegador',
        'Tente em modo anônimo/privado para descartar extensões',
        'Use navegador moderno (Chrome, Firefox, Edge atualizados)',
        'Verifique console do navegador (F12) para erros'
      ]
    },
    {
      problema: 'Não consigo criar transferência - validação falha',
      solucao: [
        'Verifique se o produto existe e tem estoque na UNE origem',
        'Confirme que a quantidade solicitada é válida (> 0)',
        'Verifique se a UNE destino pode receber o produto',
        'Alguns produtos podem ter restrições de transferência',
        'Consulte a mensagem de erro detalhada retornada pelo sistema'
      ]
    },
    {
      problema: 'Página Admin não está acessível',
      solucao: [
        'Verifique se seu usuário tem role "admin"',
        'Faça logout e login novamente para atualizar permissões',
        'Se você é admin mas não consegue acessar, contate suporte técnico',
        'Verifique se a URL está correta: /admin'
      ]
    },
    {
      problema: 'Download CSV falha ou arquivo vazio',
      solucao: [
        'Aplique filtros para reduzir quantidade de dados',
        'Verifique se há dados disponíveis na tabela',
        'Tente atualizar dados antes de exportar',
        'Desabilite bloqueador de pop-ups no navegador',
        'Verifique permissões de escrita na pasta Downloads'
      ]
    }
  ];

  const filteredFAQ = () => {
    if (!searchTerm()) return FAQ_ITEMS;
    const term = searchTerm().toLowerCase();
    return FAQ_ITEMS.filter(item =>
      item.pergunta.toLowerCase().includes(term) ||
      item.resposta.toLowerCase().includes(term)
    );
  };

  return (
    <div class="flex flex-col h-full p-6 gap-6">
      {/* Header */}
      <div>
        <h2 class="text-2xl font-bold flex items-center gap-2">
          <HelpCircle size={28} />
          Central de Ajuda
        </h2>
        <p class="text-muted">Documentação, FAQ e guias de uso do sistema</p>
      </div>

      {/* Tabs */}
      <div class="border-b">
        <div class="flex gap-1">
          <button
            onClick={() => setActiveTab('guia')}
            class={`px-4 py-2 font-medium transition-colors ${
              activeTab() === 'guia'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted hover:text-foreground'
            }`}
          >
            <div class="flex items-center gap-2">
              <Book size={16} />
              Guia Rápido
            </div>
          </button>

          <button
            onClick={() => setActiveTab('faq')}
            class={`px-4 py-2 font-medium transition-colors ${
              activeTab() === 'faq'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted hover:text-foreground'
            }`}
          >
            <div class="flex items-center gap-2">
              <HelpCircle size={16} />
              FAQ
            </div>
          </button>

          <button
            onClick={() => setActiveTab('troubleshooting')}
            class={`px-4 py-2 font-medium transition-colors ${
              activeTab() === 'troubleshooting'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted hover:text-foreground'
            }`}
          >
            <div class="flex items-center gap-2">
              <AlertCircle size={16} />
              Troubleshooting
            </div>
          </button>

          <button
            onClick={() => setActiveTab('dados')}
            class={`px-4 py-2 font-medium transition-colors ${
              activeTab() === 'dados'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted hover:text-foreground'
            }`}
          >
            <div class="flex items-center gap-2">
              <Database size={16} />
              Dados Disponíveis
            </div>
          </button>
        </div>
      </div>

      {/* Content */}
      <div class="flex-1 overflow-auto">
        {/* Tab: Guia Rápido */}
        <Show when={activeTab() === 'guia'}>
          <div class="max-w-4xl mx-auto space-y-6">
            <div class="card p-6 border">
              <h3 class="text-xl font-bold mb-4">🚀 Primeiros Passos</h3>
              <ol class="list-decimal list-inside space-y-3 text-sm leading-relaxed">
                <li><strong>Login:</strong> Use suas credenciais corporativas. Após autenticação, você será redirecionado para o Dashboard.</li>
                <li><strong>Dashboard:</strong> Visualize KPIs de negócio (total de produtos, UNEs, rupturas, valor de estoque) e gráficos principais.</li>
                <li><strong>Chat BI:</strong> Faça perguntas em linguagem natural. Ex: "Quais os 10 produtos mais vendidos?" ou "Mostre rupturas do segmento X".</li>
                <li><strong>Rupturas:</strong> Acesse produtos críticos, filtre por segmento/UNE, e exporte relatórios CSV.</li>
                <li><strong>Transferências:</strong> Solicite movimentação de estoque entre UNEs com validação automática de prioridade.</li>
              </ol>
            </div>

            <div class="card p-6 border">
              <h3 class="text-xl font-bold mb-4">💬 Dicas para usar o Chat BI</h3>
              <ul class="list-disc list-inside space-y-2 text-sm leading-relaxed">
                <li>Seja específico: "Produtos com vendas acima de 1000 unidades no segmento Alimentação"</li>
                <li>Use filtros: "Mostre estoque da UNE 42 abaixo da linha verde"</li>
                <li>Solicite gráficos: "Crie um gráfico de vendas por categoria"</li>
                <li>Compare dados: "Compare vendas de janeiro vs fevereiro"</li>
                <li>Dê feedback: Use 👍 👎 para melhorar o sistema</li>
                <li>Explore exemplos: Acesse "Exemplos" no menu para 80 perguntas pré-definidas</li>
              </ul>
            </div>

            <div class="card p-6 border">
              <h3 class="text-xl font-bold mb-4">🎯 Funcionalidades Principais</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div class="p-4 bg-secondary rounded-lg">
                  <strong class="text-primary">📊 Dashboards</strong>
                  <p class="text-muted mt-1">Monitoramento, Métricas e Rupturas Críticas com KPIs em tempo real</p>
                </div>
                <div class="p-4 bg-secondary rounded-lg">
                  <strong class="text-primary">🚚 Operacional</strong>
                  <p class="text-muted mt-1">Transferências e Relatórios com validação e histórico completo</p>
                </div>
                <div class="p-4 bg-secondary rounded-lg">
                  <strong class="text-primary">🤖 Inteligência</strong>
                  <p class="text-muted mt-1">Chat BI, Exemplos, Aprendizado e Playground para testes</p>
                </div>
                <div class="p-4 bg-secondary rounded-lg">
                  <strong class="text-primary">⚙️ Sistema</strong>
                  <p class="text-muted mt-1">Diagnóstico DB, Alterar Senha e Administração de usuários</p>
                </div>
              </div>
            </div>
          </div>
        </Show>

        {/* Tab: FAQ */}
        <Show when={activeTab() === 'faq'}>
          <div class="max-w-4xl mx-auto space-y-4">
            {/* Search */}
            <div class="relative">
              <Search size={20} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
              <input
                type="text"
                class="w-full pl-10 pr-4 py-3 bg-card border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Buscar perguntas..."
                value={searchTerm()}
                onInput={(e) => setSearchTerm(e.currentTarget.value)}
              />
            </div>

            {/* FAQ List */}
            <div class="space-y-2">
              <For each={filteredFAQ()}>
                {(item, index) => (
                  <div class="card border">
                    <button
                      onClick={() => setExpandedFAQ(expandedFAQ() === index() ? null : index())}
                      class="w-full p-4 text-left flex items-center justify-between hover:bg-secondary/50 transition-colors"
                    >
                      <span class="font-semibold">{item.pergunta}</span>
                      <Show
                        when={expandedFAQ() === index()}
                        fallback={<ChevronDown size={20} class="text-muted" />}
                      >
                        <ChevronUp size={20} class="text-primary" />
                      </Show>
                    </button>
                    <Show when={expandedFAQ() === index()}>
                      <div class="px-4 pb-4 text-sm text-muted leading-relaxed border-t pt-4">
                        {item.resposta}
                      </div>
                    </Show>
                  </div>
                )}
              </For>
            </div>

            <Show when={filteredFAQ().length === 0}>
              <div class="text-center p-12">
                <Search size={48} class="mx-auto mb-4 opacity-20" />
                <p class="text-muted">Nenhuma pergunta encontrada</p>
              </div>
            </Show>
          </div>
        </Show>

        {/* Tab: Troubleshooting */}
        <Show when={activeTab() === 'troubleshooting'}>
          <div class="max-w-4xl mx-auto space-y-4">
            <For each={TROUBLESHOOTING_ITEMS}>
              {(item) => (
                <div class="card p-6 border">
                  <div class="flex items-start gap-3 mb-4">
                    <div class="p-2 bg-red-500/10 text-red-500 rounded">
                      <AlertCircle size={20} />
                    </div>
                    <h4 class="font-bold text-lg flex-1">{item.problema}</h4>
                  </div>
                  <div class="pl-11">
                    <div class="text-sm font-medium text-primary mb-2">Soluções:</div>
                    <ol class="list-decimal list-inside space-y-1 text-sm text-muted">
                      <For each={item.solucao}>
                        {(solucao) => <li>{solucao}</li>}
                      </For>
                    </ol>
                  </div>
                </div>
              )}
            </For>
          </div>
        </Show>

        {/* Tab: Dados Disponíveis */}
        <Show when={activeTab() === 'dados'}>
          <div class="max-w-4xl mx-auto space-y-6">
            <div class="card p-6 border">
              <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
                <Database size={24} />
                Estrutura de Dados
              </h3>
              <p class="text-sm text-muted mb-4">
                O sistema utiliza dados de produtos, vendas e estoque armazenados em arquivos Parquet.
                Principal fonte: <code class="px-2 py-1 bg-secondary rounded">admmat.parquet</code>
              </p>

              <div class="space-y-4">
                <div>
                  <h4 class="font-semibold mb-2">📦 Campos Principais</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    <div class="p-2 bg-secondary rounded"><code>PRODUTO</code> - Código do produto</div>
                    <div class="p-2 bg-secondary rounded"><code>NOME</code> - Nome do produto</div>
                    <div class="p-2 bg-secondary rounded"><code>UNE</code> - Unidade de negócio</div>
                    <div class="p-2 bg-secondary rounded"><code>CATEGORIA</code> - Categoria do produto</div>
                    <div class="p-2 bg-secondary rounded"><code>SEGMENTO</code> - Segmento comercial</div>
                    <div class="p-2 bg-secondary rounded"><code>FABRICANTE</code> - Fabricante/marca</div>
                  </div>
                </div>

                <div>
                  <h4 class="font-semibold mb-2">📊 Estoque</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    <div class="p-2 bg-secondary rounded"><code>ESTOQUE_LOJA</code> - Estoque na UNE</div>
                    <div class="p-2 bg-secondary rounded"><code>ESTOQUE_CD</code> - Estoque no Centro de Distribuição</div>
                    <div class="p-2 bg-secondary rounded"><code>ESTOQUE_LV</code> - Linha Verde (mínimo)</div>
                    <div class="p-2 bg-secondary rounded"><code>ESTOQUE_LR</code> - Linha Vermelha (crítico)</div>
                  </div>
                </div>

                <div>
                  <h4 class="font-semibold mb-2">💰 Vendas e Valores</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    <div class="p-2 bg-secondary rounded"><code>VENDA_30DD</code> - Vendas últimos 30 dias</div>
                    <div class="p-2 bg-secondary rounded"><code>VENDA_90DD</code> - Vendas últimos 90 dias</div>
                    <div class="p-2 bg-secondary rounded"><code>PRECO_VENDA</code> - Preço de venda</div>
                    <div class="p-2 bg-secondary rounded"><code>CUSTO</code> - Custo do produto</div>
                  </div>
                </div>

                <div>
                  <h4 class="font-semibold mb-2">📈 Métricas Calculadas</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    <div class="p-2 bg-secondary rounded"><code>CRITICIDADE_PCT</code> - % de criticidade de ruptura</div>
                    <div class="p-2 bg-secondary rounded"><code>NECESSIDADE</code> - Quantidade necessária para reposição</div>
                    <div class="p-2 bg-secondary rounded"><code>GIRO_ESTOQUE</code> - Taxa de giro (vendas/estoque)</div>
                    <div class="p-2 bg-secondary rounded"><code>MARGEM</code> - Margem de lucro</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="card p-6 border bg-blue-500/5 border-blue-500/30">
              <h4 class="font-semibold mb-2 text-blue-400">💡 Dica para Desenvolvedores</h4>
              <p class="text-sm text-muted leading-relaxed">
                Para consultar o schema completo dos dados Parquet, acesse a página <strong>Diagnóstico DB</strong> no menu Sistema.
                Lá você encontrará informações detalhadas sobre colunas, tipos de dados e estatísticas das tabelas disponíveis.
              </p>
            </div>
          </div>
        </Show>
      </div>
    </div>
  );
}
