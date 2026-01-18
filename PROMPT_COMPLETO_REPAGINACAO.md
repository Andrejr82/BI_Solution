# 🤖 PROMPT COMPLETO PARA REPAGINAÇÃO - LOJAS CAÇULA BI

Use este prompt com qualquer LLM (Claude, GPT-4, Gemini) para aplicar a modernização completa no projeto.

---

## 📋 PROMPT PARA A LLM

```
Você é um desenvolvedor frontend sênior especializado em SolidJS e design systems modernos. 

Sua tarefa é modernizar completamente a interface do sistema "Caçulinha BI" das Lojas Caçula, aplicando as últimas tendências de design 2024-2025 mantendo fidelidade à identidade visual da marca.

## CONTEXTO DO PROJETO

**Tecnologias:**
- Frontend: SolidJS + TypeScript
- Styling: Tailwind CSS + DaisyUI
- Gráficos: Plotly.js
- Roteamento: @solidjs/router

**Estrutura de Pastas:**
```
frontend-solid/
├── src/
│   ├── components/     # Componentes reutilizáveis
│   ├── pages/          # Páginas do sistema (AQUI VAMOS TRABALHAR)
│   ├── lib/            # Utils e API
│   ├── store/          # Estado global
│   └── styles/         # CSS global
```

## IDENTIDADE VISUAL - LOJAS CAÇULA

**Cores Oficiais (extraídas de www.lojascacula.com):**

```typescript
const coresBrand = {
  // Verde Caçula - Cor Principal
  verde: {
    50: '#F2F9E8',
    100: '#E5F3D1',
    200: '#CCE7A3',
    300: '#B2DB75',
    400: '#99CF47',
    500: '#78B928',  // ← PRINCIPAL
    600: '#609420',
    700: '#486F18',
    800: '#304A10',
    900: '#182508',
  },
  
  // Vermelho Pétala - Accent
  vermelho: {
    50: '#FEE8E9',
    100: '#FDD1D3',
    500: '#ED1C24',  // ← PRINCIPAL
    600: '#BE161D',
  },
  
  // Amarelo Caçula - Secundário
  amarelo: {
    50: '#FFF9E5',
    100: '#FFF3CB',
    500: '#FDB913',  // ← PRINCIPAL
    600: '#CA940F',
  },
};

const gradientes = {
  primary: 'linear-gradient(135deg, #78B928 0%, #99CF47 100%)',
  accent: 'linear-gradient(135deg, #ED1C24 0%, #F7474F 100%)',
  secondary: 'linear-gradient(135deg, #FDB913 0%, #FFCF2F 100%)',
  hero: 'linear-gradient(135deg, #78B928 0%, #FDB913 50%, #ED1C24 100%)',
};
```

**Quando Usar Cada Cor:**
- 🟢 **Verde (#78B928)**: CTAs principais, sucesso, crescimento, métricas positivas
- 🔴 **Vermelho (#ED1C24)**: Alertas, rupturas, urgências, erros
- 🟡 **Amarelo (#FDB913)**: Destaques secundários, avisos, informações importantes
- ⚫ **Neutros**: Textos, fundos, bordas

## TENDÊNCIAS DE DESIGN 2024-2025 A APLICAR

### 1. **Glassmorphism (Efeito Vidro Fosco)**
```tsx
// Aplicar em cards, modais, painéis
class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border border-white/20"
```

### 2. **Micro-interações e Hover States**
```tsx
// Todos os elementos interativos
class="transition-all duration-300 hover:scale-105 hover:shadow-xl"
```

### 3. **Typography Forte e Hierarquizada**
```tsx
// Headers principais
<h1 class="text-5xl md:text-6xl font-black tracking-tight">
  <span class="bg-gradient-to-r from-[#78B928] to-[#99CF47] bg-clip-text text-transparent">
    Título
  </span>
</h1>

// Subtítulos
<p class="text-xl text-gray-600 dark:text-gray-400 leading-relaxed">
  Subtítulo
