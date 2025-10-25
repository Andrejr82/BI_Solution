"""
Script para salvar o logo da Caçula como arquivo PNG
"""
import base64
from pathlib import Path

# Imagem fornecida pelo usuário (logo Caçula)
# Nota: Esta é uma imagem placeholder - você precisará fornecer a imagem real
logo_cacula = """
iVBORw0KGgoAAAANSUhEUgAAAMgAAAAyCAYAAAAZUZThAAAACXBIWXMAAAsTAAALEwEAmpwYAAAF
[IMAGEM_BASE64_AQUI]
"""

def save_logo():
    """Salva o logo da Caçula em assets/images"""
    output_path = Path(__file__).parent.parent / "assets" / "images" / "cacula_logo.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Decodificar base64 e salvar
        logo_bytes = base64.b64decode(logo_cacula.strip())

        with open(output_path, 'wb') as f:
            f.write(logo_bytes)

        print(f"✅ Logo salvo em: {output_path}")
        return str(output_path)
    except Exception as e:
        print(f"❌ Erro ao salvar logo: {e}")
        return None

if __name__ == "__main__":
    save_logo()
