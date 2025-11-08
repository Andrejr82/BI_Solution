"""
Mapeamento de UNEs (Unidades de Negócio) - Siglas e Códigos
Sistema: Agent_Solution_BI
Data: 2025-10-25
Atualizado: Dados reais do banco de dados (42 UNEs)

Este módulo contém o mapeamento entre siglas/nomes de UNEs e seus códigos numéricos.
Usado para normalizar queries do usuário e evitar erros de inferência do LLM.
"""

# Dicionário principal: Sigla/Nome → Código Numérico
# DADOS REAIS DO BANCO - 42 UNEs
UNE_MAP = {
    # UNEs principais
    "scr": "1",
    "são cristóvão": "1",
    "sao cristovao": "1",
    "une scr": "1",

    "alc": "3",
    "alcântara": "3",
    "une alc": "3",

    "dc": "11",
    "une dc": "11",

    "cfr": "35",
    "une cfr": "35",

    "pet": "57",
    "petrópolis": "57",
    "une pet": "57",

    "vvl": "61",
    "une vvl": "61",

    "vil": "64",
    "une vil": "64",

    "rep": "79",
    "une rep": "79",

    "jfa": "81",
    "juiz de fora": "81",
    "une jfa": "81",

    "nit": "135",
    "niterói": "135",
    "une nit": "135",

    "cgr": "148",
    "une cgr": "148",

    "obe": "265",
    "une obe": "265",

    "261": "1685",
    "buenos aires": "1685",
    "une 261": "1685",

    "cxa": "520",
    "caxias": "520",
    "une cxa": "520",

    "bgu": "1974",
    "une bgu": "1974",

    "alp": "2137",
    "une alp": "2137",

    "bar": "2365",
    "barra": "2365",
    "une bar": "2365",

    "cp2": "2401",
    "copacabana": "2401",
    "une cp2": "2401",

    "jrd": "2475",
    "jardim": "2475",
    "une jrd": "2475",

    "nig": "2586",
    "une nig": "2586",

    "ita": "2599",
    "itaboraí": "2599",
    "itaborai": "2599",
    "une ita": "2599",

    "mad": "2720",
    "madureira": "2720",
    "une mad": "2720",

    "jfj": "2906",
    "une jfj": "2906",

    "cam": "2952",
    "campos": "2952",
    "une cam": "2952",

    "vrd": "3038",
    "verde": "3038",
    "une vrd": "3038",

    "sgo": "3054",
    "une sgo": "3054",

    "nfr": "3091",
    "nova friburgo": "3091",
    "une nfr": "3091",

    "tij": "3116",
    "tijuca": "3116",
    "une tij": "3116",

    "ang": "3281",
    "angra": "3281",
    "une ang": "3281",

    "bon": "3318",
    "une bon": "3318",

    "ipa": "3387",
    "ipanema": "3387",
    "une ipa": "3387",

    "bot": "3404",
    "botafogo": "3404",
    "une bot": "3404",

    "nil": "3481",
    "une nil": "3481",

    "taq": "3499",
    "une taq": "3499",

    "rdo": "3577",
    "une rdo": "3577",

    "3rs": "3578",
    "une 3rs": "3578",

    "sts": "5570",
    "santos": "5570",
    "une sts": "5570",

    "nam": "5822",
    "une nam": "5822",
}

# Dicionário reverso: Código → Nome Oficial
UNE_NAMES = {
    "1": "SCR - São Cristóvão",
    "3": "ALC - Alcântara",
    "11": "DC - Vila Tecidos",
    "35": "CFR - Cabo Frio",
    "57": "PET - Petrópolis",
    "61": "VVL - Vila Velha",
    "64": "VIL - Vilar",
    "79": "REP - Resende",
    "81": "JFA - Juiz de Fora",
    "135": "NIT - Niterói",
    "148": "CGR - Campos Grande",
    "265": "OBE - Obelisco",
    "520": "CXA - Caxias",
    "1685": "261 - Buenos Aires",
    "1974": "BGU - Bangu",
    "2137": "ALP",
    "2365": "BAR - Barra",
    "2401": "CP2 - Copacabana",
    "2475": "JRD - Jurandir",
    "2586": "NIG - Nova Iguaçu",
    "2599": "ITA - Itaboraí",
    "2720": "MAD - Madureira",
    "2906": "JFJ - Juiz de Fora Centro",
    "2952": "CAM - Campos dos Goytacazes",
    "3038": "VRD - Volta Redonda",
    "3054": "SGO - São Gonçalo",
    "3091": "NFR - Nova Friburgo",
    "3116": "TIJ - Tijuca",
    "3281": "ANG - Angra dos Reis",
    "3318": "BON - Bonsucesso",
    "3387": "IPA - Ipanema",
    "3404": "BOT - Botafogo",
    "3481": "NIL - Nilópolis",
    "3499": "TAQ - Taquara",
    "3577": "RDO - Rio das Ostras",
    "3578": "3RS - Três Rios",
    "5570": "STS - Santa Cruz da Serra",
    "5822": "NAM - Nova América",
}


