from __future__ import annotations
from pathlib import Path
from typing import Dict, Type, Tuple
import yaml

_PY_TYPES: Dict[str, Type] = {
    "float": float,
    "int":   int,
    "str":   str,
    "bool":  bool,
}

class ContractSchema:
    """
    Хранит описание разделов inputs и targets из yaml-файла.
    """

    def __init__(self, yaml_path: str | "os.PathLike[str]") -> None:
        self.path = Path(yaml_path)
        self._inputs, self._targets = self._load()

    @property
    def inputs(self) -> Dict[str, Type]:
        return self._inputs

    @property
    def targets(self) -> Dict[str, Type]:
        return self._targets

    def _load(self) -> Tuple[Dict[str, Type], Dict[str, Type]]:
        with self.path.open(encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        if not {"inputs", "targets"} <= raw.keys():
            raise KeyError(
                "YAML must contain 'inputs' and 'targets' sections")

        return self._convert(raw["inputs"]), self._convert(raw["targets"])

    @staticmethod
    def _convert(raw_map: Dict[str, str]) -> Dict[str, Type]:
        unknown = set(raw_map.values()) - _PY_TYPES.keys()
        if unknown:
            raise ValueError(f"Unknown types in YAML: {unknown}")
        return {k: _PY_TYPES[v] for k, v in raw_map.items()}
