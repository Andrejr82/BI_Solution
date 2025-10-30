"""
Script para salvar a nova logo Caçula.

INSTRUÇÕES:
1. Baixe a Image #1 que você forneceu (personagem 3D colorido)
2. Execute este script
3. Quando solicitado, forneça o caminho da imagem baixada
"""

from pathlib import Path
import shutil

def salvar_logo():
    print("=" * 80)
    print("SALVANDO NOVA LOGO CAÇULA")
    print("=" * 80)
    print()

    # Caminho de destino
    destino = Path(__file__).parent / "assets" / "images" / "cacula_logo.png"

    print(f"Destino: {destino}")
    print()

    # Solicitar caminho da imagem
    print("Cole o caminho completo da imagem que você baixou:")
    print("Exemplo: C:\\Users\\André\\Downloads\\cacula_personagem.png")
    print()

    origem = input("Caminho da imagem: ").strip().strip('"').strip("'")

    if not Path(origem).exists():
        print(f"❌ ERRO: Arquivo não encontrado em: {origem}")
        return

    try:
        # Fazer backup se já existir
        if destino.exists():
            backup = destino.parent / "cacula_logo_backup.png"
            shutil.copy(destino, backup)
            print(f"✅ Backup criado: {backup}")

        # Copiar nova logo
        shutil.copy(origem, destino)
        print(f"✅ Logo salva com sucesso em: {destino}")
        print()
        print("PRÓXIMOS PASSOS:")
        print("1. Reiniciar o Streamlit")
        print("2. Verificar logo no sidebar")
        print("3. Verificar logo nas mensagens do assistente")

    except Exception as e:
        print(f"❌ ERRO ao copiar: {e}")

if __name__ == "__main__":
    salvar_logo()
