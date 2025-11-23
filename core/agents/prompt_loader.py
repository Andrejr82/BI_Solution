"""
Módulo para core/agents/prompt_loader.py. Define a classe principal 'PromptLoader'. Fornece as funções: load_prompt, list_available_prompts, save_prompt.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/agent.log",
    filemode="a",
)
logger = logging.getLogger("prompt_loader")


class PromptLoader:
    """
    Classe responsável por carregar prompts externos em formato JSON
    """

    def __init__(self, prompts_dir: str = None):
        """
        Inicializa o carregador de prompts

        Args:
            prompts_dir (str): Diretório onde os arquivos de prompt estão localizados
        """
        # Define o diretório de prompts padrão se não for especificado
        if prompts_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.prompts_dir = os.path.join(base_dir, "prompts")
        else:
            self.prompts_dir = prompts_dir

        # Cria o diretório de prompts se não existir
        if not os.path.exists(self.prompts_dir):
            try:
                os.makedirs(self.prompts_dir)
                logger.info(f"Diretório de prompts criado: {self.prompts_dir}")
            except Exception as e:
                logger.error(f"Erro ao criar diretório de prompts: {e}")

        logger.info(
            f"Carregador de prompts inicializado. Diretório: {self.prompts_dir}"
        )

    def load_prompt(self, prompt_name: str) -> Optional[Dict[str, Any]]:
        """
        Carrega um prompt específico pelo nome do arquivo

        Args:
            prompt_name (str): Nome do arquivo de prompt (sem extensão)

        Returns:
            dict: Conteúdo do prompt carregado ou None se ocorrer erro
        """
        # Adiciona a extensão .json se não estiver presente
        if not prompt_name.endswith(".json"):
            prompt_file = f"{prompt_name}.json"
        else:
            prompt_file = prompt_name

        # Constrói o caminho completo do arquivo
        prompt_path = os.path.join(self.prompts_dir, prompt_file)

        # Verifica se o arquivo existe
        if not os.path.exists(prompt_path):
            logger.error(f"Arquivo de prompt não encontrado: {prompt_path}")
            return None

        # Carrega o arquivo JSON
        try:
            with open(prompt_path, "r", encoding="utf-8") as file:
                prompt_data = json.load(file)
                logger.info(f"Prompt carregado com sucesso: {prompt_name}")
                return prompt_data
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON do prompt {prompt_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao carregar prompt {prompt_name}: {e}")
            return None

    def list_available_prompts(self) -> list:
        """
        Lista todos os prompts disponíveis no diretório

        Returns:
            list: Lista de nomes de arquivos de prompt disponíveis
        """
        try:
            # Lista todos os arquivos .json no diretório de prompts
            prompt_files = [
                f
                for f in os.listdir(self.prompts_dir)
                if f.endswith(".json")
                and os.path.isfile(os.path.join(self.prompts_dir, f))
            ]
            return prompt_files
        except Exception as e:
            logger.error(f"Erro ao listar prompts disponíveis: {e}")
            return []

    def save_prompt(self, prompt_name: str, prompt_data: Dict[str, Any]) -> bool:
        """
        Salva um prompt em formato JSON

        Args:
            prompt_name (str): Nome do arquivo de prompt (sem extensão)
            prompt_data (dict): Dados do prompt a serem salvos

        Returns:
            bool: True se o prompt foi salvo com sucesso, False caso contrário
        """
        # Adiciona a extensão .json se não estiver presente
        if not prompt_name.endswith(".json"):
            prompt_file = f"{prompt_name}.json"
        else:
            prompt_file = prompt_name

        # Constrói o caminho completo do arquivo
        prompt_path = os.path.join(self.prompts_dir, prompt_file)

        # Salva o arquivo JSON
        try:
            with open(prompt_path, "w", encoding="utf-8") as file:
                json.dump(prompt_data, file, ensure_ascii=False, indent=4)
                logger.info(f"Prompt salvo com sucesso: {prompt_name}")
                return True
        except Exception as e:
            logger.error(f"Erro ao salvar prompt {prompt_name}: {e}")
            return False

    def load_prompt_template(self, prompt_name: str) -> Optional[str]:
        """
        Carrega um template de prompt em formato Markdown (.md)
        
        Args:
            prompt_name (str): Nome do arquivo de prompt (com ou sem extensão .md)
            
        Returns:
            str: Conteúdo do template ou None se ocorrer erro
        """
        # Adiciona a extensão .md se não estiver presente
        if not prompt_name.endswith(".md"):
            prompt_file = f"{prompt_name}.md"
        else:
            prompt_file = prompt_name
        
        # Constrói o caminho completo do arquivo
        prompt_path = os.path.join(self.prompts_dir, prompt_file)
        
        # Verifica se o arquivo existe
        if not os.path.exists(prompt_path):
            logger.error(f"Template de prompt não encontrado: {prompt_path}")
            return None
        
        # Carrega o arquivo Markdown
        try:
            with open(prompt_path, "r", encoding="utf-8") as file:
                template_content = file.read()
                logger.info(f"Template de prompt carregado com sucesso: {prompt_name}")
                return template_content
        except Exception as e:
            logger.error(f"Erro ao carregar template de prompt {prompt_name}: {e}")
            return None
    
    def inject_context_into_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Injeta contexto dinâmico em um template de prompt usando placeholders.
        
        Placeholders esperados no template:
        - [CONTEXTO_DADOS]: Será substituído pelo esquema de banco de dados
        - [OBJETIVO_ATÔMICO]: Será substituído pelo objetivo da tarefa
        - [FORMATO_RESPOSTA]: Será substituído pelas instruções de formato
        - [PERGUNTA_USUARIO]: Será substituído pela pergunta do usuário
        
        Args:
            template (str): Conteúdo do template com placeholders
            context (Dict[str, Any]): Dicionário com valores para substituição
            
        Returns:
            str: Template com contexto injetado
        """
        result = template
        
        # Substitui placeholders por valores do contexto
        for placeholder, value in context.items():
            placeholder_key = f"[{placeholder}]"
            if isinstance(value, dict):
                # Se o valor é um dicionário, converte para string formatada
                value_str = json.dumps(value, ensure_ascii=False, indent=2)
            else:
                value_str = str(value)
            
            result = result.replace(placeholder_key, value_str)
            logger.debug(f"Placeholder {placeholder_key} substituído com sucesso")
        
        return result
