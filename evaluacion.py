"""Evaluacion estructural de un perfil seleccionado del catalogo."""

from dataclasses import dataclass

from catalogo import obtener_perfil_por_cromosoma
from modelo_estructural import (
    calcular_deflexion_admisible,
    calcular_deflexion_maxima,
    calcular_momento_maximo,
    calcular_tension_flexion,
    cumple_deflexion,
    cumple_resistencia,
    es_factible,
)


@dataclass(frozen=True)
class ResultadoEvaluacion:
    """Resultados estructurales de un perfil para una condicion de carga."""

    nombre_perfil: str
    cromosoma: str
    longitud_m: float
    longitud_mm: float
    carga_kn_m: float
    carga_n_mm: float
    masa_lineal_kg_m: float
    masa_total_kg: float
    momento_maximo_n_mm: float
    tension_maxima_mpa: float
    fy_mpa: float
    deflexion_maxima_mm: float
    deflexion_admisible_mm: float
    cumple_resistencia: bool
    cumple_deflexion: bool
    factible: bool


def _validar_numero_positivo(valor, nombre):
    """Valida una entrada numerica estrictamente positiva."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"{nombre} debe ser un valor numerico.")
    if valor <= 0:
        raise ValueError(f"{nombre} debe ser mayor que cero.")


def evaluar_perfil(L_m, w_kn_m, cromosoma):
    """Evalua estructuralmente el perfil identificado por un cromosoma.

    Args:
        L_m: Longitud de la viga en metros.
        w_kn_m: Carga distribuida uniforme en kN/m.
        cromosoma: Cadena binaria de tres bits.

    Returns:
        Un objeto ResultadoEvaluacion con los calculos y verificaciones.
    """
    _validar_numero_positivo(L_m, "L_m")
    _validar_numero_positivo(w_kn_m, "w_kn_m")

    perfil = obtener_perfil_por_cromosoma(cromosoma)

    longitud_mm = L_m * 1000
    carga_n_mm = w_kn_m
    inercia_mm4 = perfil.inercia_cm4 * 10000
    modulo_resistente_mm3 = perfil.modulo_resistente_cm3 * 1000

    momento_maximo = calcular_momento_maximo(carga_n_mm, longitud_mm)
    deflexion_maxima = calcular_deflexion_maxima(
        carga_n_mm,
        longitud_mm,
        perfil.E_mpa,
        inercia_mm4,
    )
    deflexion_admisible = calcular_deflexion_admisible(longitud_mm)
    tension_maxima = calcular_tension_flexion(
        momento_maximo,
        modulo_resistente_mm3,
    )
    resultado_resistencia = cumple_resistencia(tension_maxima, perfil.fy_mpa)
    resultado_deflexion = cumple_deflexion(
        deflexion_maxima,
        deflexion_admisible,
    )

    return ResultadoEvaluacion(
        nombre_perfil=perfil.nombre,
        cromosoma=perfil.cromosoma,
        longitud_m=L_m,
        longitud_mm=longitud_mm,
        carga_kn_m=w_kn_m,
        carga_n_mm=carga_n_mm,
        masa_lineal_kg_m=perfil.masa_lineal_kg_m,
        masa_total_kg=perfil.masa_lineal_kg_m * L_m,
        momento_maximo_n_mm=momento_maximo,
        tension_maxima_mpa=tension_maxima,
        fy_mpa=perfil.fy_mpa,
        deflexion_maxima_mm=deflexion_maxima,
        deflexion_admisible_mm=deflexion_admisible,
        cumple_resistencia=resultado_resistencia,
        cumple_deflexion=resultado_deflexion,
        factible=es_factible(resultado_resistencia, resultado_deflexion),
    )