</p>
```

### 4. **Espaçamento Generoso (Grid 8px)**
```tsx
// Aplicar consistentemente
gap-6    // 24px
gap-8    // 32px
p-8      // 32px
py-20    // 80px
```

### 5. **Border Radius Grandes**
```tsx
rounded-2xl   // 16px - Cards médios
rounded-3xl   // 24px - Cards grandes, modais
```

### 6. **Sombras Elevadas**
```tsx
shadow-xl              // Padrão
shadow-2xl             // Destaque
shadow-[#78B928]/20    // Glow verde (branded)
```

## COMPONENTES MODERNOS A USAR

### ModernCard (criar em components/)
```tsx
interface ModernCardProps {
  variant?: 'default' | 'glass' | 'gradient' | 'elevated';
  hover?: boolean;
  class?: string;
  children: JSX.Element;
}

export const ModernCard: ParentComponent<ModernCardProps> = (props) => {
  const variants = {
    default: "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700",
    glass: "bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border border-white/20",
    gradient: "bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900",
    elevated: "bg-white dark:bg-gray-800 shadow-xl",
  };
  
  return (
    <div class={`
      rounded-3xl transition-all duration-300
      ${variants[props.variant || 'default']}
      ${props.hover ? 'hover:shadow-2xl hover:-translate-y-2 cursor-pointer' : ''}
      ${props.class || ''}
    `}>
      {props.children}
    </div>
  );
};
```

### StatCard (para KPIs no Dashboard)
```tsx
interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: JSX.Element;
  variant?: 'primary' | 'accent' | 'secondary' | 'neutral';
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
}

export const StatCard: Component<StatCardProps> = (props) => {
  const variantStyles = {
    primary: {
      bg: 'bg-gradient-to-br from-[#78B928]/10 to-[#78B928]/5',
      icon: 'bg-[#78B928]/20 text-[#78B928]',
      border: 'border-[#78B928]/20',
    },
    accent: {
      bg: 'bg-gradient-to-br from-[#ED1C24]/10 to-[#ED1C24]/5',
      icon: 'bg-[#ED1C24]/20 text-[#ED1C24]',
      border: 'border-[#ED1C24]/20',
    },
    // ... outros variants
  };
  
  const style = variantStyles[props.variant || 'neutral'];
  
  return (
    <div class={`
      p-6 rounded-2xl border ${style.bg} ${style.border}
      hover:shadow-xl hover:-translate-y-1 transition-all duration-300
    `}>
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <p class="text-sm font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wider mb-2">
            {props.title}
          </p>
          <h3 class="text-4xl font-black text-gray-900 dark:text-white mb-1">
            {props.value}
          </h3>
          {props.subtitle && (
            <p class="text-xs text-gray-500">{props.subtitle}</p>
          )}
          {props.trend && (
            <div class={`flex items-center gap-1 mt-2 text-sm font-semibold ${
              props.trend === 'up' ? 'text-green-500' : 
              props.trend === 'down' ? 'text-red-500' : 'text-gray-500'
            }`}>
              {props.trend === 'up' ? '↑' : props.trend === 'down' ? '↓' : '→'}
              <span>{props.trendValue}</span>
            </div>
          )}
        </div>
        {props.icon && (
          <div class={`p-3 rounded-xl ${style.icon}`}>
            {props.icon}
          </div>
        )}
      </div>
    </div>
  );
};
```

### ModernButton
```tsx
interface ModernButtonProps {
  variant?: 'primary' | 'accent' | 'secondary' | 'outline' | 'ghost' | 'gradient';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  icon?: JSX.Element;
  children: JSX.Element;
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
}

