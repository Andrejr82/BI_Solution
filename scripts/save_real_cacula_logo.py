"""
Script para salvar o logo REAL da Caçula
IMPORTANTE: Este script precisa da imagem original fornecida pelo usuário
"""
from PIL import Image
import requests
from io import BytesIO
from pathlib import Path
import sys

def save_from_url(url):
    """Baixa e salva o logo de uma URL"""
    try:
        print(f"Baixando logo de: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content))

        # Converter para RGBA se necessário
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Redimensionar mantendo proporção (altura 200px)
        aspect_ratio = img.width / img.height
        new_height = 200
        new_width = int(new_height * aspect_ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Salvar
        output_path = Path(__file__).parent.parent / "assets" / "images" / "cacula_logo.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        img.save(output_path, "PNG", optimize=True)
        print(f"✅ Logo salvo em: {output_path}")
        print(f"   Tamanho: {new_width}x{new_height}px")
        return True

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def save_from_file(file_path):
    """Copia logo de um arquivo local"""
    try:
        img = Image.open(file_path)

        # Converter para RGBA se necessário
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Redimensionar mantendo proporção (altura 200px)
        aspect_ratio = img.width / img.height
        new_height = 200
        new_width = int(new_height * aspect_ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Salvar
        output_path = Path(__file__).parent.parent / "assets" / "images" / "cacula_logo.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        img.save(output_path, "PNG", optimize=True)
        print(f"✅ Logo salvo em: {output_path}")
        print(f"   Tamanho: {new_width}x{new_height}px")
        return True

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("=" * 70)
    print(" SALVAR LOGO REAL DA CAÇULA")
    print("=" * 70)
    print()
    print("Opções:")
    print("1. Baixar de URL")
    print("2. Copiar de arquivo local")
    print("3. Sair")
    print()

    choice = input("Escolha (1-3): ").strip()

    if choice == "1":
        print()
        print("URLs sugeridas do logo Caçula:")
        print("- Site oficial: https://www.cacula.com.br/")
        print("- Ou cole a URL direta da imagem")
        print()
        url = input("Cole a URL: ").strip()
        if url:
            save_from_url(url)

    elif choice == "2":
        print()
        file_path = input("Cole o caminho do arquivo: ").strip('"').strip("'")
        if file_path:
            save_from_file(file_path)

    else:
        print("\nOperação cancelada")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperação interrompida")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
