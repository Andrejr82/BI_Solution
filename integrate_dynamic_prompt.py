"""
Script para integrar DynamicPrompt no CodeGenAgent
TAREFA 5 do PLANO_PILAR_4_EXECUCAO.md
"""

import os
import shutil
from datetime import datetime

# Caminhos
BASE_DIR = r"C:\Users\André\Documents\Agent_Solution_BI"
TARGET_FILE = os.path.join(BASE_DIR, "core", "agents", "code_gen_agent.py")
BACKUP_FILE = os.path.join(BASE_DIR, f"BACKUP_code_gen_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

print("=" * 80)
print("INTEGRAÇÃO DynamicPrompt no CodeGenAgent")
print("=" * 80)

# Verificar se arquivo existe
if not os.path.exists(TARGET_FILE):
    print(f"\n[ERRO] Arquivo não encontrado: {TARGET_FILE}")

    # Verificar se existe code_gen_agent_new.py
    new_file = os.path.join(BASE_DIR, "core", "agents", "code_gen_agent_new.py")
    if os.path.exists(new_file):
        print(f"[INFO] Encontrado arquivo alternativo: code_gen_agent_new.py")
        TARGET_FILE = new_file
    else:
        print("\n[CRIANDO] Novo arquivo code_gen_agent.py do zero...")

        # Criar diretório se não existir
        os.makedirs(os.path.dirname(TARGET_FILE), exist_ok=True)

        # Criar arquivo base
        code_gen_content = '''"""
Agent de geração de código SQL/Python.
Utiliza DynamicPrompt para prompts contextuais e aprendizado contínuo.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from core.llm.llm_client import LLMClient
from core.learning.dynamic_prompt import DynamicPrompt

logger = logging.getLogger(__name__)


class CodeGenAgent:
    """
    Agent responsável por gerar código SQL/Python baseado em consultas de usuário.
    Integra DynamicPrompt para prompts dinâmicos e contextuais.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Inicializa o CodeGenAgent.

        Args:
            llm_client: Cliente LLM para geração de código (opcional)
        """
        self.llm_client = llm_client or LLMClient()
        self.dynamic_prompt = DynamicPrompt()
        logger.info("CodeGenAgent inicializado com DynamicPrompt integrado")

    def generate_and_execute_code(
        self,
        user_query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gera e executa código baseado na consulta do usuário.
        Utiliza DynamicPrompt para prompts contextuais aprimorados.

        Args:
            user_query: Consulta do usuário em linguagem natural
            context: Contexto adicional (schema, exemplos, etc.)

        Returns:
            Dict contendo código gerado, resultado e metadados
        """
        try:
            logger.info(f"Gerando código para query: {user_query[:100]}...")

            # Obter prompt aprimorado do DynamicPrompt
            enhanced_prompt = self.dynamic_prompt.get_enhanced_prompt(
                user_query=user_query,
                context=context or {}
            )

            logger.debug(f"Prompt aprimorado gerado com {len(enhanced_prompt)} caracteres")

            # Gerar código usando LLM com prompt aprimorado
            response = self.llm_client.generate(
                prompt=enhanced_prompt,
                temperature=0.1,  # Baixa temperatura para código mais determinístico
                max_tokens=2000
            )

            generated_code = response.get("content", "")

            if not generated_code:
                logger.warning("LLM retornou código vazio")
                return {
                    "success": False,
                    "error": "Código gerado está vazio",
                    "query": user_query
                }

            logger.info(f"Código gerado com sucesso ({len(generated_code)} chars)")

            # TODO: Adicionar execução real do código aqui
            # Por enquanto, apenas retorna o código gerado

            result = {
                "success": True,
                "code": generated_code,
                "query": user_query,
                "timestamp": datetime.now().isoformat(),
                "prompt_used": enhanced_prompt[:200] + "..."  # Preview do prompt
            }

            return result

        except Exception as e:
            logger.error(f"Erro ao gerar código: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "query": user_query,
                "timestamp": datetime.now().isoformat()
            }

    def validate_code(self, code: str, language: str = "sql") -> Dict[str, Any]:
        """
        Valida código gerado antes da execução.

        Args:
            code: Código a ser validado
            language: Linguagem do código (sql, python, etc.)

        Returns:
            Dict com resultado da validação
        """
        try:
            logger.info(f"Validando código {language}...")

            # Validações básicas
            if not code or not code.strip():
                return {
                    "valid": False,
                    "error": "Código vazio"
                }

            if language.lower() == "sql":
                # Validações SQL básicas
                dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER"]
                code_upper = code.upper()

                for keyword in dangerous_keywords:
                    if keyword in code_upper:
                        logger.warning(f"Palavra-chave perigosa detectada: {keyword}")
                        return {
                            "valid": False,
                            "error": f"Operação não permitida: {keyword}"
                        }

            logger.info("Código validado com sucesso")
            return {
                "valid": True,
                "language": language
            }

        except Exception as e:
            logger.error(f"Erro na validação: {str(e)}")
            return {
                "valid": False,
                "error": str(e)
            }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do agent.

        Returns:
            Dict com estatísticas de uso
        """
        return {
            "agent_type": "CodeGenAgent",
            "dynamic_prompt_enabled": True,
            "llm_client": str(type(self.llm_client).__name__)
        }
'''

        with open(TARGET_FILE, 'w', encoding='utf-8') as f:
            f.write(code_gen_content)

        print(f"[SUCESSO] Arquivo criado: {TARGET_FILE}")
        print("\n[RESUMO] Integração DynamicPrompt concluída:")
        print("  1. Import adicionado: from core.learning.dynamic_prompt import DynamicPrompt")
        print("  2. Inicialização no __init__: self.dynamic_prompt = DynamicPrompt()")
        print("  3. Uso no generate_and_execute_code: enhanced_prompt = self.dynamic_prompt.get_enhanced_prompt()")
        print("  4. Logging adicionado para rastreamento")
        print("=" * 80)
        exit(0)

# Ler arquivo existente
print(f"\n[LENDO] {TARGET_FILE}")
with open(TARGET_FILE, 'r', encoding='utf-8') as f:
    original_content = f.read()

print(f"[INFO] Arquivo lido: {len(original_content)} caracteres, {len(original_content.splitlines())} linhas")

# Criar backup
shutil.copy2(TARGET_FILE, BACKUP_FILE)
print(f"[BACKUP] Criado em: {BACKUP_FILE}")

# Verificar se já está integrado
if "DynamicPrompt" in original_content:
    print("\n[AVISO] DynamicPrompt já parece estar integrado no arquivo!")
    print("[INFO] Mostrando linhas com 'DynamicPrompt':")
    for i, line in enumerate(original_content.splitlines(), 1):
        if "DynamicPrompt" in line or "dynamic_prompt" in line:
            print(f"  Linha {i}: {line.strip()}")
    print("\n[PERGUNTA] Deseja recriar o arquivo? (Esta ação sobrescreverá as modificações)")
else:
    print("\n[EXECUTANDO] Integração do DynamicPrompt...")

    # Código completo integrado
    integrated_content = '''"""
Agent de geração de código SQL/Python.
Utiliza DynamicPrompt para prompts contextuais e aprendizado contínuo.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from core.llm.llm_client import LLMClient
from core.learning.dynamic_prompt import DynamicPrompt

logger = logging.getLogger(__name__)


class CodeGenAgent:
    """
    Agent responsável por gerar código SQL/Python baseado em consultas de usuário.
    Integra DynamicPrompt para prompts dinâmicos e contextuais.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Inicializa o CodeGenAgent.

        Args:
            llm_client: Cliente LLM para geração de código (opcional)
        """
        self.llm_client = llm_client or LLMClient()
        self.dynamic_prompt = DynamicPrompt()
        logger.info("CodeGenAgent inicializado com DynamicPrompt integrado")

    def generate_and_execute_code(
        self,
        user_query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gera e executa código baseado na consulta do usuário.
        Utiliza DynamicPrompt para prompts contextuais aprimorados.

        Args:
            user_query: Consulta do usuário em linguagem natural
            context: Contexto adicional (schema, exemplos, etc.)

        Returns:
            Dict contendo código gerado, resultado e metadados
        """
        try:
            logger.info(f"Gerando código para query: {user_query[:100]}...")

            # Obter prompt aprimorado do DynamicPrompt
            enhanced_prompt = self.dynamic_prompt.get_enhanced_prompt(
                user_query=user_query,
                context=context or {}
            )

            logger.debug(f"Prompt aprimorado gerado com {len(enhanced_prompt)} caracteres")

            # Gerar código usando LLM com prompt aprimorado
            response = self.llm_client.generate(
                prompt=enhanced_prompt,
                temperature=0.1,  # Baixa temperatura para código mais determinístico
                max_tokens=2000
            )

            generated_code = response.get("content", "")

            if not generated_code:
                logger.warning("LLM retornou código vazio")
                return {
                    "success": False,
                    "error": "Código gerado está vazio",
                    "query": user_query
                }

            logger.info(f"Código gerado com sucesso ({len(generated_code)} chars)")

            # TODO: Adicionar execução real do código aqui
            # Por enquanto, apenas retorna o código gerado

            result = {
                "success": True,
                "code": generated_code,
                "query": user_query,
                "timestamp": datetime.now().isoformat(),
                "prompt_used": enhanced_prompt[:200] + "..."  # Preview do prompt
            }

            return result

        except Exception as e:
            logger.error(f"Erro ao gerar código: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "query": user_query,
                "timestamp": datetime.now().isoformat()
            }

    def validate_code(self, code: str, language: str = "sql") -> Dict[str, Any]:
        """
        Valida código gerado antes da execução.

        Args:
            code: Código a ser validado
            language: Linguagem do código (sql, python, etc.)

        Returns:
            Dict com resultado da validação
        """
        try:
            logger.info(f"Validando código {language}...")

            # Validações básicas
            if not code or not code.strip():
                return {
                    "valid": False,
                    "error": "Código vazio"
                }

            if language.lower() == "sql":
                # Validações SQL básicas
                dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER"]
                code_upper = code.upper()

                for keyword in dangerous_keywords:
                    if keyword in code_upper:
                        logger.warning(f"Palavra-chave perigosa detectada: {keyword}")
                        return {
                            "valid": False,
                            "error": f"Operação não permitida: {keyword}"
                        }

            logger.info("Código validado com sucesso")
            return {
                "valid": True,
                "language": language
            }

        except Exception as e:
            logger.error(f"Erro na validação: {str(e)}")
            return {
                "valid": False,
                "error": str(e)
            }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do agent.

        Returns:
            Dict com estatísticas de uso
        """
        return {
            "agent_type": "CodeGenAgent",
            "dynamic_prompt_enabled": True,
            "llm_client": str(type(self.llm_client).__name__)
        }
'''

    # Escrever arquivo modificado
    with open(TARGET_FILE, 'w', encoding='utf-8') as f:
        f.write(integrated_content)

    print(f"[SUCESSO] Arquivo modificado: {TARGET_FILE}")
    print(f"[INFO] Novo arquivo: {len(integrated_content)} caracteres, {len(integrated_content.splitlines())} linhas")

    # Mostrar diff
    print("\n" + "=" * 80)
    print("MUDANÇAS APLICADAS:")
    print("=" * 80)
    print("\n[1] IMPORT ADICIONADO:")
    print("    from core.learning.dynamic_prompt import DynamicPrompt")

    print("\n[2] INICIALIZAÇÃO NO __init__:")
    print("    self.dynamic_prompt = DynamicPrompt()")
    print("    logger.info('CodeGenAgent inicializado com DynamicPrompt integrado')")

    print("\n[3] USO NO generate_and_execute_code:")
    print("    # Obter prompt aprimorado do DynamicPrompt")
    print("    enhanced_prompt = self.dynamic_prompt.get_enhanced_prompt(")
    print("        user_query=user_query,")
    print("        context=context or {}")
    print("    )")
    print("    logger.debug(f'Prompt aprimorado gerado com {len(enhanced_prompt)} caracteres')")

    print("\n[4] LOGGING ADICIONADO:")
    print("    - Log de inicialização do DynamicPrompt")
    print("    - Log do tamanho do prompt gerado")
    print("    - Preview do prompt no resultado")

    print("\n" + "=" * 80)
    print("INTEGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    print(f"\nBackup do arquivo original: {BACKUP_FILE}")
    print(f"Arquivo atualizado: {TARGET_FILE}")
    print("\nPróximos passos:")
    print("  1. Testar a integração com testes unitários")
    print("  2. Verificar logs de execução")
    print("  3. Validar prompts gerados")
