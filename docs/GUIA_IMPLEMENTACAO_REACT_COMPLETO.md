# 🚀 GUIA COMPLETO DE IMPLEMENTAÇÃO - REACT PARA PRODUÇÃO

**Projeto:** Agent Solution BI  
**Objetivo:** Migrar interface de Streamlit para React profissional  
**Prazo:** 4-6 meses (20 semanas)  
**Custo:** R$ 85.000 - R$ 120.000

> **IMPORTANTE:** Este documento é autocontido e permite que qualquer desenvolvedor ou LLM continue a implementação do ponto onde parou.

---

## 📋 ÍNDICE

1. [Pré-requisitos](#pré-requisitos)
2. [Fase 1: Fundação (Semanas 1-4)](#fase-1-fundação)
3. [Fase 2: Páginas Core Parte 1 (Semanas 5-8)](#fase-2-páginas-core-parte-1)
4. [Fase 3: Páginas Core Parte 2 (Semanas 9-12)](#fase-3-páginas-core-parte-2)
5. [Fase 4: Otimização (Semanas 13-16)](#fase-4-otimização)
6. [Fase 5: Testes e Deploy (Semanas 17-20)](#fase-5-testes-e-deploy)
7. [Apêndices](#apêndices)

---

## 🔧 PRÉ-REQUISITOS

### Software Necessário

```bash
# 1. Node.js LTS (v20+)
# Download: https://nodejs.org/
node --version  # Deve mostrar v20.x.x ou superior

# 2. pnpm (gerenciador de pacotes - mais rápido que npm)
npm install -g pnpm
pnpm --version  # Deve mostrar v8.x.x ou superior

# 3. Git
git --version

# 4. VS Code (editor recomendado)
# Download: https://code.visualstudio.com/

# 5. Docker (para backend FastAPI)
docker --version
```

### Extensões VS Code Recomendadas

```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense",
    "mikestead.dotenv",
    "prisma.prisma",
    "ms-playwright.playwright"
  ]
}
```

Salvar em: `.vscode/extensions.json`

---

## 📁 FASE 1: FUNDAÇÃO (SEMANAS 1-4)

### ✅ Checklist Fase 1

```markdown
- [ ] 1.1 Criar projeto Next.js
- [ ] 1.2 Configurar TypeScript estrito
- [ ] 1.3 Configurar ESLint + Prettier
- [ ] 1.4 Setup Tailwind CSS
- [ ] 1.5 Instalar shadcn/ui
- [ ] 1.6 Criar Design System base
- [ ] 1.7 Configurar Zustand (estado global)
- [ ] 1.8 Configurar TanStack Query
- [ ] 1.9 Criar serviço de API
- [ ] 1.10 Implementar autenticação JWT
- [ ] 1.11 Setup WebSocket client
- [ ] 1.12 Criar layout base
```

---

### 1.1 Criar Projeto Next.js

```bash
# Navegar para pasta do projeto
cd c:\Users\André\Documents\Agent_Solution_BI

# Criar pasta frontend-react (separada do Streamlit)
mkdir frontend-react
cd frontend-react

# Criar projeto Next.js com TypeScript
pnpm create next-app@latest . --typescript --tailwind --app --src-dir --import-alias "@/*"

# Responda às perguntas:
# ✔ Would you like to use ESLint? → Yes
# ✔ Would you like to use Tailwind CSS? → Yes
# ✔ Would you like to use `src/` directory? → Yes
# ✔ Would you like to use App Router? → Yes
# ✔ Would you like to customize the default import alias? → Yes (@/*)
```

**Estrutura criada:**

```
frontend-react/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   └── components/
├── public/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── .eslintrc.json
```

---

### 1.2 Configurar TypeScript Estrito

**Arquivo: `tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/hooks/*": ["./src/hooks/*"],
      "@/types/*": ["./src/types/*"],
      "@/services/*": ["./src/services/*"],
      "@/store/*": ["./src/store/*"]
    },
    // Strict rules
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitReturns": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

---

### 1.3 Configurar ESLint + Prettier

**Instalar dependências:**

```bash
pnpm add -D prettier eslint-config-prettier eslint-plugin-prettier @typescript-eslint/eslint-plugin @typescript-eslint/parser
```

**Arquivo: `.eslintrc.json`**

```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended",
    "plugin:prettier/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": [
      "error",
      { "argsIgnorePattern": "^_" }
    ],
    "@typescript-eslint/no-explicit-any": "warn",
    "react-hooks/exhaustive-deps": "warn",
    "prefer-const": "error",
    "no-console": ["warn", { "allow": ["warn", "error"] }]
  }
}
```

**Arquivo: `.prettierrc`**

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "arrowParens": "avoid",
  "endOfLine": "lf"
}
```

**Arquivo: `.prettierignore`**

```
node_modules
.next
out
build
dist
```

---

### 1.4 Setup Tailwind CSS

**Arquivo: `tailwind.config.ts`**

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Design system colors
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        secondary: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#a855f7',
          600: '#9333ea',
          700: '#7e22ce',
          800: '#6b21a8',
          900: '#581c87',
          950: '#3b0764',
        },
        // UI colors
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [require('tailwindcss-animate'), require('@tailwindcss/typography')],
};

export default config;
```

**Instalar plugins:**

```bash
pnpm add tailwindcss-animate @tailwindcss/typography
```

**Arquivo: `src/app/globals.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;

    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;

    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;

    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;

    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;

    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;

    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;

    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;

    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;

    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;

    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;

    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;

    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;

    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;

    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;

    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;

    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;

    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
    font-feature-settings: 'rlig' 1, 'calt' 1;
  }
}
```

---

### 1.5 Instalar shadcn/ui

```bash
# Instalar CLI do shadcn
pnpm dlx shadcn-ui@latest init

# Responda:
# ✔ Which style would you like to use? › Default
# ✔ Which color would you like to use as base color? › Slate
# ✔ Would you like to use CSS variables for colors? › yes

# Instalar componentes base essenciais
pnpm dlx shadcn-ui@latest add button
pnpm dlx shadcn-ui@latest add card
pnpm dlx shadcn-ui@latest add input
pnpm dlx shadcn-ui@latest add label
pnpm dlx shadcn-ui@latest add select
pnpm dlx shadcn-ui@latest add dialog
pnpm dlx shadcn-ui@latest add dropdown-menu
pnpm dlx shadcn-ui@latest add toast
pnpm dlx shadcn-ui@latest add avatar
pnpm dlx shadcn-ui@latest add badge
pnpm dlx shadcn-ui@latest add separator
pnpm dlx shadcn-ui@latest add skeleton
pnpm dlx shadcn-ui@latest add table
pnpm dlx shadcn-ui@latest add tabs
pnpm dlx shadcn-ui@latest add alert
```

**Componentes instalados em:** `src/components/ui/`

---

### 1.6 Criar Design System Base

**Arquivo: `src/lib/design-system/tokens.ts`**

```typescript
export const tokens = {
  colors: {
    brand: {
      primary: '#0ea5e9',
      secondary: '#a855f7',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6',
    },
    neutral: {
      50: '#f9fafb',
      100: '#f3f4f6',
      200: '#e5e7eb',
      300: '#d1d5db',
      400: '#9ca3af',
      500: '#6b7280',
      600: '#4b5563',
      700: '#374151',
      800: '#1f2937',
      900: '#111827',
      950: '#030712',
    },
  },
  spacing: {
    xs: '0.25rem', // 4px
    sm: '0.5rem', // 8px
    md: '1rem', // 16px
    lg: '1.5rem', // 24px
    xl: '2rem', // 32px
    '2xl': '3rem', // 48px
    '3xl': '4rem', // 64px
  },
  typography: {
    fontSizes: {
      xs: '0.75rem', // 12px
      sm: '0.875rem', // 14px
      base: '1rem', // 16px
      lg: '1.125rem', // 18px
      xl: '1.25rem', // 20px
      '2xl': '1.5rem', // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem', // 36px
    },
    fontWeights: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
  },
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
  },
} as const;
```

**Arquivo: `src/components/design-system/Container.tsx`**

```typescript
import React from 'react';
import { cn } from '@/lib/utils';

