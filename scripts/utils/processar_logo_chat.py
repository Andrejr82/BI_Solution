"""
Script para processar e redimensionar logo Caçula para uso no chat.

Cria versão 80x80px otimizada para avatar do chat Streamlit.
"""

from PIL import Image
from pathlib import Path
import sys

def processar_logo():
    """Redimensiona logo para chat mantendo qualidade"""

    print("=" * 80)
    print("PROCESSANDO LOGO CAÇULA PARA CHAT")
    print("=" * 80)
    print()

    # Caminhos
    assets_dir = Path(__file__).parent / "assets" / "images"
    logo_original = assets_dir / "cacula_logo.png"
    logo_chat = assets_dir / "cacula_logo_chat.png"

    # Verificar se logo original existe
    if not logo_original.exists():
        print(f"[ERRO] Logo original nao encontrada em: {logo_original}")
        print()
        print("SOLUCAO:")
        print("1. Salve a Image #1 (logo Cacula colorida)")
        print(f"2. Copie para: {logo_original}")
        print("3. Execute este script novamente")
        return False

    try:
        print(f"[OK] Logo original encontrada: {logo_original}")

        # Abrir imagem
        img = Image.open(logo_original)
        print(f"   Tamanho original: {img.size[0]}x{img.size[1]}px")
        print(f"   Modo: {img.mode}")

        # Redimensionar para 80x80px (mantém proporção)
        # Usa LANCZOS para melhor qualidade
        img_chat = img.copy()
        img_chat.thumbnail((80, 80), Image.Resampling.LANCZOS)

        # Converter para RGBA se necessário (transparência)
        if img_chat.mode != 'RGBA':
            img_chat = img_chat.convert('RGBA')

        # Salvar versão para chat
        img_chat.save(logo_chat, 'PNG', optimize=True)

        print()
        print(f"[OK] Logo para chat criada: {logo_chat}")
        print(f"   Tamanho final: {img_chat.size[0]}x{img_chat.size[1]}px")
        print(f"   Formato: PNG com transparencia")

        print()
        print("=" * 80)
        print("[SUCESSO] PROCESSAMENTO CONCLUIDO!")
        print("=" * 80)
        print()
        print("PROXIMOS PASSOS:")
        print("1. Reiniciar Streamlit")
        print("2. Verificar logo aparece corretamente no chat")
        print("3. Verificar logo NAO esta cortada")

        return True

    except Exception as e:
        print(f"[ERRO] ao processar logo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = processar_logo()
    sys.exit(0 if sucesso else 1)