export const ModernButton: ParentComponent<ModernButtonProps> = (props) => {
  const variants = {
    primary: 'bg-[#78B928] hover:bg-[#609420] text-white shadow-md hover:shadow-lg',
    accent: 'bg-[#ED1C24] hover:bg-[#BE161D] text-white shadow-md hover:shadow-lg',
    gradient: 'bg-gradient-to-r from-[#78B928] to-[#99CF47] hover:from-[#609420] hover:to-[#78B928] text-white shadow-xl',
    outline: 'border-2 border-[#78B928] text-[#78B928] hover:bg-[#78B928] hover:text-white',
    ghost: 'text-[#78B928] hover:bg-[#78B928]/10',
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
    xl: 'px-10 py-5 text-xl',
  };
  
  return (
    <button
      disabled={props.disabled || props.loading}
      onClick={props.onClick}
      class={`
        inline-flex items-center justify-center gap-2 rounded-2xl font-bold
        transition-all duration-300 disabled:opacity-50
        ${sizes[props.size || 'md']}
        ${variants[props.variant || 'primary']}
        hover:scale-105
      `}
    >
      {props.loading && (
        <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      )}
      {props.icon}
      {props.children}
    </button>
  );
};
```

### SectionHeader (para headers de páginas)
```tsx
interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  icon?: JSX.Element;
  action?: JSX.Element;
}