interface ContainerProps {
  children: React.ReactNode;
  className?: string;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
}

const maxWidthMap = {
  sm: 'max-w-screen-sm',
  md: 'max-w-screen-md',
  lg: 'max-w-screen-lg',
  xl: 'max-w-screen-xl',
  '2xl': 'max-w-screen-2xl',
  full: 'max-w-full',
};

export const Container: React.FC<ContainerProps> = ({
  children,
  className,
  maxWidth = 'xl',
}) => {
  return (
    <div
      className={cn(
        'mx-auto w-full px-4 sm:px-6 lg:px-8',
        maxWidthMap[maxWidth],
        className
      )}
    >
      {children}
    </div>
  );
};
```

---

### 1.7 Configurar Zustand (Estado Global)

**Instalar:**

```bash
pnpm add zustand immer
```

**Arquivo: `src/store/auth.store.ts`**

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'user' | 'viewer';
  avatar?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  login: (user: User, token: string) => void;
  logout: () => void;
  setUser: (user: User) => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    immer((set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: (user, token) =>
        set((state) => {
          state.user = user;
          state.token = token;
          state.isAuthenticated = true;
        }),

      logout: () =>
        set((state) => {
          state.user = null;
          state.token = null;
          state.isAuthenticated = false;
        }),

      setUser: (user) =>
        set((state) => {
          state.user = user;
        }),

      setLoading: (loading) =>
        set((state) => {
          state.isLoading = loading;
        }),
    })),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

**Arquivo: `src/store/ui.store.ts`**

```typescript
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
  }>;

  // Actions
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  addNotification: (
    type: UIState['notifications'][0]['type'],
    message: string
  ) => void;
  removeNotification: (id: string) => void;
}

