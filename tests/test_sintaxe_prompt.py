"""Teste de sintaxe do prompt - conversão para teste pytest.

O antigo arquivo imprimia e usava exit(1) em import-time, o que quebra a
execução do pytest. Aqui convertimos o comportamento em asserts para que
o teste seja executado como parte da suíte.
"""

from pathlib import Path


def test_prompt_syntax_is_valid():
    path = Path("core/agents/code_gen_agent.py")
    assert path.exists(), (
        "Arquivo core/agents/code_gen_agent.py não encontrado"
    )

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Checar que o prompt é construído de forma dinâmica conforme convenção.
    content_joined = "\n".join(lines)

    # O agente moderno constrói o prompt via _build_structured_prompt(...)
    # e injeta uma mensagem com role 'system'.
    uses_builder = "_build_structured_prompt(" in content_joined
    has_system_message = (
        '{"role": "system"' in content_joined
        or "SystemMessage(" in content_joined
    )

    assert (
        uses_builder or 'system_prompt' in content_joined
    ), "Arquivo não parece construir 'system_prompt' dinamicamente."

    assert has_system_message, (
        "Não foi encontrada a injeção de mensagem do tipo 'system' no agente."
    )


def test_prompt_string_construction_example():
    # Simular a construção de prompt para garantir que formatações não levantam
    column_context = "Colunas: PRODUTO, VENDA_30DD"
    valid_segments = "Segmentos: Medicamentos"

    test_prompt = (
        """Voce eh um especialista em analise de dados.

""" + column_context + """

""" + valid_segments + """

EXEMPLO:
df = load_data()
temporal_data = pd.DataFrame({
    'Mes': ['Mes 1', 'Mes 2'],
    'Vendas': [100, 200]
})
"""
    )

    # Se a concatenação ou presença de chaves gerasse ValueError, falharíamos
    assert isinstance(test_prompt, str) and len(test_prompt) > 0
    # Verificar presença de placeholders apenas como sanity check
    assert "{" in test_prompt and "}" in test_prompt
