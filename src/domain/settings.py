from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class Tag:
    nombre: str
    estado: str = "activo"

    def to_dict(self) -> Dict[str, str]:
        return {"nombre": self.nombre, "estado": self.estado}

    @staticmethod
    def from_iterable(items: Iterable[str]) -> List["Tag"]:
        return [Tag(nombre=item) for item in items]


@dataclass
class AppSettings:
    """
    Contenedor tipado para la configuración de la aplicación. Mantiene compatibilidad
    con el acceso por clave de diccionario usado históricamente.
    """

    data: Dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def update(self, other: Dict[str, Any]):
        self.data.update(other)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppSettings":
        return cls(data=dict(data))
