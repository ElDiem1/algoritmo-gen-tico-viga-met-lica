"""Algoritmo genetico binario para seleccionar perfiles estructurales."""

from dataclasses import dataclass
import random

from catalogo import obtener_catalogo
from evaluacion import ResultadoEvaluacion, evaluar_perfil


@dataclass(frozen=True)
class IndividuoEvaluado:
    """Cromosoma junto con su evaluacion estructural y aptitud."""

    cromosoma: str
    evaluacion: ResultadoEvaluacion
    fitness: float
    violacion: float


@dataclass(frozen=True)
class RegistroGeneracion:
    """Resumen del mejor individuo de una generacion."""

    numero_generacion: int
    cromosoma: str
    nombre_perfil: str
    fitness: float
    masa_total_kg: float
    factible: bool
    tension_maxima_mpa: float
    deflexion_maxima_mm: float
    deflexion_admisible_mm: float


@dataclass(frozen=True)
class ParametrosAlgoritmoGenetico:
    """Parametros utilizados durante una ejecucion del algoritmo."""

    tamano_poblacion: int
    probabilidad_crossover: float
    probabilidad_mutacion: float
    max_generaciones: int
    elitismo: int
    seed: int | None


@dataclass(frozen=True)
class ResultadoAlgoritmoGenetico:
    """Resultado completo de una ejecucion del algoritmo genetico."""

    mejor_individuo: IndividuoEvaluado
    mejor_solucion: ResultadoEvaluacion | None
    historial: tuple
    parametros: ParametrosAlgoritmoGenetico
    generaciones_ejecutadas: int


def _validar_cromosoma(cromosoma):
    """Valida una cadena binaria de cinco bits."""
    if not isinstance(cromosoma, str):
        raise TypeError("El cromosoma debe ser una cadena de texto.")
    if len(cromosoma) != 5:
        raise ValueError("El cromosoma debe tener exactamente 5 bits.")
    if any(bit not in "01" for bit in cromosoma):
        raise ValueError("El cromosoma solo puede contener 0 y 1.")


def reparar_cromosoma(cromosoma):
    """Repara un cromosoma invalido transformandolo en uno valido del catalogo."""
    _validar_cromosoma(cromosoma)
    indice = int(cromosoma, 2)
    perfil_valido = indice % len(obtener_catalogo())
    return format(perfil_valido, "05b")


def _validar_numero_positivo(valor, nombre):
    """Valida un numero estrictamente positivo."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"{nombre} debe ser un valor numerico.")
    if valor <= 0:
        raise ValueError(f"{nombre} debe ser mayor que cero.")


def _validar_probabilidad(valor, nombre):
    """Valida una probabilidad dentro del intervalo [0, 1]."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"{nombre} debe ser un valor numerico.")
    if valor < 0 or valor > 1:
        raise ValueError(f"{nombre} debe estar entre 0 y 1.")


def crear_poblacion_inicial(tamano_poblacion=6, rng=None):
    """Crea una poblacion aleatoria de cromosomas validos de cinco bits."""
    _validar_numero_positivo(tamano_poblacion, "tamano_poblacion")
    if not isinstance(tamano_poblacion, int):
        raise TypeError("tamano_poblacion debe ser un numero entero.")
    generador = rng if rng is not None else random.Random()
    cromosomas_validos = [perfil.cromosoma for perfil in obtener_catalogo()]
    return [generador.choice(cromosomas_validos) for _ in range(tamano_poblacion)]


def calcular_violacion(resultado):
    """Calcula la mayor violacion relativa de las restricciones."""
    violacion_resistencia = max(
        0.0,
        resultado.tension_maxima_mpa / resultado.fy_mpa - 1,
    )
    violacion_deflexion = max(
        0.0,
        resultado.deflexion_maxima_mm / resultado.deflexion_admisible_mm - 1,
    )
    return max(violacion_resistencia, violacion_deflexion)


