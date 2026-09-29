"""Ecuaciones estructurales para una viga simplemente apoyada.

Las magnitudes recibidas por este modulo utilizan el sistema N-mm-MPa:
longitud en mm, carga en N/mm, momentos en N*mm, propiedades geometricas
en mm^3 o mm^4 y propiedades del material en N/mm^2.
"""


def _validar_numero_positivo(valor, nombre):
	"""Valida que un argumento sea un numero real estrictamente positivo."""
	if isinstance(valor, bool) or not isinstance(valor, (int, float)):
		raise TypeError(f"{nombre} debe ser un valor numerico.")
	if valor <= 0:
		raise ValueError(f"{nombre} debe ser mayor que cero.")


def _validar_numero_no_negativo(valor, nombre):
	"""Valida que un argumento sea un numero real no negativo."""
	if isinstance(valor, bool) or not isinstance(valor, (int, float)):
		raise TypeError(f"{nombre} debe ser un valor numerico.")
	if valor < 0:
		raise ValueError(f"{nombre} no puede ser negativo.")


def calcular_momento_maximo(w, L):
	"""Calcula el momento maximo en N*mm para una carga uniforme."""
	_validar_numero_positivo(w, "w")
	_validar_numero_positivo(L, "L")
	return w * L**2 / 8


def calcular_deflexion_maxima(w, L, E, I):
	"""Calcula la deflexion maxima en mm para una carga uniforme."""
	_validar_numero_positivo(w, "w")
	_validar_numero_positivo(L, "L")
	_validar_numero_positivo(E, "E")
	_validar_numero_positivo(I, "I")
	return 5 * w * L**4 / (384 * E * I)


def calcular_deflexion_admisible(L):
	"""Calcula la deflexion admisible mediante el criterio L/360."""
	_validar_numero_positivo(L, "L")
	return L / 360


def calcular_tension_flexion(Mmax, W):
	"""Calcula la tension maxima de flexion en MPa."""
	_validar_numero_no_negativo(Mmax, "Mmax")
	_validar_numero_positivo(W, "W")
	return Mmax / W


def cumple_resistencia(sigma_max, fy):
	"""Comprueba si la tension no supera el limite de fluencia."""
	_validar_numero_no_negativo(sigma_max, "sigma_max")
	_validar_numero_positivo(fy, "fy")
	return sigma_max <= fy


def cumple_deflexion(delta_max, delta_adm):
	"""Comprueba si la deflexion no supera el limite admisible."""
	_validar_numero_no_negativo(delta_max, "delta_max")
	_validar_numero_positivo(delta_adm, "delta_adm")
	return delta_max <= delta_adm


def es_factible(cumple_resistencia_resultado, cumple_deflexion_resultado):
	"""Comprueba si se cumplen simultaneamente ambas restricciones."""
	if not isinstance(cumple_resistencia_resultado, bool):
		raise TypeError("cumple_resistencia_resultado debe ser booleano.")
	if not isinstance(cumple_deflexion_resultado, bool):
		raise TypeError("cumple_deflexion_resultado debe ser booleano.")
	return cumple_resistencia_resultado and cumple_deflexion_resultado
