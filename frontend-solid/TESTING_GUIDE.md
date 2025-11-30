# Guia de Testes - Componentes Migrados SolidJS

## 🧪 Como Testar os Componentes Migrados

### 1. Executar o Projeto SolidJS

```bash
cd frontend-solid
pnpm install  # Se ainda não instalou
pnpm dev      # Inicia servidor de desenvolvimento
```

O projeto deve abrir em: `http://localhost:3000`

### 2. Testar Componentes Individualmente

#### Opção A: Usar a Página de Demonstração Existente
Acesse: `http://localhost:3000/components-demo`

Esta página já mostra:
- Skeleton
- Badge (todas variantes)
- Button (todas variantes e tamanhos)

#### Opção B: Criar Página de Teste Completa

Crie `src/pages/TestAllComponents.tsx`:

```tsx
import {
  Skeleton, Badge, Button, Separator, Label, Input,
  Card, CardHeader, CardTitle, CardContent,
  Avatar, AvatarImage, AvatarFallback,
  Alert, AlertTitle, AlertDescription,
  LazyImage, SkipLink,
  Tabs, TabsList, TabsTrigger, TabsContent,
  Table, TableHeader, TableBody, TableRow, TableHead, TableCell,
  Dialog, DialogContent, DialogHeader, DialogTitle,
  Select, SelectOption,
  DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem,
  Sheet, SheetHeader, SheetTitle,
  toast, Toaster
} from "../migrated-components/components/ui";
import { createSignal } from "solid-js";

export default function TestAllComponents() {
  const [dialogOpen, setDialogOpen] = createSignal(false);
  const [sheetOpen, setSheetOpen] = createSignal(false);

  return (
    <div class="p-8 space-y-8">
      <Toaster />
      
      <h1 class="text-3xl font-bold">Teste de Todos os Componentes</h1>

      {/* Skeleton */}
      <section>
        <h2 class="text-xl font-semibold mb-4">Skeleton</h2>
        <Skeleton class="h-12 w-full" />
      </section>

      {/* Badge */}
      <section>
        <h2 class="text-xl font-semibold mb-4">Badge</h2>
        <div class="flex gap-2">
          <Badge>Default</Badge>
          <Badge variant="secondary">Secondary</Badge>
          <Badge variant="destructive">Destructive</Badge>
          <Badge variant="outline">Outline</Badge>
        </div>
      </section>

      {/* Button */}
      <section>
        <h2 class="text-xl font-semibold mb-4">Button</h2>
        <div class="flex gap-2">
          <Button>Default</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="destructive">Destructive</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="link">Link</Button>
        </div>
      </section>

      {/* Input + Label */}
      <section>
        <h2 class="text-xl font-semibold mb-4">Input & Label</h2>
        <div class="space-y-2">
          <Label for="test-input">Email</Label>
          <Input id="test-input" type="email" placeholder="Digite seu email" />
        </div>
      </section>

      {/* Card */}
      <section>
        <h2 class="text-xl font-semibold mb-4">Card</h2>
        <Card>
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Card content goes here</p>
          </CardContent>
        </Card>
      </section>

      {/* Alert */}
      <section>
        <h2 class="text-xl font-semibold mb-4">Alert</h2>
        <Alert>
          <AlertTitle>Alert Title</AlertTitle>
          <AlertDescription>This is an alert message</AlertDescription>
        </Alert>
      </section>

      {/* Avatar */}
      <section>
        <h2 class="text-xl font-semibold mb-4">Avatar</h2>
        <Avatar>
          <AvatarFallback>AB</AvatarFallback>
        </Avatar>
      </section>

      {/* Tabs */}
      <section>
        <h2 class="text-xl font-semibold mb-4">Tabs</h2>
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
          <TabsContent value="tab2">Content 2</TabsContent>
        </Tabs>
      </section>

      {/* Table */}
      <section>
        <h2 class="text-xl font-semibold mb-4">Table</h2>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell>Item 1</TableCell>
              <TableCell>Active</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </section>

      {/* Dialog */}
      <section>
        <h2 class="text-xl font-semibold mb-4">Dialog</h2>
        <Button onClick={() => setDialogOpen(true)}>Open Dialog</Button>
        <Dialog open={dialogOpen()} onOpenChange={setDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Dialog Title</DialogTitle>
            </DialogHeader>
            <p>Dialog content</p>
          </DialogContent>
        </Dialog>
      </section>

      {/* Sheet */}
      <section>
        <h2 class="text-xl font-semibold mb-4">Sheet</h2>
        <Button onClick={() => setSheetOpen(true)}>Open Sheet</Button>
        <Sheet open={sheetOpen()} onOpenChange={setSheetOpen}>
          <SheetHeader>
            <SheetTitle>Sheet Title</SheetTitle>
          </SheetHeader>
          <p>Sheet content</p>
        </Sheet>
      </section>

      {/* Toast */}
      <section>
        <h2 class="text-xl font-semibold mb-4">Toast (Sonner)</h2>
        <div class="flex gap-2">
          <Button onClick={() => toast("Default toast")}>Default</Button>
          <Button onClick={() => toast("Success!", { type: "success" })}>Success</Button>
          <Button onClick={() => toast("Error!", { type: "error" })}>Error</Button>
        </div>
      </section>
    </div>
  );
}
```

### 3. Executar Testes Unitários

```bash
cd frontend-solid
pnpm test
```

**Resultado esperado:** 17/18 testes passando (94%)

### 4. Checklist de Validação

- [ ] Servidor dev inicia sem erros
- [ ] Página carrega corretamente
- [ ] Skeleton aparece com animação
- [ ] Badge mostra todas as 4 variantes
- [ ] Button mostra todas as 6 variantes
- [ ] Input aceita texto
- [ ] Card renderiza corretamente
- [ ] Alert mostra mensagem
- [ ] Avatar mostra fallback
- [ ] Tabs troca de conteúdo ao clicar
- [ ] Table mostra dados
- [ ] Dialog abre e fecha
- [ ] Sheet abre e fecha
- [ ] Toast aparece e desaparece
- [ ] Estilos estão corretos (tema light/dark)
- [ ] Não há erros no console

### 5. Testar Integração com Backend (Opcional)

Se quiser testar com o backend:

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend-solid
pnpm dev
```

### 6. Build de Produção (Opcional)

```bash
cd frontend-solid
pnpm build
pnpm preview  # Testa build de produção
```

## ✅ Critérios de Sucesso

- ✅ Todos os componentes renderizam
- ✅ Interações funcionam (clicks, inputs, etc)
- ✅ Estilos aplicados corretamente
- ✅ Sem erros no console
- ✅ Performance boa (sem lags)

## 🐛 Se Encontrar Problemas

1. Verifique o console do navegador
2. Verifique logs do terminal
3. Confirme que todas dependências estão instaladas
4. Teste componentes isoladamente

## 📝 Após Validação

Quando tudo estiver funcionando:
1. Documente quaisquer ajustes necessários
2. Faça merge para main
3. Deploy em produção

---

**Branch atual:** `migracao-solidjs`  
**Status:** Pronto para testes
