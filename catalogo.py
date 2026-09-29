"""Catalogo interno de perfiles IPE para el proyecto academico.

Las propiedades geometricas se almacenan en sus unidades originales:
area en cm^2, masa lineal en kg/m, inercia en cm^4 y modulo resistente
en cm^3. Las propiedades del material E y fy se almacenan en MPa.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Perfil:
    """Representa un perfil del catalogo y sus propiedades de trabajo."""

    nombre: str
    indice: int
    cromosoma: str
    area_cm2: float
    masa_lineal_kg_m: float
    inercia_cm4: float
    modulo_resistente_cm3: float
    material: str
    E_mpa: float
    fy_mpa: float


CATALOGO = [
    Perfil("IPE 80", 0, "00000", 7.6, 6.0, 80.1, 20.0, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 100", 1, "00001", 10.3, 8.1, 171, 34.2, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 120", 2, "00010", 13.2, 10.4, 318, 53.0, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 140", 3, "00011", 16.4, 12.9, 541, 77.3, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 160", 4, "00100", 20.1, 15.8, 869, 109, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 180", 5, "00101", 23.9, 18.8, 1317, 146, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 200", 6, "00110", 28.5, 22.4, 1943, 194, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 220", 7, "00111", 33.4, 26.2, 2772, 252, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 240", 8, "01000", 39.1, 30.7, 3892, 324, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 270", 9, "01001", 45.9, 36.1, 5790, 429, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 300", 10, "01010", 53.8, 42.2, 8356, 557, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 330", 11, "01011", 62.6, 49.1, 11770, 713, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 360", 12, "01100", 72.7, 57.1, 16270, 904, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 400", 13, "01101", 84.5, 66.3, 23130, 1160, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 450", 14, "01110", 98.8, 77.6, 33740, 1500, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 500", 15, "01111", 115.5, 90.7, 48200, 1930, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 550", 16, "10000", 134.4, 106.0, 67120, 2440, "ASTM A572 Grado 50", 200000, 345),
    Perfil("IPE 600", 17, "10001", 156.0, 122.0, 92080, 3070, "ASTM A572 Grado 50", 200000, 345),
]


def _validar_cromosoma(cromosoma):
    """Valida que el cromosoma tenga exactamente 5 bits binarios."""
    if not isinstance(cromosoma, str):
        raise TypeError("El cromosoma debe ser una cadena de texto.")
    if len(cromosoma) != 5:
        raise ValueError("El cromosoma debe tener exactamente 5 bits.")
    if any(bit not in "01" for bit in cromosoma):
        raise ValueError("El cromosoma solo puede contener 0 y 1.")


def obtener_perfil_por_cromosoma(cromosoma):
    """Devuelve el perfil asociado con un cromosoma binario de 5 bits."""
    _validar_cromosoma(cromosoma)
    indice = int(cromosoma, 2)
    if indice >= len(CATALOGO):
        raise ValueError("El cromosoma no corresponde a un perfil valido del catalogo.")
    return CATALOGO[indice]


def obtener_catalogo():
    """Devuelve una copia de la lista completa de perfiles."""
    return CATALOGO.copy()
