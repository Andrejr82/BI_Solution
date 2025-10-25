# Instruções para Adicionar o Logo da Caçula

## 📋 Passo a Passo

### Opção 1: Upload Manual (Mais Simples)
1. Salve o logo da Caçula como `cacula_logo.png`
2. Copie o arquivo para a pasta: `assets/images/cacula_logo.png`
3. Reinicie o Streamlit

### Opção 2: Usando Python
Execute o seguinte script Python:

```python
from PIL import Image
import requests
from io import BytesIO

# Se você tem a imagem em um URL
url = "https://[URL_DO_LOGO_CACULA]"
response = requests.get(url)
img = Image.open(BytesIO(response.content))

# Ou se você tem a imagem local
# img = Image.open("caminho/para/logo.png")

# Redimensionar para tamanho ideal (opcional)
img = img.resize((200, 200), Image.Resampling.LANCZOS)

# Salvar
img.save("assets/images/cacula_logo.png")
print("✅ Logo salvo com sucesso!")
```

### Opção 3: Converter de Base64
Se você tem a imagem em base64:

```python
import base64
from pathlib import Path

# Cole aqui o base64 da imagem
logo_base64 = """
[COLE_AQUI_O_BASE64_DA_IMAGEM]
"""

# Salvar
output_path = Path("assets/images/cacula_logo.png")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'wb') as f:
    f.write(base64.b64decode(logo_base64.strip()))

print("✅ Logo salvo!")
```

## 🎨 Formato Recomendado
- **Formato**: PNG com transparência
- **Tamanho**: 200x200 pixels (quadrado)
- **Fundo**: Transparente (opcional, mas recomendado)

## 📍 Local do Arquivo
```
Agent_Solution_BI/
├── assets/
│   └── images/
│       └── cacula_logo.png  ← Coloque o arquivo aqui
```

## ✅ Verificação
Após adicionar o logo:
1. Reinicie o Streamlit: `streamlit run streamlit_app.py`
2. O logo deve aparecer:
   - No sidebar (centralizado)
   - Nas mensagens do assistente (como avatar)

## 🔄 Fallback
Se o logo não for encontrado, o sistema usará automaticamente:
- Emoji padrão do Streamlit para o assistente
- Layout sem logo no sidebar

## 🐛 Troubleshooting
Se o logo não aparecer:
1. Verifique se o arquivo existe: `assets/images/cacula_logo.png`
2. Verifique as permissões do arquivo
3. Confirme que o formato é PNG
4. Limpe o cache do Streamlit: `streamlit cache clear`