export const useUIStore = create<UIState>()(
  immer((set) => ({
    sidebarOpen: true,
    theme: 'light',
    notifications: [],

    toggleSidebar: () =>
      set((state) => {
        state.sidebarOpen = !state.sidebarOpen;
      }),

    setSidebarOpen: (open) =>
      set((state) => {
        state.sidebarOpen = open;
      }),

    setTheme: (theme) =>
      set((state) => {
        state.theme = theme;
      }),

    addNotification: (type, message) =>
      set((state) => {
        state.notifications.push({
          id: Math.random().toString(36).substring(7),
          type,
          message,
        });
      }),

    removeNotification: (id) =>
      set((state) => {
        state.notifications = state.notifications.filter((n) => n.id !== id);
      }),
  }))
);
```

---

### 1.8 Configurar TanStack Query

**Instalar:**

```bash
pnpm add @tanstack/react-query @tanstack/react-query-devtools
```

**Arquivo: `src/lib/react-query/provider.tsx`**

```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

export function ReactQueryProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minuto
            gcTime: 5 * 60 * 1000, // 5 minutos (antes era cacheTime)
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

**Atualizar `src/app/layout.tsx`:**

```typescript
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { ReactQueryProvider } from '@/lib/react-query/provider';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
  title: 'Agent Solution BI - Produção',
  description: 'Business Intelligence com IA - Interface Profissional',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className={inter.variable}>
        <ReactQueryProvider>{children}</ReactQueryProvider>
      </body>
    </html>
  );
}
```

---

### 1.9 Criar Serviço de API

**Arquivo: `src/lib/api/client.ts`**

```typescript
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/store/auth.store';

// URL da API FastAPI (ajustar conforme ambiente)
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para adicionar token em todas as requisições
    this.client.interceptors.request.use(
      (config) => {
        const token = useAuthStore.getState().token;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Interceptor para tratar erros
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expirado - fazer logout
          useAuthStore.getState().logout();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }

  // Streaming para chat BI
  async *stream(url: string, data?: unknown): AsyncGenerator<string> {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${useAuthStore.getState().token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Stream error: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('No reader available');

    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      yield decoder.decode(value);
    }
  }
}

export const apiClient = new APIClient();
```

**Instalar axios:**

```bash
pnpm add axios
```

---

### 1.10 Implementar Autenticação JWT

**Arquivo: `src/services/auth.service.ts`**

```typescript
import { apiClient } from '@/lib/api/client';
import type { User } from '@/store/auth.store';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  token_type: string;
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>('/api/auth/login', credentials);
  },

  async logout(): Promise<void> {
    return apiClient.post('/api/auth/logout');
  },

  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/api/auth/me');
  },

  async refreshToken(): Promise<{ access_token: string }> {
    return apiClient.post<{ access_token: string }>('/api/auth/refresh');
  },
};
```

