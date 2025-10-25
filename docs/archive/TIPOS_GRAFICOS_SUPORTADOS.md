# Tipos de Gráficos Suportados - Agent_BI

**Última atualização:** 08/10/2025

---

## 📊 Visão Geral

O Agent_BI suporta **9 tipos de gráficos** diferentes através do Plotly, com renderização automática baseada no tipo especificado no `chart_data`.

---

## ✅ Tipos Suportados

### 1. **bar** - Gráfico de Barras
**Uso:** Comparar valores entre categorias

**Dados necessários:**
```python
{
    "type": "bar",
    "x": ["Cat A", "Cat B", "Cat C"],
    "y": [100, 200, 150],
    "colors": "#1f77b4"  # opcional
}
```

**Recursos:**
- Valores exibidos sobre as barras
- Eixo X rotacionado -45° para melhor leitura
- Hover com formatação de milhares

---

### 2. **pie** - Gráfico de Pizza
**Uso:** Mostrar distribuição percentual

**Dados necessários:**
```python
{
    "type": "pie",
    "x": ["Categoria A", "Categoria B"],
    "y": [300, 700]
}
```

**Recursos:**
- Percentuais automáticos
- Labels + percentuais visíveis
- Hover com valor absoluto e percentual

---

### 3. **line** - Gráfico de Linha
**Uso:** Mostrar tendências ao longo do tempo

**Dados necessários:**
```python
{
    "type": "line",
    "x": ["Jan", "Fev", "Mar"],
    "y": [100, 150, 120]
}
```

**Recursos:**
- Linhas + marcadores
- Ideal para séries temporais
- Suavização visual

---

### 4. **scatter** - Gráfico de Dispersão
**Uso:** Mostrar correlação entre variáveis

**Dados necessários:**
```python
{
    "type": "scatter",
    "x": [1, 2, 3, 4, 5],
    "y": [10, 25, 30, 45, 50]
}
```

**Recursos:**
- Colorscale automática (Viridis)
- Tamanho fixo de marcadores
- Barra de cores quando aplicável

---

### 5. **area** - Gráfico de Área
**Uso:** Mostrar volume ao longo do tempo

**Dados necessários:**
```python
{
    "type": "area",
    "x": ["T1", "T2", "T3"],
    "y": [100, 200, 150]
}
```

**Recursos:**
- Preenchimento até o eixo zero
- Ótimo para acumulados
- Visualização de tendências

---

### 6. **histogram** - Histograma
**Uso:** Mostrar distribuição de frequências

**Dados necessários:**
```python
{
    "type": "histogram",
    "y": [1, 2, 2, 3, 3, 3, 4, 4, 5]  # apenas y necessário
}
```

**Recursos:**
- Bins automáticos
- Ideal para análise estatística
- Frequência no eixo Y

---

### 7. **box** - Box Plot (Caixa)
**Uso:** Mostrar distribuição estatística

**Dados necessários:**
```python
{
    "type": "box",
    "y": [10, 20, 30, 40, 50, 60, 100]  # apenas y necessário
}
```

**Recursos:**
- Mediana visível
- Quartis e outliers
- Desvio padrão exibido

---

### 8. **heatmap** - Mapa de Calor
**Uso:** Mostrar correlações em matriz

**Dados necessários:**
```python
{
    "type": "heatmap",
    "x": ["A", "B", "C"],
    "y": ["1", "2", "3"],
    "z": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
}
```

**Recursos:**
- Colorscale Viridis
- Requer matriz z
- Ideal para correlações

---

### 9. **funnel** - Funil
**Uso:** Mostrar processo de conversão

**Dados necessários:**
```python
{
    "type": "funnel",
    "x": [1000, 800, 600, 400],
    "y": ["Visitas", "Interesse", "Carrinho", "Compra"]
}
```

**Recursos:**
- Percentual total automático
- Visualização de conversão
- Cores customizáveis

---

## 🔧 Fallback Automático

**Tipo desconhecido?** O sistema renderiza como gráfico de barras e exibe aviso:
```
⚠️ Tipo 'custom_type' usando renderização padrão (barras)
```

---

## 🎨 Configurações Comuns

Todos os gráficos suportam:

```python
{
    "type": "bar",  # tipo do gráfico
    "x": [...],
    "y": [...],
    "colors": "#custom",  # cor personalizada (opcional)
    "height": 600,  # altura em pixels (opcional, padrão: 500)
    "margin": {"l": 60, "r": 60, "t": 80, "b": 100}  # margens (opcional)
}
```

---

## 📝 Como Usar no DirectQueryEngine

**No método de query, retorne:**

```python
return {
    "type": "chart",
    "title": "Meu Gráfico",
    "result": {
        "chart_data": {
            "type": "pie",  # escolha o tipo
            "x": categorias,
            "y": valores
        }
    },
    "summary": "Resumo textual",
    "tokens_used": 0
}
```

---

## 🚀 Exemplos Práticos

### Distribuição de Categorias (Pie)
```python
chart_data = {
    "type": "pie",
    "x": ["TECIDOS", "ARTESANATO", "CARNAVALESCO"],
    "y": [45000, 30000, 25000]
}
```

### Evolução Mensal (Line)
```python
chart_data = {
    "type": "line",
    "x": ["Jan", "Fev", "Mar", "Abr"],
    "y": [1000, 1200, 1100, 1500]
}
```

### Ranking de Vendas (Bar)
```python
chart_data = {
    "type": "bar",
    "x": ["UNE 261", "UNE 262", "UNE 263"],
    "y": [50000, 45000, 40000],
    "colors": "#1f77b4"
}
```

---

## ⚠️ Notas Importantes

1. **Tipo "heatmap"** requer campo adicional `z` (matriz)
2. **Tipos "histogram" e "box"** funcionam apenas com campo `y`
3. **Fallback automático** garante que nenhum gráfico falhe completamente
4. **Cores personalizadas** são opcionais em todos os tipos

---

**Arquivo de implementação:** `streamlit_app.py` (linhas 646-811)
