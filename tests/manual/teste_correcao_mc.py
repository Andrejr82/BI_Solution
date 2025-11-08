"""
Teste da correcao da funcao calcular_mc_produto
"""
import sys
from pathlib import Path

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent))

from core.tools.une_tools import calcular_mc_produto

def teste_mc():
    """Testar funcao calcular_mc_produto com produto 369947 na UNE 2720"""

    print("=" * 80)
    print("TESTE: calcular_mc_produto(369947, 2720)")
    print("=" * 80)

    try:
        # Chamar como tool do LangChain usando invoke
        resultado = calcular_mc_produto.invoke({"produto_id": 369947, "une_id": 2720})

        print("\nResultado:")
        print("-" * 80)

        if 'error' in resultado:
            print(f"[ERRO] {resultado['error']}")
            print("\nDetalhes completos:")
            for k, v in resultado.items():
                print(f"  {k}: {v}")
        else:
            print("[OK] Produto encontrado!")
            print("\nInformacoes do produto:")
            print(f"  Produto ID:              {resultado.get('produto_id')}")
            print(f"  UNE ID:                  {resultado.get('une_id')}")
            print(f"  Nome:                    {resultado.get('nome')}")
            print(f"  Segmento:                {resultado.get('segmento')}")
            print(f"\n  MC Calculada:            {resultado.get('mc_calculada')}")
            print(f"  Estoque Atual:           {resultado.get('estoque_atual')}")
            print(f"  Linha Verde:             {resultado.get('linha_verde')}")
            print(f"  Percentual Linha Verde:  {resultado.get('percentual_linha_verde')}%")

            if 'estoque_gondola' in resultado:
                print(f"  Estoque Gondola:         {resultado.get('estoque_gondola')}")

            print(f"\n  Recomendacao:            {resultado.get('recomendacao')}")

    except Exception as e:
        print(f"[ERRO] Excecao: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)

if __name__ == "__main__":
    teste_mc()
