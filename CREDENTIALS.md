# Credenciais de Acesso - Agent Solution BI

## Credenciais Padrão

### Usuário Administrador

```
Usuário: admin
Senha: Admin@2024
```

> [!IMPORTANT]
> **Atenção**: A senha é **case-sensitive** e contém caracteres especiais.
> - ✅ Correto: `Admin@2024`
> - ❌ Incorreto: `admin`, `admin123`, `Admin2024`

## Como Fazer Login

1. **Inicie o sistema**:
   ```bash
   RUN.bat
   ```
   Ou manualmente:
   ```bash
   python run.py
   ```

2. **Aguarde a inicialização**:
   - Backend estará disponível em: `http://localhost:8000`
   - Frontend estará disponível em: `http://localhost:3000`

3. **Acesse o frontend**:
   - O navegador abrirá automaticamente em `http://localhost:3000`
   - Ou acesse manualmente: `http://localhost:3000/login`

4. **Faça login**:
   - Digite: `admin`
   - Digite: `Admin@2024`
   - Clique em "Entrar"

## Troubleshooting

### Erro: "Backend não está disponível"

**Causa**: O backend FastAPI não está rodando na porta 8000.

**Solução**:
```bash
# Verifique se o backend está rodando
python diagnose_system.py

# Inicie apenas o backend
python run.py --backend-only
```

### Erro: "Credenciais inválidas"

**Causa**: Senha incorreta ou usuário não existe.

**Soluções**:
1. Verifique se está usando `Admin@2024` (com A maiúsculo e @)
2. Verifique se o arquivo `data/parquet/users.parquet` existe
3. Execute o diagnóstico:
   ```bash
   python diagnose_system.py
   ```

### Erro: "Network Error"

**Causa**: Frontend não consegue conectar ao backend.

**Soluções**:
1. Verifique se o backend está rodando:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

2. Reinicie o sistema:
   ```bash
   # Mate processos na porta 8000
   python kill_port.py 8000
   
   # Reinicie
   python run.py
   ```

## Verificação do Sistema

Execute o script de diagnóstico para verificar se tudo está configurado corretamente:

```bash
python diagnose_system.py
```

Este script verifica:
- ✅ Backend está rodando na porta 8000
- ✅ Endpoint de health responde
- ✅ Arquivo de usuários existe
- ✅ Hash de senha está correto
- ✅ Endpoint de login funciona
- ✅ Configuração do frontend está correta

## Alterando a Senha

Para alterar a senha do usuário admin, você precisará:

1. Gerar um novo hash bcrypt
2. Atualizar o arquivo `data/parquet/users.parquet`
3. Ou atualizar diretamente no SQL Server (se habilitado)

### Exemplo de geração de hash:

```python
import bcrypt

nova_senha = "MinhaNovaSenh@123"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(nova_senha.encode('utf-8'), salt)
print(hashed.decode('utf-8'))
```

## Suporte

Se você continuar tendo problemas:

1. Execute o diagnóstico completo: `python diagnose_system.py`
2. Verifique os logs do backend em tempo real
3. Verifique o console do navegador (F12) para erros do frontend
4. Consulte a documentação em `docs/`
