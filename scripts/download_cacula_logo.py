"""
Script para baixar e salvar o logo da Caçula
NOTA: Execute este script para adicionar o logo ao sistema
"""
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

def save_placeholder_logo():
    """
    Cria um logo placeholder até que o logo real seja adicionado
    """
    from PIL import Image, ImageDraw, ImageFont

    # Criar diretório se não existir
    logo_dir = root_dir / "assets" / "images"
    logo_dir.mkdir(parents=True, exist_ok=True)
    logo_path = logo_dir / "cacula_logo.png"

    # Criar imagem placeholder 200x200 com fundo transparente
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Desenhar círculo colorido (similar ao logo Caçula)
    colors = [
        (255, 0, 0),      # Vermelho
        (255, 165, 0),    # Laranja
        (255, 255, 0),    # Amarelo
        (0, 255, 0),      # Verde
        (0, 191, 255),    # Azul claro
        (138, 43, 226),   # Roxo
    ]

    # Desenhar pétalas coloridas (simulando a borboleta do logo)
    center = 100
    radius = 80

    for i, color in enumerate(colors):
        angle = i * 60
        draw.ellipse([
            center - radius//2,
            center - radius//2,
            center + radius//2,
            center + radius//2
        ], fill=color + (180,))  # Com transparência

    # Salvar
    img.save(logo_path, "PNG")
    print(f"✅ Logo placeholder salvo em: {logo_path}")
    print("📝 Para usar o logo real da Caçula, substitua este arquivo pelo logo original")

    return str(logo_path)

def download_from_url(url):
    """
    Baixa o logo de uma URL
    """
    import requests
    from PIL import Image
    from io import BytesIO

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content))

        # Salvar
        logo_dir = root_dir / "assets" / "images"
        logo_dir.mkdir(parents=True, exist_ok=True)
        logo_path = logo_dir / "cacula_logo.png"

        img.save(logo_path, "PNG")
        print(f"✅ Logo baixado e salvo em: {logo_path}")
        return str(logo_path)
    except Exception as e:
        print(f"❌ Erro ao baixar logo: {e}")
        print("🔄 Criando logo placeholder...")
        return save_placeholder_logo()

def main():
    print("🎨 Configurando logo da Caçula...")
    print()

    # Verificar se já existe
    logo_path = root_dir / "assets" / "images" / "cacula_logo.png"
    if logo_path.exists():
        print(f"ℹ️ Logo já existe em: {logo_path}")
        overwrite = input("Deseja substituir? (s/n): ").lower()
        if overwrite != 's':
            print("✅ Logo mantido")
            return

    # Opções
    print("Escolha uma opção:")
    print("1. Criar logo placeholder temporário")
    print("2. Baixar de URL")
    print("3. Sair (adicionar manualmente)")
    print()

    choice = input("Opção (1-3): ").strip()

    if choice == "1":
        save_placeholder_logo()
    elif choice == "2":
        url = input("Cole a URL do logo: ").strip()
        download_from_url(url)
    else:
        print("📝 Adicione o logo manualmente em:")
        print(f"   {logo_path}")
        print()
        print("Formato recomendado: PNG 200x200 com fundo transparente")

if __name__ == "__main__":
    main()
