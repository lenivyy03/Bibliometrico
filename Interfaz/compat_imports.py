from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Dict, List


_MODULE_CACHE: Dict[str, ModuleType] = {}

_FILE_CANDIDATES: Dict[str, List[str]] = {
    "carga": ["carga.py", "carga(2).py"],
    "conteo": ["conteo.py", "conteo(2).py"],
    "estadisticas_autoria": ["estadisticas_autoria.py", "estadisticas_autoria(2).py"],
    "filtrado": ["filtrado.py", "filtrado(2).py"],
    "impacto": ["impacto.py", "impacto(2).py"],
    "lista_paises": ["lista_paises.py", "lista_paises(2).py"],
    "tops": ["tops.py", "tops(2).py"],
    "exportacion": ["exportacion.py", "exportacion(2).py"],
}


def _candidate_dirs() -> List[Path]:
    here = Path(__file__).resolve().parent
    dirs = [here, here.parent, Path.cwd(), Path("/mnt/data")]
    seen = set()
    ordered: List[Path] = []
    for item in dirs:
        try:
            resolved = item.resolve()
        except FileNotFoundError:
            continue
        if resolved not in seen:
            seen.add(resolved)
            ordered.append(resolved)
    return ordered


def load_project_module(module_name: str) -> ModuleType:
    if module_name in _MODULE_CACHE:
        return _MODULE_CACHE[module_name]

    try:
        module = importlib.import_module(module_name)
        _MODULE_CACHE[module_name] = module
        return module
    except Exception:
        pass

    filenames = _FILE_CANDIDATES.get(module_name, [f"{module_name}.py"])
    for directory in _candidate_dirs():
        for filename in filenames:
            path = directory / filename
            if not path.exists():
                continue
            spec = importlib.util.spec_from_file_location(f"compat_{module_name}", path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"compat_{module_name}"] = module
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            _MODULE_CACHE[module_name] = module
            return module

    raise ImportError(f"No se pudo localizar el módulo '{module_name}'.")
