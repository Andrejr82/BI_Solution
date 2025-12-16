import { createSignal, createEffect, onMount, For, Show } from 'solid-js';
import { createStore } from 'solid-js/store';
import { Truck, Search, Plus, Trash2, ShoppingCart, AlertTriangle, CheckCircle, Package, ArrowRight } from 'lucide-solid';
import api from '../lib/api';

// Types
type TransferMode = 'UNE - UNE' | 'UNE - UNES' | 'UNES - UNES';

interface Product {
  produto_id: number;
  nome: string;
  segmento: string;
  fabricante: string;
  estoque_loja: number;
  estoque_cd: number;
  vendas_30dd: number;
  unes: number;
}

interface UNE {
  une: number;
  total_produtos: number;
  estoque_total: number;
}

interface CartItem {
  produto_id: number;
  produto_nome: string;
  une_origem: number;
  une_destino: number[];
  quantidade: number;
  score?: number;
  nivel_urgencia?: string;
}

interface ValidationResult {
  status: string;
  mensagem: string;
  score_prioridade?: number;
  nivel_urgencia?: string;
}

export default function Transfers() {
  // Estado principal
  const [mode, setMode] = createSignal<TransferMode>('1→1');
  const [unes, setUnes] = createSignal<UNE[]>([]);
  const [products, setProducts] = createSignal<Product[]>([]);
  const [cart, setCart] = createStore<{ items: CartItem[] }>({ items: [] });

  // Filtros disponíveis
  const [availableSegmentos, setAvailableSegmentos] = createSignal<string[]>([]);
  const [availableFabricantes, setAvailableFabricantes] = createSignal<string[]>([]);

  // Filtros de busca
  const [searchSegmento, setSearchSegmento] = createSignal('');
  const [searchFabricante, setSearchFabricante] = createSignal('');
  const [searchEstoqueMin, setSearchEstoqueMin] = createSignal<number | ''>('');

  // Seleção de produto/UNE para adicionar ao carrinho
  const [selectedProducts, setSelectedProducts] = createSignal<Product[]>([]);
  const [selectedUneOrigem, setSelectedUneOrigem] = createSignal<number | ''>('');
  const [selectedUnesOrigem, setSelectedUnesOrigem] = createSignal<number[]>([]);
  const [selectedUnesDestino, setSelectedUnesDestino] = createSignal<number[]>([]);
  const [quantidade, setQuantidade] = createSignal<number | ''>('');

  // Estados UI
  const [loading, setLoading] = createSignal(false);
  const [searching, setSearching] = createSignal(false);
  const [validating, setValidating] = createSignal(false);
  const [creating, setCreating] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);
  const [success, setSuccess] = createSignal<string | null>(null);
  const [validationResult, setValidationResult] = createSignal<ValidationResult | null>(null);

  // Toggle selection of a product
  const toggleProductSelection = (product: Product) => {
    const current = selectedProducts();
    const exists = current.find(p => p.produto_id === product.produto_id);
    
    if (exists) {
      setSelectedProducts(current.filter(p => p.produto_id !== product.produto_id));
    } else {
      setSelectedProducts([...current, product]);
    }
  };

  // Carregar filtros disponíveis
  const loadFilters = async (segmento?: string) => {
    try {
      const params = segmento ? { segmento } : {};
      const response = await api.get<{ segmentos: string[]; fabricantes: string[] }>('/transfers/filters', { params });
      
      // Se não tem segmento filtrado (inicialização), carrega lista completa de segmentos
      if (!segmento) {
        setAvailableSegmentos(response.data.segmentos);
      }
      // Sempre atualiza fabricantes baseado no filtro (ou falta dele)
      setAvailableFabricantes(response.data.fabricantes);
    } catch (err: any) {
      console.error('Erro ao carregar filtros:', err);
    }
  };

  // Carregar UNEs disponíveis
  const loadUnes = async () => {
    try {
      const response = await api.get<UNE[]>('/transfers/unes');
      setUnes(response.data);
      
      // Context7 Best Practice: Auto-select if only one option is available
      if (response.data.length === 1) {
        const singleUne = response.data[0].une;
        // Apply selection based on current mode
        if (mode() === 'N→N') {
          // Only select if empty to avoid overwriting user choice during reloads (if any)
          if (selectedUnesOrigem().length === 0) {
            setSelectedUnesOrigem([singleUne]);
          }
        } else {
          // Modes 1→1 and 1→N
          if (!selectedUneOrigem()) {
            setSelectedUneOrigem(singleUne);
          }
        }
      }
    } catch (err: any) {
      console.error('Erro ao carregar UNEs:', err);
    }
  };

  // Re-apply auto-selection when mode changes, if applicable
  createEffect(() => {
    const currentUnes = unes();
    if (currentUnes.length === 1) {
        const singleUne = currentUnes[0].une;
        if (mode() === 'UNES - UNES') {
          if (selectedUnesOrigem().length === 0) setSelectedUnesOrigem([singleUne]);
        } else {
          // Modes UNE - UNE and UNE - UNES
          if (!selectedUneOrigem()) {
            setSelectedUneOrigem(singleUne);
          }
        }
    }
  });

  // Buscar produtos
  const searchProducts = async () => {
    setSearching(true);
    setError(null);
    try {
      const response = await api.post<Product[]>('/transfers/products/search', {
        segmento: searchSegmento() || undefined,
        fabricante: searchFabricante() || undefined,
        estoque_min: searchEstoqueMin() || undefined,
        limit: 50
      });
      setProducts(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao buscar produtos');
    } finally {
      setSearching(false);
    }
  };

  // Adicionar item ao carrinho
  const addToCart = async () => {
    // Validar seleções baseado no modo
    const selectedOrigens = mode() === 'UNES - UNES' ? selectedUnesOrigem() : selectedUneOrigem() ? [selectedUneOrigem() as number] : [];
    
    if (selectedProducts().length === 0 || selectedOrigens.length === 0 || selectedUnesDestino().length === 0 || !quantidade()) {
      setError(`Preencha todos os campos para adicionar ao carrinho (Modo ${mode()})`);
      return;
    }

    const qtd = quantidade() as number;
    setValidating(true);
    
    try {
      const allNewItems: CartItem[] = [];
      const firstOrigem = selectedOrigens[0];
      const firstDestino = selectedUnesDestino()[0];

      // Validate and create items for EACH selected product
      const promises = selectedProducts().map(async (product) => {
          const validationResponse = await api.post<ValidationResult>('/transfers/validate', {
            produto_id: product.produto_id,
            une_origem: firstOrigem,
            une_destino: firstDestino,
            quantidade: qtd,
            solicitante_id: 'temp'
          });

          return selectedOrigens.map(origem => ({
            produto_id: product.produto_id,
            produto_nome: product.nome,
            une_origem: origem,
            une_destino: selectedUnesDestino(),
            quantidade: qtd,
            score: validationResponse.data.score_prioridade,
            nivel_urgencia: validationResponse.data.nivel_urgencia
          }));
      });

      const results = await Promise.all(promises);
      results.forEach(items => allNewItems.push(...items));

      setCart('items', [...cart.items, ...allNewItems]);
      setSuccess(`${allNewItems.length} item(ns) adicionado(s) ao carrinho!`);

      // Limpar seleção
      setSelectedProducts([]);
      setSelectedUneOrigem('');
      setSelectedUnesOrigem([]);
      setSelectedUnesDestino([]);
      setQuantidade('');
      setValidationResult(null);

      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao validar transferência');
    } finally {
      setValidating(false);
    }
  };

  // Remover item do carrinho
  const removeFromCart = (index: number) => {
    setCart('items', cart.items.filter((_, i) => i !== index));
  };

  // Limpar carrinho
  const clearCart = () => {
    setCart('items', []);
    setSuccess('Carrinho limpo!');
    setTimeout(() => setSuccess(null), 2000);
  };

  // Gerar solicitação
  const generateRequest = async () => {
    if (cart.items.length === 0) {
      setError('Carrinho vazio! Adicione itens primeiro.');
      return;
    }

    setCreating(true);
    setError(null);

    try {
      // Preparar payload baseado no modo
      const transfers = [];

      for (const item of cart.items) {
        for (const destino of item.une_destino) {
          transfers.push({
            produto_id: item.produto_id,
            une_origem: item.une_origem,
            une_destino: destino,
            quantidade: item.quantidade,
            solicitante_id: 'temp'
          });
        }
      }

      if (mode() === 'UNE - UNE' && transfers.length === 1) {
        // Transferência simples
        const response = await api.post('/transfers', transfers[0]);
        setSuccess(`Solicitação criada! ID: ${response.data.transfer_id}`);
      } else {
        // Transferência em massa
        const response = await api.post('/transfers/bulk', {
          items: transfers,
          modo: mode()
        });
        setSuccess(`Lote criado! ID: ${response.data.batch_id} (${transfers.length} transferências)`);
      }

      // Limpar carrinho
      setCart('items', []);

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao criar solicitação');
    } finally {
      setCreating(false);
    }
  };

  // Limpar seleções ao mudar modo
  createEffect(() => {
    mode(); // Dependency on mode changes
    setSelectedUneOrigem('');
    setSelectedUnesOrigem([]);
    setSelectedUnesDestino([]);
    setSelectedProducts([]);
    setValidationResult(null);
  });

  onMount(() => {
    loadFilters();
    loadUnes();
    searchProducts();
  });

  // Atualizar filtros (fabricantes) quando segmento mudar
  createEffect(() => {
    loadFilters(searchSegmento());
  });

  // Auto-buscar ao mudar filtros
  createEffect(() => {
    if (searchSegmento() || searchFabricante() || searchEstoqueMin()) {
      searchProducts();
    }
  });

  const getUrgencyColor = (nivel?: string) => {
    switch (nivel) {
      case 'URGENTE': return 'text-red-500';
      case 'ALTA': return 'text-orange-500';
      case 'MÉDIA': return 'text-yellow-500';
      case 'BAIXA': return 'text-green-500';
      default: return 'text-gray-500';
    }
  };

  return (
    <div class="flex flex-col h-full p-6 gap-6">
      {/* Header */}
      <div>
        <h2 class="text-2xl font-bold">Sistema de Transferências</h2>
        <p class="text-muted">Gerencie transferências de produtos entre UNEs</p>
      </div>

      {/* Error/Success Messages */}
      <Show when={error()}>
        <div class="card p-4 border-red-500 bg-red-500/10">
          <div class="flex items-center gap-2 text-red-500">
            <AlertTriangle size={20} />
            <span>{error()}</span>
          </div>
        </div>
      </Show>

      <Show when={success()}>
        <div class="card p-4 border-green-500 bg-green-500/10">
          <div class="flex items-center gap-2 text-green-500">
            <CheckCircle size={20} />
            <span>{success()}</span>
          </div>
        </div>
      </Show>

      {/* Mode Selection & UNE Origin/Destination Filters */}
      <div class="card p-4 border">
        <div class="space-y-4">
          {/* Mode Selection */}
          <div>
            <label class="text-sm font-medium mb-3 block">Modo de Transferência</label>
            <div class="flex gap-2">
              <button
                class={`btn ${mode() === 'UNE - UNE' ? 'btn-primary' : 'btn-outline'}`}
                onClick={() => setMode('UNE - UNE')}
              >
                UNE - UNE (Simples)
              </button>
              <button
                class={`btn ${mode() === 'UNE - UNES' ? 'btn-primary' : 'btn-outline'}`}
                onClick={() => setMode('UNE - UNES')}
              >
                UNE - UNES (Uma origem, várias destinos)
              </button>
              <button
                class={`btn ${mode() === 'UNES - UNES' ? 'btn-primary' : 'btn-outline'}`}
                onClick={() => setMode('UNES - UNES')}
              >
                UNES - UNES (Múltiplas origens e destinos)
              </button>
            </div>
          </div>

          {/* UNE Origin & Destination Pre-selection */}
          <div class="border-t pt-4">
            <p class="text-xs text-muted mb-3">
              ℹ️ {
                mode() === 'UNE - UNE' ? 'Selecione uma UNE de origem e uma de destino' :
                mode() === 'UNE - UNES' ? 'Selecione uma UNE de origem e múltiplos destinos' :
                'Selecione múltiplas UNEs de origem e destino'
              }
            </p>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Origin UNEs Selection */}
              <div>
                <label class="text-xs text-muted block mb-2 font-semibold">
                  UNE(s) de Origem
                  {mode() === 'N→N' && ` (${selectedUnesOrigem().length} selecionadas)`}
                </label>
                <div class="max-h-40 overflow-y-auto border rounded p-3 space-y-2 bg-muted/5">
                  <Show when={unes().length > 0} fallback={
                    <div class="text-xs text-muted p-2">Nenhuma UNE disponível</div>
                  }>
                    <For each={unes()}>
                      {(une) => {
                        const isSelectedInMode = () => mode() === 'N→N' 
                          ? selectedUnesOrigem().includes(une.une)
                          : selectedUneOrigem() === une.une;
                        
                        const toggleSelection = () => {
                          if (mode() === 'UNES - UNES') {
                            const current = selectedUnesOrigem();
                            if (current.includes(une.une)) {
                              setSelectedUnesOrigem(current.filter(u => u !== une.une));
                            } else {
                              setSelectedUnesOrigem([...current, une.une]);
                            }
                          } else {
                            // Modo UNE - UNE ou UNE - UNES
                            if (selectedUneOrigem() === une.une) {
                              setSelectedUneOrigem('');
                            } else {
                              setSelectedUneOrigem(une.une);
                            }
                          }
                        };
                        
                        return (
                          <div 
                            class={`flex items-center gap-2 text-xs cursor-pointer p-1.5 rounded transition ${
                              isSelectedInMode() ? 'bg-blue-100 dark:bg-blue-900' : 'hover:bg-muted/30'
                            }`}
                            onClick={toggleSelection}
                          >
                            <div class="flex-shrink-0">
                              {mode() === 'N→N' ? (
                                <input
                                  type="checkbox"
                                  checked={isSelectedInMode()}
                                  onClick={(e) => e.stopPropagation()}
                                  onChange={toggleSelection}
                                  class="cursor-pointer"
                                />
                              ) : (
                                <input
                                  type="radio"
                                  name="origin-une"
                                  checked={isSelectedInMode()}
                                  onClick={(e) => e.stopPropagation()}
                                  onChange={toggleSelection}
                                  class="cursor-pointer"
                                />
                              )}
                            </div>
                            <span>UNE {une.une}</span>
                            <span class="text-muted text-xs">({une.estoque_total} un.)</span>
                          </div>
                        );
                      }}
                    </For>
                  </Show>
                </div>
              </div>

              {/* Destination UNEs Selection */}
              <div>
                <label class="text-xs text-muted block mb-2 font-semibold">
                  UNE(s) de Destino
                  {(mode() === '1→N' || mode() === 'N→N') && ` (${selectedUnesDestino().length} selecionadas)`}
                </label>
                <div class="max-h-40 overflow-y-auto border rounded p-3 space-y-2 bg-muted/5">
                  <Show when={unes().length > 0} fallback={
                    <div class="text-xs text-muted p-2">Nenhuma UNE disponível</div>
                  }>
                    <For each={unes()}>
                      {(une) => {
                        const isDisabledDestino = () => mode() === 'UNE - UNE' 
                          ? selectedUneOrigem() === une.une
                          : mode() === 'UNES - UNES'
                          ? selectedUnesOrigem().includes(une.une)
                          : selectedUneOrigem() === une.une;

                        const isSelectedDestino = () => selectedUnesDestino().includes(une.une);
                        
                        const toggleDestSelection = () => {
                          if (isDisabledDestino()) return; // Impedir clique em origem
                          
                          const current = selectedUnesDestino();
                          if (current.includes(une.une)) {
                            setSelectedUnesDestino(current.filter(u => u !== une.une));
                          } else {
                            if (mode() === 'UNE - UNE' && current.length >= 1) {
                              setSelectedUnesDestino([une.une]);
                            } else {
                              setSelectedUnesDestino([...current, une.une]);
                            }
                          }
                        };

                        return (
                          <div 
                            class={`flex items-center gap-2 text-xs p-1.5 rounded transition ${
                              isDisabledDestino() 
                                ? 'opacity-50 cursor-not-allowed bg-gray-100 dark:bg-gray-800' 
                                : isSelectedDestino()
                                ? 'bg-green-100 dark:bg-green-900 cursor-pointer'
                                : 'hover:bg-muted/30 cursor-pointer'
                            }`}
                            onClick={toggleDestSelection}
                          >
                            <div class="flex-shrink-0">
                              <input
                                type="checkbox"
                                disabled={isDisabledDestino()}
                                checked={isSelectedDestino()}
                                onClick={(e) => e.stopPropagation()}
                                onChange={toggleDestSelection}
                                class={`cursor-pointer ${isDisabledDestino() ? 'opacity-50 cursor-not-allowed' : ''}`}
                              />
                            </div>
                            <span class={isDisabledDestino() ? 'line-through text-muted' : ''}>
                              UNE {une.une}
                            </span>
                            <span class="text-muted text-xs">({une.estoque_total} un.)</span>
                          </div>
                        );
                      }}
                    </For>
                  </Show>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        {/* Left Column - Product Search */}
        <div class="lg:col-span-2 flex flex-col gap-4">
          {/* Search Filters */}
          <div class="card p-4 border">
            <div class="flex items-center gap-2 mb-4">
              <Search size={20} />
              <h3 class="font-semibold">Buscar Produtos</h3>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <select
                class="input"
                value={searchSegmento()}
                onChange={(e) => setSearchSegmento(e.currentTarget.value)}
              >
                <option value="">Todos os Segmentos</option>
                <For each={availableSegmentos()}>
                  {(segmento) => <option value={segmento}>{segmento}</option>}
                </For>
              </select>

              <select
                class="input"
                value={searchFabricante()}
                onChange={(e) => setSearchFabricante(e.currentTarget.value)}
              >
                <option value="">Todos os Fabricantes</option>
                <For each={availableFabricantes()}>
                  {(fabricante) => <option value={fabricante}>{fabricante}</option>}
                </For>
              </select>

              <input
                type="number"
                placeholder="Estoque mín."
                class="input"
                value={searchEstoqueMin()}
                onInput={(e) => setSearchEstoqueMin(parseInt(e.currentTarget.value) || '')}
              />
            </div>

            <button
              class="btn btn-primary w-full mt-3 gap-2"
              onClick={searchProducts}
              disabled={searching()}
            >
              <Search size={16} />
              {searching() ? 'Buscando...' : 'Buscar'}
            </button>
          </div>

          {/* Products List */}
          <div class="card border flex-1 flex flex-col">
            <div class="p-4 border-b">
              <h3 class="font-semibold">Produtos ({products().length})</h3>
            </div>

            <div class="flex-1 overflow-y-auto">
              <Show when={products().length > 0} fallback={
                <div class="p-8 text-center text-muted">
                  <Package size={48} class="mx-auto mb-4 opacity-50" />
                  <p>Nenhum produto encontrado</p>
                </div>
              }>
                <For each={products()}>
                  {(product) => {
                    const isSelected = () => selectedProducts().some(p => p.produto_id === product.produto_id);
                    return (
                      <div
                        class={`p-3 border-b hover:bg-muted/30 cursor-pointer transition-colors ${
                          isSelected() ? 'bg-primary/10 border-primary' : ''
                        }`}
                        onClick={() => toggleProductSelection(product)}
                      >
                        <div class="flex items-start gap-3">
                          <div class="pt-1">
                            <input 
                              type="checkbox" 
                              checked={isSelected()} 
                              readOnly
                              class="cursor-pointer pointer-events-none"
                            />
                          </div>
                          <div class="flex-1 flex justify-between items-start">
                            <div>
                              <div class="font-medium text-sm">{product.nome}</div>
                              <div class="text-xs text-muted mt-1">
                                ID: {product.produto_id} • {product.segmento} • {product.fabricante}
                              </div>
                            </div>
                            <div class="text-right text-xs">
                              <div class="text-muted">Loja: {product.estoque_loja}</div>
                              <div class="text-muted">CD: {product.estoque_cd}</div>
                              <div class="text-blue-400">Vendas: {product.vendas_30dd}</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  }}
                </For>
              </Show>
            </div>
          </div>
        </div>

        {/* Right Column - Transfer Config & Cart */}
        <div class="flex flex-col gap-4">
          {/* Transfer Configuration */}
          <Show when={selectedProducts().length > 0}>
            <div class="card p-4 border">
              <Show when={selectedProducts().length === 1} fallback={
                <div class="mb-4">
                  <h3 class="font-semibold mb-3 text-sm">{selectedProducts().length} Produtos Selecionados</h3>
                  <div class="max-h-32 overflow-y-auto border rounded p-2 bg-muted/5 space-y-1">
                    <For each={selectedProducts()}>
                      {p => <div class="text-xs truncate text-muted">• {p.nome}</div>}
                    </For>
                  </div>
                </div>
              }>
                <h3 class="font-semibold mb-3 text-sm">Detalhe do Produto Selecionado</h3>

                <div class="space-y-3 mb-4">
                  <div>
                    <label class="text-xs text-muted block mb-1">Produto</label>
                    <div class="text-sm font-medium truncate">{selectedProducts()[0].nome}</div>
                  </div>

                  <div class="text-xs text-muted space-y-1">
                    <div>ID: {selectedProducts()[0].produto_id}</div>
                    <div>Segmento: {selectedProducts()[0].segmento}</div>
                    <div>Fabricante: {selectedProducts()[0].fabricante}</div>
                    <div class="mt-2 pt-2 border-t">
                      <div>Estoque Loja: <span class="text-foreground font-medium">{selectedProducts()[0].estoque_loja} un.</span></div>
                      <div>Estoque CD: <span class="text-foreground font-medium">{selectedProducts()[0].estoque_cd} un.</span></div>
                      <div>Vendas (30dd): <span class="text-blue-400 font-medium">{selectedProducts()[0].vendas_30dd}</span></div>
                    </div>
                  </div>
                </div>
              </Show>

              <div class="space-y-3">
                <div>
                  <label class="text-xs text-muted block mb-1">Quantidade a Transferir {selectedProducts().length > 1 ? '(para cada)' : ''}</label>
                  <input
                    type="number"
                    class="input w-full"
                    placeholder="0"
                    value={quantidade()}
                    onInput={(e) => setQuantidade(parseInt(e.currentTarget.value) || '')}
                  />
                </div>

                <button
                  class="btn btn-primary w-full gap-2 text-sm"
                  onClick={addToCart}
                  disabled={validating() || selectedProducts().length === 0 || 
                    (mode() === 'N→N' ? selectedUnesOrigem().length === 0 : !selectedUneOrigem()) || 
                    selectedUnesDestino().length === 0 || !quantidade()}
                >
                  <Plus size={16} />
                  {validating() ? 'Validando...' : `Adicionar ${selectedProducts().length > 1 ? `(${selectedProducts().length})` : ''} ao Carrinho`}
                </button>
              </div>
            </div>
          </Show>

          {/* Cart */}
          <div class="card border flex-1 flex flex-col">
            <div class="p-3 border-b flex justify-between items-center">
              <div class="flex items-center gap-2">
                <ShoppingCart size={18} />
                <h3 class="font-semibold text-sm">Carrinho ({cart.items.length})</h3>
              </div>
              <Show when={cart.items.length > 0}>
                <button
                  class="text-xs text-red-400 hover:text-red-300"
                  onClick={clearCart}
                >
                  Limpar
                </button>
              </Show>
            </div>

            <div class="flex-1 overflow-y-auto">
              <Show when={cart.items.length > 0} fallback={
                <div class="p-6 text-center text-muted text-sm">
                  <ShoppingCart size={32} class="mx-auto mb-2 opacity-50" />
                  <p>Carrinho vazio</p>
                </div>
              }>
                <For each={cart.items}>
                  {(item, index) => (
                    <div class="p-3 border-b text-xs">
                      <div class="flex justify-between items-start mb-2">
                        <div class="flex-1 font-medium">{item.produto_nome}</div>
                        <button
                          class="text-red-400 hover:text-red-300"
                          onClick={() => removeFromCart(index())}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>

                      <div class="space-y-1 text-muted">
                        <div class="flex items-center gap-1">
                          <span>UNE {item.une_origem}</span>
                          <ArrowRight size={12} />
                          <span>UNE {item.une_destino.join(', ')}</span>
                        </div>
                        <div>Qtd: {item.quantidade} un.</div>
                        <Show when={item.score !== undefined}>
                          <div class="flex items-center gap-2">
                            <span>Score: {item.score}</span>
                            <span class={`font-semibold ${getUrgencyColor(item.nivel_urgencia)}`}>
                              {item.nivel_urgencia}
                            </span>
                          </div>
                        </Show>
                      </div>
                    </div>
                  )}
                </For>
              </Show>
            </div>

            <Show when={cart.items.length > 0}>
              <div class="p-3 border-t">
                <button
                  class="btn btn-primary w-full gap-2 text-sm"
                  onClick={generateRequest}
                  disabled={creating()}
                >
                  <Truck size={16} />
                  {creating() ? 'Gerando...' : 'Gerar Solicitação'}
                </button>
              </div>
            </Show>
          </div>
        </div>
      </div>
    </div>
  );
}
