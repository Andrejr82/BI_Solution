"""
Script para substituir o logo placeholder pelo logo real da Caçula
"""
import shutil
from pathlib import Path

def substituir_logo():
    """
    Substitui o logo placeholder pelo logo real
    """
    print("=" * 60)
    print("SUBSTITUICAO DO LOGO CACULA")
    print("=" * 60)
    print()

    # Caminhos
    root_dir = Path(__file__).parent.parent
    logo_destino = root_dir / "assets" / "images" / "cacula_logo.png"

    print(f"Destino: {logo_destino}")
    print()

    # Verificar se ja existe
    if logo_destino.exists():
        print(f"[!] Logo atual encontrado:")
        print(f"    Tamanho: {logo_destino.stat().st_size} bytes")
        print()

        confirmar = input("Deseja substituir o logo atual? (s/n): ").strip().lower()
        if confirmar != 's':
            print("\n[X] Operacao cancelada pelo usuario")
            return

    print()
    print("Opcoes de substituicao:")
    print("1. Copiar de um arquivo local")
    print("2. Informacoes para download manual")
    print("3. Cancelar")
    print()

    opcao = input("Escolha uma opcao (1-3): ").strip()

    if opcao == "1":
        print()
        caminho_origem = input("Cole o caminho completo do logo real: ").strip()
        caminho_origem = Path(caminho_origem.strip('"').strip("'"))

        if not caminho_origem.exists():
            print(f"\n[X] Erro: Arquivo nao encontrado: {caminho_origem}")
            return

        # Copiar
        shutil.copy2(caminho_origem, logo_destino)
        print(f"\n[OK] Logo substituido com sucesso!")
        print(f"     De: {caminho_origem}")
        print(f"     Para: {logo_destino}")
        print()
        print("[*] Reinicie o Streamlit para ver as mudancas")

    elif opcao == "2":
        print()
        print("=" * 60)
        print("INSTRUCOES PARA DOWNLOAD MANUAL")
        print("=" * 60)
        print()
        print("1. Baixe o logo oficial da Cacula (formato PNG)")
        print("2. Salve o arquivo com o nome: cacula_logo.png")
        print("3. Copie o arquivo para:")
        print(f"   {logo_destino}")
        print()
        print("Formato recomendado:")
        print("  - Tipo: PNG com transparencia")
        print("  - Tamanho: 200x200 pixels (quadrado)")
        print("  - Fundo: Transparente (opcional)")
        print()
        print("4. Reinicie o Streamlit")
        print()

    else:
        print("\n[X] Operacao cancelada")

if __name__ == "__main__":
    try:
        substituir_logo()
    except KeyboardInterrupt:
        print("\n\n[X] Operacao interrompida pelo usuario")
    except Exception as e:
        print(f"\n[X] Erro: {e}")
