"""
Script simples para criar logo placeholder da Cacula
"""
from PIL import Image, ImageDraw
from pathlib import Path

def create_logo():
    # Criar diretorio
    logo_dir = Path(__file__).parent.parent / "assets" / "images"
    logo_dir.mkdir(parents=True, exist_ok=True)
    logo_path = logo_dir / "cacula_logo.png"

    # Criar imagem 200x200 com fundo transparente
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Cores da borboleta Cacula
    colors = [
        (255, 0, 0, 200),      # Vermelho
        (255, 165, 0, 200),    # Laranja
        (255, 255, 0, 200),    # Amarelo
        (0, 255, 0, 200),      # Verde
        (0, 191, 255, 200),    # Azul claro
        (138, 43, 226, 200),   # Roxo
    ]

    # Desenhar petals em circulo
    center = 100
    petal_size = 50
    num_petals = len(colors)

    import math
    for i, color in enumerate(colors):
        angle = (i * 360 / num_petals) * (math.pi / 180)
        x = center + int(40 * math.cos(angle))
        y = center + int(40 * math.sin(angle))

        draw.ellipse([
            x - petal_size//2,
            y - petal_size//2,
            x + petal_size//2,
            y + petal_size//2
        ], fill=color)

    # Centro preto
    draw.ellipse([
        center - 20,
        center - 20,
        center + 20,
        center + 20
    ], fill=(0, 0, 0, 255))

    # Salvar
    img.save(logo_path, "PNG")
    print(f"Logo salvo em: {logo_path}")
    return str(logo_path)

if __name__ == "__main__":
    create_logo()
