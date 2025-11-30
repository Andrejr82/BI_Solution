# Guia de Uso - Componentes UI Migrados para SolidJS

## 📚 Componentes Disponíveis

Todos os 18 componentes UI foram migrados do React para SolidJS e estão disponíveis para uso.

## 🚀 Como Usar

### Importação

```typescript
// Importar componentes individuais
import { Button, Badge, Card } from "./migrated-components/components/ui";

// Ou importar tudo
import * as UI from "./migrated-components/components/ui";
```

### Exemplos de Uso

#### Button
```tsx
import { Button } from "./migrated-components/components/ui";

<Button variant="default">Click me</Button>
<Button variant="destructive" size="sm">Delete</Button>
<Button variant="outline" disabled>Disabled</Button>
```

#### Card
```tsx
import { Card, CardHeader, CardTitle, CardContent } from "./migrated-components/components/ui";

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
  </CardHeader>
  <CardContent>
    Card content goes here
  </CardContent>
</Card>
```

#### Dialog
```tsx
import { createSignal } from "solid-js";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./migrated-components/components/ui";

const [open, setOpen] = createSignal(false);

<>
  <Button onClick={() => setOpen(true)}>Open Dialog</Button>
  <Dialog open={open()} onOpenChange={setOpen}>
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Dialog Title</DialogTitle>
      </DialogHeader>
      <p>Dialog content</p>
    </DialogContent>
  </Dialog>
</>
```

#### Tabs
```tsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./migrated-components/components/ui";

<Tabs defaultValue="tab1">
  <TabsList>
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">Content 1</TabsContent>
  <TabsContent value="tab2">Content 2</TabsContent>
</Tabs>
```

#### Toast (Sonner)
```tsx
import { toast, Toaster } from "./migrated-components/components/ui";

// Adicionar Toaster ao App
<Toaster />

// Usar toast
toast("Success message", { type: "success" });
toast("Error message", { type: "error", duration: 5000 });
```

## 🎨 Componentes por Categoria

### Core
- **Skeleton** - Loading placeholder
- **Badge** - Status indicators (4 variantes)
- **Button** - Buttons (6 variantes, 6 tamanhos)

### Forms
- **Input** - Text input
- **Label** - Form labels
- **Select** - Dropdown select
- **Separator** - Visual divider

### Layout
- **Card** - Content container (7 subcomponentes)
- **Table** - Data tables (8 subcomponentes)
- **Tabs** - Tab navigation (4 subcomponentes)

### Overlays
- **Dialog** - Modal dialogs (5 subcomponentes)
- **Sheet** - Side panels (3 subcomponentes, 4 posições)
- **DropdownMenu** - Dropdown menus (4 subcomponentes)

### Feedback
- **Alert** - Alert messages (3 subcomponentes)
- **Sonner** - Toast notifications

### Media & A11y
- **Avatar** - User avatars (3 subcomponentes)
- **LazyImage** - Lazy loaded images
- **SkipLink** - Accessibility skip link

## ⚙️ Características Técnicas

### Estado
Componentes com estado usam `createSignal`:
- **LazyImage**: loading/error states
- **Tabs**: active tab management
- **Sonner**: global toast state

### Portals
Componentes que usam Portal do SolidJS:
- **Dialog**: overlay + modal
- **Sheet**: overlay + side panel
- **Sonner**: toast container

### Variantes
Componentes com variantes usam `class-variance-authority`:
- **Button**: 6 variantes, 6 tamanhos
- **Badge**: 4 variantes
- **Alert**: 2 variantes

## 📝 Notas Importantes

1. **Sem Radix UI**: Todos componentes são nativos SolidJS
2. **Tipagem**: Usa tipos nativos do SolidJS (`JSX.HTMLAttributes`, etc)
3. **Props**: `class` ao invés de `className`
4. **Children**: Usa `ParentComponent` para componentes com children
5. **Estado**: `createSignal` ao invés de `useState`

## 🔗 Próximos Passos

Para usar estes componentes em produção:
1. Importe os componentes necessários
2. Adicione `<Toaster />` ao App se usar toast
3. Configure tema (light/dark) via CSS variables
4. Teste a integração com sua aplicação