def calcular_fitness(resultado, masa_total_maxima):
    """Calcula la aptitud normalizada segun factibilidad y masa.

    Las soluciones factibles reciben una aptitud entre 1 y 2
    aproximadamente. Las no factibles reciben 1/(1 + violacion),
    donde violacion es la mayor violacion relativa de las restricciones.
    """
    _validar_numero_positivo(masa_total_maxima, "masa_total_maxima")

    if resultado.factible:
        masa_normalizada = resultado.masa_total_kg / masa_total_maxima
        return 1 + (1 - masa_normalizada)

    return 1 / (1 + calcular_violacion(resultado))


def _masa_total_maxima(L_m):
    """Obtiene la masa total del perfil mas pesado del catalogo."""
    return max(
        perfil.masa_lineal_kg_m * L_m
        for perfil in obtener_catalogo()
    )


def evaluar_poblacion(poblacion, L_m, w_kn_m, masa_total_maxima=None):
    """Evalua todos los cromosomas de una poblacion."""
    if not poblacion:
        raise ValueError("La poblacion no puede estar vacia.")

    masa_maxima = (
        masa_total_maxima
        if masa_total_maxima is not None
        else _masa_total_maxima(L_m)
    )
    _validar_numero_positivo(masa_maxima, "masa_total_maxima")

    individuos = []
    for cromosoma in poblacion:
        cromosoma_validado = reparar_cromosoma(cromosoma)
        resultado = evaluar_perfil(L_m, w_kn_m, cromosoma_validado)
        violacion = calcular_violacion(resultado)
        fitness = calcular_fitness(resultado, masa_maxima)
        individuos.append(
            IndividuoEvaluado(cromosoma_validado, resultado, fitness, violacion)
        )
    return individuos


def seleccionar_ruleta(individuos, cantidad, rng=None):
    """Selecciona cromosomas con probabilidad proporcional al fitness."""
    if not individuos:
        raise ValueError("Se necesita al menos un individuo para seleccionar.")
    _validar_numero_positivo(cantidad, "cantidad")
    if not isinstance(cantidad, int):
        raise TypeError("cantidad debe ser un numero entero.")

    generador = rng if rng is not None else random.Random()
    suma_fitness = sum(individuo.fitness for individuo in individuos)
    if suma_fitness <= 0:
        raise ValueError("La suma de fitness debe ser positiva.")

    seleccionados = []
    for _ in range(cantidad):
        objetivo = generador.random() * suma_fitness
        acumulado = 0.0
        for individuo in individuos:
            acumulado += individuo.fitness
            if acumulado >= objetivo:
                seleccionados.append(individuo.cromosoma)
                break
    return seleccionados


def crossover_un_punto(cromosoma_1, cromosoma_2, probabilidad=0.86, rng=None):
    """Aplica crossover de un punto y devuelve dos cromosomas hijos."""
    _validar_cromosoma(cromosoma_1)
    _validar_cromosoma(cromosoma_2)
    _validar_probabilidad(probabilidad, "probabilidad")
    generador = rng if rng is not None else random.Random()

    if generador.random() >= probabilidad:
        return cromosoma_1, cromosoma_2

    punto_corte = generador.randint(1, 4)
    hijo_1 = cromosoma_1[:punto_corte] + cromosoma_2[punto_corte:]
    hijo_2 = cromosoma_2[:punto_corte] + cromosoma_1[punto_corte:]
    return reparar_cromosoma(hijo_1), reparar_cromosoma(hijo_2)


def mutar_cromosoma(cromosoma, probabilidad=0.10, rng=None):
    """Muta cada bit de un cromosoma con la probabilidad indicada."""
    _validar_cromosoma(cromosoma)
    _validar_probabilidad(probabilidad, "probabilidad")
    generador = rng if rng is not None else random.Random()

    bits_mutados = []
    for bit in cromosoma:
        if generador.random() < probabilidad:
            bits_mutados.append("1" if bit == "0" else "0")
        else:
            bits_mutados.append(bit)
    return reparar_cromosoma("".join(bits_mutados))


def _clave_mejor_individuo(individuo):
    """Construye el orden de prioridad del mejor individuo."""
    if individuo.evaluacion.factible:
        return (1, 0.0, -individuo.evaluacion.masa_total_kg)
    return (0, -individuo.violacion, -individuo.evaluacion.masa_total_kg)


def _mejor_individuo(individuos):
    """Devuelve el individuo con mayor prioridad de seleccion."""
    return max(individuos, key=_clave_mejor_individuo)