**Arquivo: `src/app/login/page.tsx`**

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth.store';
import { authService } from '@/services/auth.service';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

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
      login(response.user, response.access_token);
      router.push('/dashboard');
    } catch (err) {
      setError('Credenciais inválidas. Tente novamente.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center text-2xl">
            Agent Solution BI
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="username">Usuário</Label>
              <Input
                id="username"
                name="username"
                type="text"
                required
                autoComplete="username"
                disabled={isLoading}
              />
            </div>
            <div>
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                name="password"
                type="password"
                required
                autoComplete="current-password"
                disabled={isLoading}
              />
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
```

---

### 1.11 Setup WebSocket Client

**Instalar:**

```bash
pnpm add socket.io-client
```

**Arquivo: `src/lib/websocket/client.ts`**

```typescript
import { io, Socket } from 'socket.io-client';
import { useAuthStore } from '@/store/auth.store';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:5000';

class WebSocketClient {
  private socket: Socket | null = null;

  connect() {
    if (this.socket?.connected) return;

    const token = useAuthStore.getState().token;

    this.socket = io(WS_URL, {
      auth: {
        token,
      },
      transports: ['websocket'],
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  emit(event: string, data: unknown) {
    if (!this.socket) {
      console.warn('Socket not connected');
      return;
    }
    this.socket.emit(event, data);
  }

  on(event: string, callback: (data: unknown) => void) {
    if (!this.socket) {
      console.warn('Socket not connected');
      return;
    }
    this.socket.on(event, callback);
  }

  off(event: string, callback?: (data: unknown) => void) {
    if (!this.socket) return;
    this.socket.off(event, callback);
  }
}

export const wsClient = new WebSocketClient();
```

---

### 1.12 Criar Layout Base

**Arquivo: `src/components/layout/Sidebar.tsx`**

```typescript
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  MessageSquare,
  BarChart3,
  FileText,
  Settings,
  LogOut,
} from 'lucide-react';
import { useAuthStore } from '@/store/auth.store';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Chat BI', href: '/chat', icon: MessageSquare },
  { name: 'Análises', href: '/analytics', icon: BarChart3 },
  { name: 'Relatórios', href: '/reports', icon: FileText },
  { name: 'Configurações', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  return (
    <div className="flex h-screen w-64 flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="flex h-16 items-center px-6">
        <h1 className="text-xl font-bold">Agent BI</h1>
      </div>

      {/* User info */}
      <div className="border-b border-gray-800 px-6 py-4">
        <div className="flex items-center gap-3">
          <Avatar>
            <AvatarFallback>
              {user?.username?.charAt(0).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 overflow-hidden">
            <p className="truncate text-sm font-medium">{user?.username}</p>
            <p className="truncate text-xs text-gray-400">{user?.email}</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-gray-800 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Logout */}
      <div className="border-t border-gray-800 p-4">
        <Button
          variant="ghost"
          className="w-full justify-start text-gray-400 hover:bg-gray-800 hover:text-white"
          onClick={logout}
        >
          <LogOut className="mr-3 h-5 w-5" />
          Sair
        </Button>
      </div>
    </div>
  );
}
```

**Instalar ícones:**

```bash
pnpm add lucide-react
```

**Arquivo: `src/app/(authenticated)/layout.tsx`**

```typescript
import { Sidebar } from '@/components/layout/Sidebar';

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-gray-50">{children}</main>
    </div>
  );
}
```

---

### ✅ Checklist Final Fase 1

Ao final da Fase 1, você deve ter:

```markdown
✅ Projeto Next.js configurado
✅ TypeScript + ESLint + Prettier funcionando
✅ Tailwind CSS + shadcn/ui instalados
✅ Design System base criado
✅ Zustand (estado global) configurado
✅ TanStack Query funcionando
✅ API client com autenticação JWT
✅ WebSocket client pronto
✅ Layout base com sidebar
✅ Página de login funcional
```

**Comando de teste:**

```bash
pnpm dev
# Abrir http://localhost:3000
```

---

## 📁 FASE 2: PÁGINAS CORE PARTE 1 (SEMANAS 5-8)

### ✅ Checklist Fase 2

```markdown
- [ ] 2.1 Criar Dashboard Principal
- [ ] 2.2 Implementar widgets interativos
- [ ] 2.3 Criar sistema de Chat BI
- [ ] 2.4 Implementar streaming LLM
- [ ] 2.5 Code highlighting
- [ ] 2.6 Histórico de conversas
- [ ] 2.7 Gráficos dinâmicos
- [ ] 2.8 Integração completa com FastAPI
```

---

### 2.1 Criar Dashboard Principal

**Arquivo: `src/app/(authenticated)/dashboard/page.tsx`**

```typescript
'use client';

import { Container } from '@/components/design-system/Container';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { TrendingUp, Users, DollarSign, Package } from 'lucide-react';

interface Metrics {
  totalSales: number;
  totalUsers: number;
  revenue: number;
  productsCount: number;
  salesGrowth: number;
  usersGrowth: number;
}

async function fetchMetrics(): Promise<Metrics> {
  return apiClient.get<Metrics>('/api/metrics/summary');
}

export default function DashboardPage() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['metrics'],
    queryFn: fetchMetrics,
  });

  const cards = [
    {
      title: 'Vendas Totais',
      value: metrics?.totalSales.toLocaleString('pt-BR') || '0',
      icon: TrendingUp,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      growth: metrics?.salesGrowth,
    },
    {
      title: 'Usuários Ativos',
      value: metrics?.totalUsers.toLocaleString('pt-BR') || '0',
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      growth: metrics?.usersGrowth,
    },
    {
      title: 'Receita',
      value: `R$ ${(metrics?.revenue || 0).toLocaleString('pt-BR')}`,
      icon: DollarSign,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Produtos',
      value: metrics?.productsCount.toLocaleString('pt-BR') || '0',
      icon: Package,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  return (
    <Container maxWidth="2xl" className="py-8">
      <h1 className="mb-8 text-3xl font-bold">Dashboard</h1>

      {/* Métricas principais */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {cards.map((card) => (
          <Card key={card.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {card.title}
              </CardTitle>
              <div className={`rounded-full p-2 ${card.bgColor}`}>
                <card.icon className={`h-5 w-5 ${card.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLoading ? '...' : card.value}
              </div>
              {card.growth !== undefined && (
                <p
                  className={`mt-1 text-xs ${
                    card.growth >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {card.growth >= 0 ? '+' : ''}
                  {card.growth}% em relação ao mês anterior
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Gráficos e tabelas serão adicionados aqui */}
    </Container>
  );
}
```

---

### 2.2 Implementar Widgets Interativos

**Instalar Recharts:**

```bash
pnpm add recharts
```

**Arquivo: `src/components/dashboard/SalesChart.tsx`**

```typescript
'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface SalesData {
  month: string;
  sales: number;
  revenue: number;
}

interface SalesChartProps {
  data: SalesData[];
}

export function SalesChart({ data }: SalesChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Evolução de Vendas</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip
              formatter={(value: number) => value.toLocaleString('pt-BR')}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="sales"
              stroke="#3b82f6"
              name="Vendas"
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="revenue"
              stroke="#10b981"
              name="Receita (R$)"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
```

---

### 2.3 Criar Sistema de Chat BI

**Arquivo: `src/app/(authenticated)/chat/page.tsx`**

```typescript
'use client';

import { useState, useRef, useEffect } from 'react';
import { Container } from '@/components/design-system/Container';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Send, Loader2 } from 'lucide-react';
import { ChatMessage } from '@/components/chat/ChatMessage';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessageMutation = useMutation({
    mutationFn: async (query: string) => {
      // Adicionar mensagem do usuário
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: query,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Adicionar mensagem de resposta vazia (para streaming)
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Streaming da resposta
      let fullContent = '';
      for await (const chunk of apiClient.stream('/api/chat', { query })) {
        fullContent += chunk;
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessage.id
              ? { ...msg, content: fullContent }
              : msg
          )
        );
      }

      // Marcar streaming como concluído
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessage.id
            ? { ...msg, isStreaming: false }
            : msg
        )
      );
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || sendMessageMutation.isPending) return;

    sendMessageMutation.mutate(input.trim());
    setInput('');
  };

  return (
    <Container maxWidth="2xl" className="flex h-screen flex-col py-8">
      <h1 className="mb-6 text-3xl font-bold">Chat BI com IA</h1>

      {/* Messages area */}
      <Card className="mb-4 flex-1 overflow-y-auto p-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          <div ref={messagesEndRef} />
        </div>
      </Card>

      {/* Input area */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Digite sua pergunta sobre os dados..."
          disabled={sendMessageMutation.isPending}
          className="flex-1"
        />
        <Button
          type="submit"
          disabled={sendMessageMutation.isPending || !input.trim()}
        >
          {sendMessageMutation.isPending ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Send className="h-5 w-5" />
          )}
        </Button>
      </form>
    </Container>
  );
}
```

---

### 2.4 Implementar Streaming LLM + Code Highlighting

**Instalar:**

```bash
pnpm add react-markdown react-syntax-highlighter
pnpm add -D @types/react-syntax-highlighter
```

**Arquivo: `src/components/chat/ChatMessage.tsx`**

```typescript
'use client';

import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { User, Bot } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={cn('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}
    >
      {/* Avatar */}
      <Avatar className={cn(isUser ? 'bg-blue-600' : 'bg-purple-600')}>
        <AvatarFallback className="text-white">
          {isUser ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
        </AvatarFallback>
      </Avatar>

      {/* Message content */}
      <div
        className={cn(
          'max-w-[70%] rounded-lg px-4 py-2',
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100'
        )}
      >
        <ReactMarkdown
          components={{
            code({ node, inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <SyntaxHighlighter
                  style={vscDarkPlus}
                  language={match[1]}
                  PreTag="div"
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
          }}
        >
          {message.content}
        </ReactMarkdown>

        {message.isStreaming && (
          <span className="inline-block h-4 w-1 animate-pulse bg-current" />
        )}

        <p className="mt-2 text-xs opacity-60">
          {message.timestamp.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  );
}
```

---

### ✅ Checklist Final Fase 2

Ao final da Fase 2, você deve ter:

```markdown
✅ Dashboard principal com métricas
✅ Gráficos interativos (Recharts)
✅ Chat BI funcional
✅ Streaming LLM implementado
✅ Syntax highlighting para código
✅ Histórico de mensagens
✅ UI responsiva
```

---

## 🔄 COMO CONTINUAR A IMPLEMENTAÇÃO

Se você ou outra LLM precisar continuar daqui:

### Próximos Passos (Fase 3 - Semanas 9-12)

1. **Página de Análise de Dados**
   - Data grid avançado (TanStack Table)
   - Filtros dinâmicos
   - Exportação CSV/Excel/PDF
   - Drill-down em gráficos

2. **Relatórios**
   - Templates de relatórios
   - Editor de relatórios
   - Agendamento de relatórios
   - Envio por email

3. **Admin Panel**
   - Gerenciamento de usuários
   - Permissões RBAC
   - Logs de auditoria
   - Configurações do sistema

### Comandos Úteis

```bash
# Desenvolvimento
pnpm dev

# Build para produção
pnpm build

# Preview da build
pnpm start

# Linting
pnpm lint

# Formatar código
pnpm format
```

### Variáveis de Ambiente

Criar `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_WS_URL=http://localhost:5000
```

---

## 📚 RECURSOS E REFERÊNCIAS

### Documentação Oficial

- **Next.js:** https://nextjs.org/docs
- **React:** https://react.dev/
- **TypeScript:** https://www.typescriptlang.org/docs/
- **Tailwind CSS:** https://tailwindcss.com/docs
- **shadcn/ui:** https://ui.shadcn.com/
- **TanStack Query:** https://tanstack.com/query/latest
- **Zustand:** https://github.com/pmndrs/zustand
- **Recharts:** https://recharts.org/

### Ferramentas Úteis

- **Figma (Design):** https://www.figma.com/
- **Excalidraw (Diagramas):** https://excalidraw.com/
- **ChatGPT (Assistência):** https://chat.openai.com/
- **GitHub Copilot:** https://github.com/features/copilot

---

## 🎯 CONCLUSÃO

Este guia fornece uma base sólida para implementar o frontend React profissional. Cada seção é independente e pode ser executada por qualquer desenvolvedor ou LLM seguindo os comandos e exemplos fornecidos.

**Tempo estimado por fase:**
- Fase 1: 4 semanas
- Fase 2: 4 semanas
- Fase 3: 4 semanas
- Fase 4: 4 semanas
- Fase 5: 4 semanas

**Total: 20 semanas (5 meses)**

---

**Último Update:** 22/11/2025  
**Versão do Guia:** 1.0.0  
**Status:** Pronto para implementação