export const SectionHeader: Component<SectionHeaderProps> = (props) => {
  return (
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
      <div class="flex items-center gap-4">
        {props.icon && (
          <div class="p-3 bg-gradient-to-br from-[#78B928] to-[#99CF47] rounded-xl text-white shadow-lg">
            {props.icon}
          </div>
        )}
        <div>
          <h2 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight">
            {props.title}
          </h2>
          {props.subtitle && (
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {props.subtitle}
            </p>
          )}
        </div>
      </div>
      {props.action}
    </div>
  );
};
```

## PÁGINAS A MODERNIZAR (PRIORIDADE)

### 1. DASHBOARD (Dashboard.tsx) - 🔴 PRIORIDADE MÁXIMA

**Mudanças:**

1. **Header Executivo:**
```tsx
// Substituir header atual por:
<div class="bg-gradient-to-br from-[#78B928]/10 via-[#FDB913]/5 to-white dark:to-gray-900 rounded-3xl p-8 mb-8">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-5xl font-black bg-gradient-to-r from-[#78B928] to-[#609420] bg-clip-text text-transparent">
        Olá, {auth.user()?.username}
      </h1>
      <div class="flex items-center gap-3 mt-4">
        <span class={`
          px-4 py-2 rounded-full text-sm font-bold border-2
          ${businessStatus() === 'healthy' 
            ? 'bg-[#78B928]/10 text-[#78B928] border-[#78B928]/20' 
            : 'bg-[#ED1C24]/10 text-[#ED1C24] border-[#ED1C24]/20'
          }
        `}>
          {businessStatus() === 'healthy' ? '✓ Operação Saudável' : '⚠ Atenção Necessária'}
        </span>
        <span class="text-sm text-gray-600">Visão geral do desempenho</span>
      </div>
    </div>
    <ModernButton variant="ghost" size="sm" icon={<RefreshCw />} onClick={loadKPIs}>
      Atualizar
    </ModernButton>
  </div>
</div>
```

2. **KPI Cards (converter para StatCard):**
```tsx
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  <StatCard
    title="Valor em Estoque"
    value={kpis()!.valor_estoque.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
    subtitle="Capital imobilizado"
    icon={<DollarSign size={28} />}
    variant="primary"
    trend="up"
    trendValue="+5.2%"
  />
  
  <StatCard
    title="Rupturas"
    value={kpis()!.produtos_ruptura}
    subtitle={kpis()!.produtos_ruptura > 0 ? 'Produtos precisam atenção' : 'Estoque saudável'}
    icon={<AlertTriangle size={28} />}
    variant={kpis()!.produtos_ruptura > 0 ? 'accent' : 'primary'}
    trend={kpis()!.produtos_ruptura > 0 ? 'up' : 'neutral'}
  />
  
  <StatCard
    title="Mix de Produtos"
    value={kpis()!.total_produtos}
    subtitle="SKUs ativos no catálogo"
    icon={<Package size={28} />}
    variant="neutral"
  />
  
  <StatCard
    title="Cobertura"
    value={kpis()!.total_unes}
    subtitle="Lojas/UNEs monitoradas"
    icon={<ShoppingCart size={28} />}
    variant="secondary"
  />
</div>
```

3. **Charts com Glassmorphism:**
```tsx
<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
  <ModernCard variant="glass" class="p-8 shadow-2xl">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h3 class="text-xl font-black text-gray-900 dark:text-white">
          Quais produtos impulsionam as vendas?
        </h3>
        <p class="text-sm text-gray-600 mt-1">Top 10 produtos por volume</p>
      </div>
      <ChartDownloadButton chartId="top-produtos" />
    </div>
    <PlotlyChart chartSpec={topProdutosChart} height="380px" />
  </ModernCard>
  
  {/* Repetir para outros charts */}
</div>
```

### 2. RUPTURAS (Rupturas.tsx) - 🔴 ALTA PRIORIDADE

**Mudanças:**

1. **Header Dramático (Ruptura = URGENTE):**
```tsx
<div class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#ED1C24] to-[#F7474F] p-10 text-white shadow-2xl mb-8">
  {/* Overlay escuro */}
  <div class="absolute inset-0 bg-black/10"></div>
  
  {/* Conteúdo */}
  <div class="relative z-10 flex items-center gap-6">
    <div class="p-4 bg-white/20 backdrop-blur-sm rounded-2xl">
      <AlertTriangle size={56} />
    </div>
    <div class="flex-1">
      <h1 class="text-5xl font-black mb-2">Rupturas Críticas</h1>
      <p class="text-red-100 text-lg">CD zerado + Estoque loja abaixo da Linha Verde</p>
    </div>
  </div>
  
  {/* Padrão de alerta animado */}
  <div class="absolute right-0 top-0 h-full w-1/3 opacity-10">
    <div class="h-full w-full" style="background: repeating-linear-gradient(45deg, transparent, transparent 10px, white 10px, white 20px)"></div>
  </div>
</div>
```

2. **Summary Cards (Urgência Visual):**
```tsx
<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
  <ModernCard variant="glass" class="p-6 bg-gradient-to-br from-[#ED1C24]/10 to-[#ED1C24]/5 border-2 border-[#ED1C24]/30">
    <div class="flex items-center gap-4">
      <div class="p-4 bg-[#ED1C24]/20 rounded-2xl">
        <PackageX size={36} class="text-[#ED1C24]" />
      </div>
      <div>
        <p class="text-xs text-gray-600 uppercase tracking-wider font-bold">Total Rupturas</p>
        <h3 class="text-5xl font-black text-[#ED1C24]">{summary().total}</h3>
      </div>
    </div>
  </ModernCard>
  
  <ModernCard variant="glass" class="p-6 bg-gradient-to-br from-orange-500/10 to-orange-500/5 border-2 border-orange-500/30">
    <div class="flex items-center gap-4">
      <div class="p-4 bg-orange-500/20 rounded-2xl">
        <AlertTriangle size={36} class="text-orange-500" />
      </div>
      <div>
        <p class="text-xs text-gray-600 uppercase tracking-wider font-bold">Criticidade Alta</p>
        <h3 class="text-5xl font-black text-orange-500">{summary().criticos}</h3>
      </div>
    </div>
  </ModernCard>
  
  <ModernCard variant="glass" class="p-6 bg-gradient-to-br from-blue-500/10 to-blue-500/5 border-2 border-blue-500/30">
    <div class="flex items-center gap-4">
      <div class="p-4 bg-blue-500/20 rounded-2xl">
        <TrendingUp size={36} class="text-blue-500" />
      </div>
      <div>
        <p class="text-xs text-gray-600 uppercase tracking-wider font-bold">Taxa Crítica</p>
        <h3 class="text-5xl font-black text-blue-500">
          {summary().total > 0 ? ((summary().criticos / summary().total) * 100).toFixed(0) : 0}%
        </h3>
      </div>
    </div>
  </ModernCard>
</div>
```

3. **Tabela Moderna:**
```tsx
<ModernCard variant="elevated" class="overflow-hidden">
  <div class="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 p-6 border-b">
    <h3 class="text-xl font-black">Produtos em Ruptura Crítica ({data().length})</h3>
  </div>
  
  <div class="overflow-x-auto">
    <table class="w-full">
      <thead class="bg-gray-100/80 dark:bg-gray-800/80 backdrop-blur-sm sticky top-0 z-10">
        <tr class="text-xs uppercase tracking-wider font-bold text-gray-600 dark:text-gray-400">
          <th class="px-6 py-4 text-left">Produto</th>
          <th class="px-6 py-4 text-left">UNE</th>
          <th class="px-6 py-4 text-right">Venda 30d</th>
          <th class="px-6 py-4 text-right">Estoque Loja</th>
          <th class="px-6 py-4 text-right">Linha Verde</th>
          <th class="px-6 py-4 text-right">Necessidade</th>
          <th class="px-6 py-4 text-center">Criticidade</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
        <For each={data()}>
          {(item) => (
            <tr class="hover:bg-[#78B928]/5 transition-all duration-200 group">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                  <div>
                    <div class="font-semibold text-gray-900 dark:text-white group-hover:text-[#78B928] transition-colors">
                      {item.NOME}
                    </div>
                    <div class="text-xs text-gray-500 font-mono">{item.PRODUTO}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex flex-col">
                  <span class="px-3 py-1 bg-gray-100 dark:bg-gray-800 rounded-lg text-xs font-mono font-bold w-fit">
                    {item.UNE}
                  </span>
                  <span class="text-xs text-gray-500 mt-1">{item.UNE_NOME}</span>
                </div>
              </td>
              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-end gap-2 text-green-600 font-semibold">
                  <TrendingUp size={16} />
                  {Math.round(item.VENDA_30DD)}
                </div>
              </td>
              <td class="px-6 py-4 text-right">
                <span class="text-red-500 font-bold">{Math.round(item.ESTOQUE_UNE)}</span>
              </td>
              <td class="px-6 py-4 text-right">
                <span class="text-blue-500 font-bold">{Math.round(item.ESTOQUE_LV)}</span>
              </td>
              <td class="px-6 py-4 text-right">
                <span class="text-orange-500 font-black text-lg">
                  {Math.round(item.NECESSIDADE)} un
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="flex flex-col items-center gap-2">
                  <span class={`
                    px-3 py-1 rounded-full text-xs font-bold border-2
                    ${item.CRITICIDADE_PCT >= 75 ? 'bg-red-500/10 text-red-500 border-red-500/30' :
                      item.CRITICIDADE_PCT >= 50 ? 'bg-orange-500/10 text-orange-500 border-orange-500/30' :
                      item.CRITICIDADE_PCT >= 25 ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/30' :
                      'bg-blue-500/10 text-blue-500 border-blue-500/30'
                    }
                  `}>
                    {item.CRITICIDADE_PCT >= 75 ? 'CRÍTICO' :
                     item.CRITICIDADE_PCT >= 50 ? 'ALTO' :
                     item.CRITICIDADE_PCT >= 25 ? 'MÉDIO' : 'BAIXO'}
                  </span>
                  <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                    <div 
                      class={`h-full rounded-full transition-all ${
                        item.CRITICIDADE_PCT >= 75 ? 'bg-red-500' :
                        item.CRITICIDADE_PCT >= 50 ? 'bg-orange-500' :
                        item.CRITICIDADE_PCT >= 25 ? 'bg-yellow-500' : 'bg-blue-500'
                      }`}
                      style={`width: ${item.CRITICIDADE_PCT}%`}
                    />
                  </div>
                  <span class="text-xs text-gray-500 font-mono">{item.CRITICIDADE_PCT.toFixed(0)}%</span>
                </div>
              </td>
            </tr>
          )}
        </For>
      </tbody>
    </table>
  </div>
</ModernCard>
```

### 3. ANALYTICS (Analytics.tsx) - 🟡 MÉDIA PRIORIDADE

**Mudanças:**

1. **Hero Section:**
```tsx
<div class="bg-gradient-to-br from-[#78B928]/10 via-[#FDB913]/5 to-[#ED1C24]/10 rounded-3xl p-8 mb-8">
  <SectionHeader
    title="Analytics Avançado"
    subtitle="Análise de vendas, estoque e distribuição ABC (Pareto)"
    icon={<BarChart3 size={32} />}
    action={
      <ModernButton variant="gradient" icon={<RefreshCw />} onClick={loadData} disabled={loading()}>
        Atualizar Dados
      </ModernButton>
    }
  />
</div>
```

2. **Filter Panel (Glassmorphism):**
```tsx
<ModernCard variant="glass" class="p-6 border-2 border-[#78B928]/20 mb-8">
  <div class="flex items-center gap-3 mb-6">
    <div class="p-2 bg-[#78B928]/20 rounded-lg">
      <Filter size={24} class="text-[#78B928]" />
    </div>
    <h3 class="text-xl font-black">Filtros Inteligentes</h3>
  </div>
  
  <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
    {/* Selects com ícones */}
    <div class="relative">
      <Database size={16} class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 z-10" />
      <select class="w-full pl-10 pr-4 py-3 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-[#78B928] focus:ring-4 focus:ring-[#78B928]/20 transition-all">
        <option>Todos os Segmentos</option>
        {/* ... */}
      </select>
    </div>
    
    {/* Repetir para categoria e grupo */}
    
    <ModernButton variant="primary" onClick={loadData} disabled={loading()}>
      Aplicar Filtros
    </ModernButton>
  </div>
</ModernCard>
```

3. **Charts Grid:**
```tsx
<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
  <ModernCard variant="glass" class="p-8 shadow-2xl border-2 border-[#78B928]/10">
    <div class="flex justify-between items-start mb-6">
      <div>
        <h3 class="text-2xl font-black text-gray-900 dark:text-white mb-2">
          Vendas por Categoria
        </h3>
        <p class="text-sm text-gray-600">Top 10 categorias por volume</p>
      </div>
      <ChartDownloadButton chartId="vendas-categoria" />
    </div>
    
    <PlotlyChart chartSpec={vendasCategoriaChart} height="400px" />
    
    {/* Footer com insight AI */}
    <div class="mt-6 p-4 bg-gradient-to-r from-[#78B928]/10 to-[#78B928]/5 rounded-xl border border-[#78B928]/20">
      <p class="text-sm text-gray-700 dark:text-gray-300 flex items-center gap-2">
        <Sparkles size={16} class="text-[#78B928]" />
        <span><strong>Insight:</strong> A categoria líder representa 32% do volume total</span>
      </p>
    </div>
  </ModernCard>
  
  {/* Repetir para outros charts */}
</div>
```

### 4. CHAT (Chat.tsx) - 🟡 MÉDIA PRIORIDADE

**Mudanças:**

1. **Message Bubbles:**
```tsx
{/* User Message */}
<div class="flex justify-end mb-4">
  <div class="max-w-[80%] bg-gradient-to-br from-[#78B928] to-[#99CF47] text-white rounded-3xl rounded-tr-md p-5 shadow-lg">
    <div class="markdown-body text-white">
      {msg.text}
    </div>
    <div class="text-xs text-white/70 mt-3 flex items-center gap-2">
      <Clock size={12} />
      {formatTimestamp(msg.timestamp)}
    </div>
  </div>
</div>

{/* Assistant Message */}
<div class="flex justify-start mb-4">
  <div class="max-w-[80%] bg-white dark:bg-gray-800 rounded-3xl rounded-tl-md p-5 shadow-xl border-2 border-gray-200 dark:border-gray-700">
    {/* Badge do Caçulinha */}
    <div class="flex items-center gap-2 mb-4 pb-3 border-b border-gray-100 dark:border-gray-700">
      <div class="p-1.5 bg-gradient-to-br from-[#78B928] to-[#99CF47] rounded-lg">
        <Sparkles size={14} class="text-white" />
      </div>
      <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Caçulinha BI</span>
    </div>
    
    <div class="markdown-body">
      {msg.text}
    </div>
    
    {/* Action buttons */}
    <div class="flex gap-2 mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
      <button class="px-3 py-1.5 text-xs font-semibold text-gray-600 hover:text-[#78B928] hover:bg-[#78B928]/10 rounded-lg transition-all flex items-center gap-1">
        <Copy size={14} />
        Copiar
      </button>
      <button class="px-3 py-1.5 text-xs font-semibold text-gray-600 hover:text-[#78B928] hover:bg-[#78B928]/10 rounded-lg transition-all flex items-center gap-1">
        <ThumbsUp size={14} />
        Útil
      </button>
    </div>
  </div>
</div>
```

2. **Input Area:**
```tsx
<div class="p-6 border-t bg-gradient-to-r from-white/50 to-gray-50/50 dark:from-gray-900/50 dark:to-gray-800/50 backdrop-blur-xl">
  <form onSubmit={sendMessage} class="max-w-4xl mx-auto">
    <div class="relative">
      <input
        type="text"
        class="
          w-full px-6 py-4 pr-24
          bg-white dark:bg-gray-800
          border-2 border-gray-200 dark:border-gray-700
          rounded-2xl
          focus:border-[#78B928] focus:ring-4 focus:ring-[#78B928]/20
          transition-all text-base shadow-lg
          placeholder:text-gray-400
        "
        placeholder="Faça uma pergunta sobre os dados..."
        value={input()}
        onInput={(e) => setInput(e.currentTarget.value)}
        disabled={isStreaming()}
      />
      
      <div class="absolute right-3 top-1/2 -translate-y-1/2 flex gap-2">
        <button 
          type="button"
          class="p-2 text-gray-400 hover:text-[#78B928] hover:bg-[#78B928]/10 rounded-lg transition-all"
        >
          <Paperclip size={20} />
        </button>
        
        <button
          type="submit"
          disabled={!input() || isStreaming()}
          class="
            p-2 px-4
            bg-gradient-to-r from-[#78B928] to-[#99CF47]
            hover:from-[#609420] hover:to-[#78B928]
            text-white rounded-xl
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-all hover:scale-105 shadow-md hover:shadow-lg
          "
        >
          {isStreaming() ? (
            <Loader2 size={20} class="animate-spin" />
          ) : (
            <Send size={20} />
          )}
        </button>
      </div>
    </div>
  </form>
</div>
```

## INSTRUÇÕES DE EXECUÇÃO

### PASSO 1: Criar Componentes Base
Primeiro, crie os componentes modernos em `src/components/modern/`:

1. `ModernCard.tsx`
2. `StatCard.tsx`
3. `ModernButton.tsx`
4. `SectionHeader.tsx`

### PASSO 2: Adicionar CSS Global
Adicione ao `src/styles/global.css` ou crie `src/styles/modern.css`:

```css
/* Glassmorphism */
.glass {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dark .glass {
  background: rgba(31, 41, 55, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Gradient Text */
.gradient-text-green {
  background: linear-gradient(135deg, #78B928 0%, #99CF47 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Animations */
@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(120, 185, 40, 0.3);
  }
  50% {
    box-shadow: 0 0 40px rgba(120, 185, 40, 0.6);
  }
}

.animate-pulse-glow {
  animation: pulse-glow 2s ease-in-out infinite;
}
```

### PASSO 3: Atualizar Tailwind Config
Adicione ao `tailwind.config.js`:

```js
module.exports = {
  theme: {
    extend: {
      colors: {
        'cacula-green': {
          DEFAULT: '#78B928',
          50: '#F2F9E8',
          500: '#78B928',
          600: '#609420',
        },
        'cacula-red': {
          DEFAULT: '#ED1C24',
          500: '#ED1C24',
          600: '#BE161D',
        },
        'cacula-yellow': {
          DEFAULT: '#FDB913',
          500: '#FDB913',
          600: '#CA940F',
        },
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #78B928 0%, #99CF47 100%)',
        'gradient-accent': 'linear-gradient(135deg, #ED1C24 0%, #F7474F 100%)',
        'gradient-hero': 'linear-gradient(135deg, #78B928 0%, #FDB913 50%, #ED1C24 100%)',
      },
    },
  },
};
```

### PASSO 4: Modernizar Páginas (Ordem de Prioridade)
1. ✅ Dashboard.tsx
2. ✅ Rupturas.tsx
3. ✅ Analytics.tsx
4. ✅ Chat.tsx
5. Transfers.tsx
6. About.tsx (use como referência - já está pronto)

### PASSO 5: Testar
- Responsividade (mobile, tablet, desktop)
- Dark mode
- Performance
- Acessibilidade

## PADRÕES A SEGUIR EM TODAS AS PÁGINAS

### ✅ SEMPRE FAZER:
- Usar `rounded-2xl` ou `rounded-3xl` (nunca `rounded-lg`)
- Aplicar `transition-all duration-300` em elementos interativos
- Usar `font-black` para headers principais
- Aplicar gradientes em textos importantes
- Incluir ícones em cards e headers
- Usar glassmorphism em painéis/modais
- Espaçamento: `gap-6`, `gap-8`, `p-8`
- Sombras: `shadow-xl`, `shadow-2xl`

### ❌ NUNCA FAZER:
- Usar cores genéricas (blue-500, green-500) - sempre usar cores da marca
- Border radius pequeno (`rounded`, `rounded-md`)
- Espaçamento apertado (`gap-2`, `p-2`)
- Headers sem hierarquia visual forte
- Cards planos sem elevação
- Botões sem hover effects
- Esquecer dark mode

## VERIFICAÇÃO FINAL

Antes de considerar concluído, confirme que CADA página tem:

- [ ] Header com SectionHeader ou gradiente
- [ 
  
] KPIs usando StatCard (quando aplicável)
- [ ] Todos os cards usando ModernCard
- [ ] Todos os botões usando ModernButton
- [ ] Cores da marca (#78B928, #ED1C24, #FDB913)
- [ ] Border radius >= 16px
- [ ] Hover effects em todos os interativos
- [ ] Glassmorphism em painéis principais
- [ ] Typography forte (font-black, gradientes)
- [ ] Espaçamento generoso (gap-6+)
- [ ] Funciona em dark mode
- [ ] Responsivo em mobile

## RESULTADO ESPERADO

Ao final, o sistema deve ter:
- Visual moderno e premium
- Identidade visual forte das Lojas Caçula
- UX fluida e agradável
- Performance mantida
- 100% funcional
- Acessível (WCAG AA)

COMECE AGORA! Priorize Dashboard e Rupturas primeiro.
```

---

## 📝 COMO USAR ESTE PROMPT

1. **Copie o prompt completo acima** (todo o conteúdo entre os três backticks)

2. **Cole em sua LLM favorita:**
   - Claude 3.5 Sonnet (recomendado)
   - GPT-4 Turbo
   - Gemini 1.5 Pro

3. **Adicione contexto do seu projeto:**
   ```
   Aqui estão os arquivos do projeto:
   [Cole os arquivos das páginas atuais que você quer modernizar]
   ```

4. **A LLM irá:**
   - Criar os componentes modernos
   - Modernizar as páginas na ordem de prioridade
   - Aplicar todas as tendências e padrões
   - Manter funcionalidade 100%

5. **Valide o resultado:**
   - Teste responsividade
   - Teste dark mode
   - Verifique performance
   - Valide cores da marca

---

## 🎯 EXEMPLO DE USO

**Você:**
```
[Cola o prompt completo acima]

Comece modernizando o Dashboard. Aqui está o arquivo atual:

[Cola o conteúdo de Dashboard.tsx]
```

**LLM:**
```tsx
// A LLM vai retornar o Dashboard.tsx completamente modernizado
// com todos os padrões aplicados
```

---

**Criado por:** DevJr - BI Assistant - Lojas Caçula  
**Versão:** 1.0.0  
**Data:** Janeiro 2025