def _registrar_generacion(numero, individuo):
    """Convierte el mejor individuo en una entrada de historial."""
    resultado = individuo.evaluacion
    return RegistroGeneracion(
        numero_generacion=numero,
        cromosoma=individuo.cromosoma,
        nombre_perfil=resultado.nombre_perfil,
        fitness=individuo.fitness,
        masa_total_kg=resultado.masa_total_kg,
        factible=resultado.factible,
        tension_maxima_mpa=resultado.tension_maxima_mpa,
        deflexion_maxima_mm=resultado.deflexion_maxima_mm,
        deflexion_admisible_mm=resultado.deflexion_admisible_mm,
    )


def ejecutar_algoritmo_genetico(
    L_m,
    w_kn_m,
    tamano_poblacion=6,
    probabilidad_crossover=0.86,
    probabilidad_mutacion=0.10,
    max_generaciones=30,
    seed=None,
):
    """Ejecuta el algoritmo genetico y devuelve su historial completo."""
    _validar_numero_positivo(L_m, "L_m")
    _validar_numero_positivo(w_kn_m, "w_kn_m")
    _validar_numero_positivo(tamano_poblacion, "tamano_poblacion")
    _validar_numero_positivo(max_generaciones, "max_generaciones")
    if not isinstance(tamano_poblacion, int):
        raise TypeError("tamano_poblacion debe ser un numero entero.")
    if not isinstance(max_generaciones, int):
        raise TypeError("max_generaciones debe ser un numero entero.")
    _validar_probabilidad(probabilidad_crossover, "probabilidad_crossover")
    _validar_probabilidad(probabilidad_mutacion, "probabilidad_mutacion")

    generador = random.Random(seed)
    masa_maxima = _masa_total_maxima(L_m)
    poblacion = crear_poblacion_inicial(tamano_poblacion, generador)
    evaluados = evaluar_poblacion(
        poblacion,
        L_m,
        w_kn_m,
        masa_maxima,
    )

    historial = [_registrar_generacion(0, _mejor_individuo(evaluados))]
    mejor_global = _mejor_individuo(evaluados)

    for numero_generacion in range(1, max_generaciones + 1):
        elite = _mejor_individuo(evaluados).cromosoma
        padres = seleccionar_ruleta(
            evaluados,
            tamano_poblacion,
            generador,
        )
        nueva_poblacion = [reparar_cromosoma(elite)]

        for posicion in range(0, tamano_poblacion - 1, 2):
            padre_1 = reparar_cromosoma(padres[posicion])
            padre_2 = reparar_cromosoma(padres[(posicion + 1) % len(padres)])
            hijo_1, hijo_2 = crossover_un_punto(
                padre_1,
                padre_2,
                probabilidad_crossover,
                generador,
            )
            nueva_poblacion.append(
                mutar_cromosoma(hijo_1, probabilidad_mutacion, generador)
            )
            if len(nueva_poblacion) < tamano_poblacion:
                nueva_poblacion.append(
                    mutar_cromosoma(
                        hijo_2,
                        probabilidad_mutacion,
                        generador,
                    )
                )

        evaluados = evaluar_poblacion(
            nueva_poblacion,
            L_m,
            w_kn_m,
            masa_maxima,
        )
        mejor_generacion = _mejor_individuo(evaluados)
        mejor_global = max(
            (mejor_global, mejor_generacion),
            key=_clave_mejor_individuo,
        )
        historial.append(
            _registrar_generacion(numero_generacion, mejor_generacion)
        )

    mejor_solucion = (
        mejor_global.evaluacion
        if mejor_global.evaluacion.factible
        else None
    )
    parametros = ParametrosAlgoritmoGenetico(
        tamano_poblacion=tamano_poblacion,
        probabilidad_crossover=probabilidad_crossover,
        probabilidad_mutacion=probabilidad_mutacion,
        max_generaciones=max_generaciones,
        elitismo=1,
        seed=seed,
    )
    return ResultadoAlgoritmoGenetico(
        mejor_individuo=mejor_global,
        mejor_solucion=mejor_solucion,
        historial=tuple(historial),
        parametros=parametros,
        generaciones_ejecutadas=max_generaciones,
    )
