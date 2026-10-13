"""Alias de compatibilidad: la biblioteca se llama ahora HiBER y vive en ../hiber/hiber.py (con hiber_parameters.json).
Los scripts de análisis que hacen `import lepsp` reciben el módulo hiber completo, incluidos los nombres privados."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hiber"))
import hiber as _hiber  # noqa: E402
sys.modules[__name__] = _hiber
