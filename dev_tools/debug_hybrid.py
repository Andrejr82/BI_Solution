import sys
from pathlib import Path

# Garantir que o diretório raiz do projeto esteja no sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.connectivity.hybrid_adapter import HybridDataAdapter
from pprint import pprint
import json


def main():
    a = HybridDataAdapter()
    print('Status:', a.get_status())
    r = a.execute_query({'une': 3})
    print('Type:', type(r))
    print('Sample:')
    if isinstance(r, list) and r:
        try:
            print(json.dumps(r[:3], default=str, indent=2))
        except Exception:
            pprint(r[:3])
    else:
        print(r)

if __name__ == '__main__':
    main()
