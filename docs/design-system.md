# Design System

O Finanpy usa tema escuro com gradientes e TailwindCSS para estilizacao.

## Paleta de Cores

### Cores Primarias

| Nome | Hex | Uso |
|------|-----|-----|
| primary-600 | `#7C3AED` | Roxo vibrante - acoes principais |
| primary-700 | `#6D28D9` | Hover em botoes primarios |
| primary-800 | `#5B21B6` | Estados ativos |

### Cores Secundarias

| Nome | Hex | Uso |
|------|-----|-----|
| secondary-500 | `#06B6D4` | Ciano - destaques |
| secondary-600 | `#0891B2` | Hover secundario |

### Cores de Fundo (Dark Theme)

| Nome | Hex | Uso |
|------|-----|-----|
| bg-primary | `#0F172A` | Slate 900 - fundo principal |
| bg-secondary | `#1E293B` | Slate 800 - cards |
| bg-tertiary | `#334155` | Slate 700 - elementos elevados |

### Cores de Texto

| Nome | Hex | Uso |
|------|-----|-----|
| text-primary | `#F1F5F9` | Slate 100 - texto principal |
| text-secondary | `#CBD5E1` | Slate 300 - texto secundario |
| text-muted | `#94A3B8` | Slate 400 - texto desabilitado |

### Cores de Status

| Nome | Hex | Uso |
|------|-----|-----|
| success | `#10B981` | Green 500 - sucesso/receitas |
| error | `#EF4444` | Red 500 - erro/despesas |
| warning | `#F59E0B` | Amber 500 - avisos |
| info | `#3B82F6` | Blue 500 - informacoes |

## Tipografia

### Fontes

- **Principal:** Inter (Google Fonts)
- **Monospace:** JetBrains Mono (valores monetarios)

### Escalas

| Classe | Tamanho |
|--------|---------|
| text-xs | 12px |
| text-sm | 14px |
| text-base | 16px |
| text-lg | 18px |
| text-xl | 20px |
| text-2xl | 24px |
| text-3xl | 30px |

## Componentes

### Botao Primario

```html
<button class="px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white font-medium rounded-lg shadow-lg hover:shadow-xl transition-all duration-200">
    Texto do Botao
</button>
```

### Botao Secundario

```html
<button class="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-slate-100 font-medium rounded-lg border border-slate-600 transition-all duration-200">
    Texto do Botao
</button>
```

### Input

```html
<input type="text"
       class="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent transition-all duration-200"
       placeholder="Digite aqui...">
```

### Card

```html
<div class="bg-slate-800 rounded-xl shadow-lg border border-slate-700 p-6 hover:border-primary-600 transition-all duration-200">
    <h3 class="text-xl font-bold text-slate-100 mb-2">Titulo</h3>
    <p class="text-slate-300">Conteudo</p>
</div>
```

### Alerta de Sucesso

```html
<div class="bg-green-900/30 border border-green-700 rounded-lg p-4 flex items-center">
    <span class="text-green-400 mr-3">✓</span>
    <p class="text-green-100">Mensagem de sucesso</p>
</div>
```

### Alerta de Erro

```html
<div class="bg-red-900/30 border border-red-700 rounded-lg p-4 flex items-center">
    <span class="text-red-400 mr-3">✗</span>
    <p class="text-red-100">Mensagem de erro</p>
</div>
```

## Layout

### Container

```html
<div class="container mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Conteudo -->
</div>
```

### Grid Responsivo

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Cards -->
</div>
```

### Layout Dashboard

```html
<div class="min-h-screen bg-slate-900">
    <!-- Navbar -->
    <div class="flex">
        <!-- Sidebar -->
        <main class="flex-1 p-6 ml-64">
            <!-- Conteudo Principal -->
        </main>
    </div>
</div>
```

## Espacamentos

| Classe | Valor |
|--------|-------|
| p-2, p-3, p-4 | 8px, 12px, 16px |
| p-6, p-8 | 24px, 32px |
| p-10, p-12 | 40px, 48px |

## Gradientes

```css
/* Gradiente primario */
bg-gradient-to-r from-primary-600 to-secondary-600

/* Gradiente de destaque */
bg-gradient-to-r from-accent-500 to-primary-600

/* Gradiente de fundo */
bg-gradient-to-br from-slate-900 to-slate-800
```
