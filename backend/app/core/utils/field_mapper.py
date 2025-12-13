# backend/app/core/utils/field_mapper.py

import json
from typing import Any, Dict, List, Optional

class FieldMapper:
    """
    Maps natural language terms to actual database field names using a catalog.
    Also provides known fields for agents.
    """
    def __init__(self, catalog_path: str = "data/catalog_focused.json"):
        self.catalog_path = catalog_path
        self.catalog = self._load_catalog(catalog_path)
        self.reverse_catalog = {v: k for k, v in self.catalog.items()} # For mapping back if needed

    def _load_catalog(self, catalog_path: str) -> Dict[str, Any]:
        """
        Loads the catalog from a JSON file.
        Placeholder implementation. In a real scenario, this would load a dynamic catalog.
        """
        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                # Assuming the catalog file has a structure that maps natural language
                # terms to their corresponding database/parquet field names.
                # Example: {"unidade de negocio": "une_id", "produto": "produto_id"}
                data = json.load(f)
                # Flatten or process the loaded data as needed
                # For now, a simple direct mapping from a flat dict is assumed.
                if isinstance(data, dict):
                    # Simple example: if catalog is a direct mapping
                    return {k.lower(): v for k, v in data.items()}
                else:
                    print(f"Warning: Catalog file {catalog_path} has unexpected structure. Using default placeholder catalog.")
                    return self._get_default_placeholder_catalog()
        except FileNotFoundError:
            print(f"Warning: Catalog file {catalog_path} not found. Using default placeholder catalog.")
            return self._get_default_placeholder_catalog()
        except json.JSONDecodeError:
            print(f"Warning: Error decoding JSON from {catalog_path}. Using default placeholder catalog.")
            return self._get_default_placeholder_catalog()

    def _get_default_placeholder_catalog(self) -> Dict[str, str]:
        """Default catalog if file not found or invalid."""
        return {
            "unidade de negocio": "une_id",
            "produto": "produto_id",
            "segmento de mercado": "segmento",
            "margem de contribuicao": "media_considerada_lv", # Example mapping
            "estoque": "estoque_origem",
            "linha verde": "linha_verde",
            "vendas diarias": "vendas_diarias",
            "transferencias pendentes": "transferencias_pendentes",
            "id da une": "une_id", # common variations
            "id do produto": "produto_id"
        }

    def map_term(self, natural_language_term: str) -> Optional[str]:
        """
        Maps a natural language term to its corresponding database field name.
        Performs a case-insensitive lookup.
        """
        if not isinstance(natural_language_term, str):
            return None
        return self.catalog.get(natural_language_term.lower(), natural_language_term)

    def get_known_fields(self) -> List[str]:
        """
        Returns a list of all known natural language terms in the catalog.
        """
        return list(self.catalog.keys())

    def get_db_fields(self) -> List[str]:
        """
        Returns a list of all known database field names in the catalog.
        """
        return list(set(self.catalog.values()))

    def suggest_correction(self, invalid_term: str) -> Optional[str]:
        """
        Suggests a correction for an invalid term based on similarity.
        Placeholder for a more advanced fuzzy matching implementation.
        """
        # For now, a very simple suggestion (e.g., if it's close to a known field)
        # Could use fuzzywuzzy or difflib for better matching
        invalid_term_lower = invalid_term.lower()
        for nl_term, db_field in self.catalog.items():
            if invalid_term_lower in nl_term or nl_term in invalid_term_lower:
                return nl_term # Return the natural language term as a suggestion
        return None

if __name__ == '__main__':
    # Create a dummy catalog_focused.json for testing
    dummy_catalog_path = "data/catalog_focused.json"
    dummy_catalog_content = {
        "unidade de negocio": "une_id",
        "produto": "produto_id",
        "segmento": "segmento",
        "quantidade estoque": "estoque_origem"
    }
    # Ensure 'data' directory exists for this test
    import os
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(dummy_catalog_path, 'w', encoding='utf-8') as f:
        json.dump(dummy_catalog_content, f, indent=4)

    print("--- Testing FieldMapper ---")
    mapper = FieldMapper()
    
    print(f"Map 'Unidade de Negocio': {mapper.map_term('Unidade de Negocio')}")
    print(f"Map 'PRODUTO': {mapper.map_term('PRODUTO')}")
    print(f"Map 'segmento': {mapper.map_term('segmento')}")
    print(f"Map 'quantidade em estoque': {mapper.map_term('quantidade em estoque')}") # Should map to estoque_origem if it recognizes a close match

    print(f"Known fields: {mapper.get_known_fields()}")
    print(f"DB fields: {mapper.get_db_fields()}")

    print(f"Suggest for 'unidade': {mapper.suggest_correction('unidade')}")
    print(f"Suggest for 'produt': {mapper.suggest_correction('produt')}")
    print(f"Suggest for 'non_existent_field': {mapper.suggest_correction('non_existent_field')}")

    # Clean up dummy file
    os.remove(dummy_catalog_path)
    print(f"Cleaned up dummy catalog: {dummy_catalog_path}")