def resolve_une_code(user_input: str) -> str:
    """
    Resolve código de UNE a partir de input do usuário.

    Args:
        user_input: String do usuário (ex: "scr", "Une Mad", "Santa Cruz", "1")

    Returns:
        Código numérico da UNE (ex: "1") ou None se não encontrado

    Examples:
        >>> resolve_une_code("scr")
        "1"
        >>> resolve_une_code("Une Mad")
        "2720"
        >>> resolve_une_code("Santa Cruz")
        "1"
        >>> resolve_une_code("desconhecida")
        None
    """
    if not user_input:
        return None

    # Normalizar input
    normalized = user_input.lower().strip()

    # Remover prefixo "une" comum
    normalized = normalized.replace("une ", "").strip()

    # Verificar se já é um código numérico
    if normalized.isdigit() and normalized in UNE_NAMES:
        return normalized

    # Buscar no dicionário
    return UNE_MAP.get(normalized)


def get_une_name(code: str) -> str:
    """
    Retorna nome oficial da UNE dado seu código.

    Args:
        code: Código numérico da UNE (ex: "1")

    Returns:
        Nome oficial ou None se não encontrado

    Examples:
        >>> get_une_name("1")
        "SCR - Santa Cruz"
    """
    return UNE_NAMES.get(code)


def list_all_unes() -> list:
    """
    Retorna lista de todas as UNEs cadastradas.

    Returns:
        Lista de tuplas (código, nome)

    Example:
        >>> list_all_unes()
        [("1", "SCR - Santa Cruz"), ("3", "ALC - Alcântara"), ...]
    """
    return [(code, name) for code, name in UNE_NAMES.items()]


def suggest_une(user_input: str) -> list:
    """
    Sugere UNEs baseado em input parcial do usuário.

    Args:
        user_input: Input parcial (ex: "san", "ma")

    Returns:
        Lista de códigos de UNEs que fazem match

    Example:
        >>> suggest_une("san")
        [("1", "SCR - Santa Cruz"), ("5570", "STS - Santos")]
    """
    if not user_input:
        return []

    normalized = user_input.lower().strip()
    suggestions = []

    # Buscar em siglas e nomes
    for key, code in UNE_MAP.items():
        if normalized in key:
            name = UNE_NAMES.get(code)
            if (code, name) not in suggestions:
                suggestions.append((code, name))

    return suggestions


if __name__ == "__main__":
    # Testes
    import sys
    import io

    # Configurar encoding UTF-8 para output
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=== Teste de Mapeamento de UNEs (DADOS REAIS) ===\n")

    test_cases = [
        "scr",
        "Une Mad",
        "Santa Cruz",
        "1",
        "juiz de fora",
        "desconhecida",
        "une jfa",
        "cam",
        "campos"
    ]

    for test in test_cases:
        code = resolve_une_code(test)
        if code:
            name = get_une_name(code)
            print(f"OK '{test}' -> Codigo: {code}, Nome: {name}")
        else:
            suggestions = suggest_une(test)
            if suggestions:
                print(f"AVISO '{test}' nao encontrado. Sugestoes: {suggestions[:3]}")
            else:
                print(f"ERRO '{test}' nao encontrado")

    print(f"\nTotal de UNEs cadastradas: {len(UNE_NAMES)}")
    print("\nPrimeiras 10 UNEs:")
    for i, (code, name) in enumerate(list_all_unes()[:10]):
        print(f"  {code}: {name}")
