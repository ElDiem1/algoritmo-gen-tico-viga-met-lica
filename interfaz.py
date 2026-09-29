"""Interfaz grafica Tkinter para la optimizacion de la viga."""

import tkinter as tk
from tkinter import messagebox, ttk

from algoritmo_genetico import ejecutar_algoritmo_genetico


class InterfazAplicacion:
    """Construye y coordina la ventana principal."""

    def __init__(self, root):
        self.root = root
        self.root.title("Optimizacion de Viga Metalica mediante Algoritmo Genetico")
        self.root.geometry("960x760")
        self.root.minsize(820, 640)

        self.longitud_var = tk.StringVar()
        self.carga_var = tk.StringVar()
        self.estado_var = tk.StringVar(value="Ingrese los datos y ejecute la optimizacion.")
        self.parametros_vars = {
            "Poblacion": tk.StringVar(value="-"),
            "Generaciones": tk.StringVar(value="-"),
            "Seleccion": tk.StringVar(value="-"),
            "Crossover": tk.StringVar(value="-"),
            "Mutacion": tk.StringVar(value="-"),
            "Elitismo": tk.StringVar(value="-"),
        }
        self.resumen_vars = {
            "Generaciones realizadas": tk.StringVar(value="-"),
            "Individuos por generacion": tk.StringVar(value="-"),
            "Mejor solucion encontrada": tk.StringVar(value="-"),
            "Fitness final": tk.StringVar(value="-"),
        }
        self.resultado_vars = {
            "Perfil seleccionado": tk.StringVar(value="-"),
            "Cromosoma": tk.StringVar(value="-"),
            "Masa lineal": tk.StringVar(value="-"),
            "Masa total": tk.StringVar(value="-"),
            "Momento maximo": tk.StringVar(value="-"),
            "Tension maxima": tk.StringVar(value="-"),
            "fy": tk.StringVar(value="-"),
            "Deflexion maxima": tk.StringVar(value="-"),
            "Deflexion admisible": tk.StringVar(value="-"),
            "Cumple resistencia": tk.StringVar(value="-"),
            "Cumple deflexion": tk.StringVar(value="-"),
            "Factibilidad global": tk.StringVar(value="-"),
        }
        self.historial_tree = None
        self._configurar_estilo()
        self._crear_interfaz()

    def _configurar_estilo(self):
        estilo = ttk.Style(self.root)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 16, "bold"))
        estilo.configure("Resultado.TLabel", font=("Segoe UI", 11, "bold"))

    def _crear_interfaz(self):
        contenedor = ttk.Frame(self.root, padding=16)
        contenedor.pack(fill="both", expand=True)
        contenedor.columnconfigure(0, weight=1)

        ttk.Label(
            contenedor,
            text="Optimizacion de Viga Metalica mediante Algoritmo Genetico",
            style="Titulo.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 14))

        self._crear_entradas(contenedor).grid(
            row=1, column=0, sticky="ew", pady=(0, 10)
        )
        ttk.Label(contenedor, textvariable=self.estado_var).grid(
            row=2, column=0, sticky="nw", pady=(0, 8)
        )
        self._crear_parametros(contenedor).grid(
            row=3, column=0, sticky="ew", pady=(0, 10)
        )
        self._crear_historial(contenedor).grid(
            row=4, column=0, sticky="nsew", pady=(0, 10)
        )
        self._crear_resumen(contenedor).grid(
            row=5, column=0, sticky="ew", pady=(0, 10)
        )
        self._crear_resultados(contenedor).grid(
            row=6, column=0, sticky="nsew"
        )
        self._crear_atajos()

    def _crear_entradas(self, padre):
        marco = ttk.LabelFrame(padre, text="Datos de entrada", padding=10)
        ttk.Label(marco, text="Longitud de la viga (m):").grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        longitud = ttk.Entry(marco, textvariable=self.longitud_var, width=16)
        longitud.grid(row=0, column=1, padx=(0, 18))
        longitud.focus_set()

        ttk.Label(marco, text="Carga distribuida (kN/m):").grid(
            row=0, column=2, sticky="w", padx=(0, 8)
        )
        ttk.Entry(marco, textvariable=self.carga_var, width=16).grid(
            row=0, column=3, padx=(0, 18)
        )
        ttk.Button(
            marco,
            text="Ejecutar optimizacion",
            command=self.ejecutar_optimizacion,
        ).grid(row=0, column=4, padx=4)
        ttk.Button(marco, text="Limpiar", command=self.limpiar).grid(
            row=0, column=5, padx=4
        )
        return marco

    def _crear_parametros(self, padre):
        marco = ttk.LabelFrame(padre, text="Parametros del algoritmo genetico", padding=10)
        marco.columnconfigure(1, weight=1)
        for fila, (etiqueta, variable) in enumerate(self.parametros_vars.items()):
            ttk.Label(marco, text=f"{etiqueta}:").grid(
                row=fila, column=0, sticky="w", padx=(0, 12), pady=3
            )
            ttk.Label(marco, textvariable=variable).grid(
                row=fila, column=1, sticky="w", pady=3
            )
        return marco

    def _crear_historial(self, padre):
        marco = ttk.LabelFrame(padre, text="Evolucion del algoritmo genetico", padding=10)
        columnas = ("generacion", "cromosoma", "perfil", "fitness", "factible")
        self.historial_tree = ttk.Treeview(
            marco,
            columns=columnas,
            show="headings",
            height=10,
        )
        self.historial_tree.heading("generacion", text="Generacion")
        self.historial_tree.heading("cromosoma", text="Cromosoma")
        self.historial_tree.heading("perfil", text="Perfil")
        self.historial_tree.heading("fitness", text="Fitness")
        self.historial_tree.heading("factible", text="Factible")
        self.historial_tree.column("generacion", width=80, anchor="center")
        self.historial_tree.column("cromosoma", width=110, anchor="center")
        self.historial_tree.column("perfil", width=150)
        self.historial_tree.column("fitness", width=120, anchor="center")
        self.historial_tree.column("factible", width=90, anchor="center")

        barra_y = ttk.Scrollbar(marco, orient="vertical", command=self.historial_tree.yview)
        barra_x = ttk.Scrollbar(marco, orient="horizontal", command=self.historial_tree.xview)
        self.historial_tree.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)

        self.historial_tree.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)
        return marco

    def _crear_resumen(self, padre):
        marco = ttk.LabelFrame(padre, text="Mejor solucion", padding=10)
        marco.columnconfigure(1, weight=1)
        for fila, (etiqueta, variable) in enumerate(self.resumen_vars.items()):
            ttk.Label(marco, text=f"{etiqueta}:").grid(
                row=fila, column=0, sticky="w", padx=(0, 12), pady=3
            )
            ttk.Label(marco, textvariable=variable).grid(
                row=fila, column=1, sticky="w", pady=3
            )
        return marco

    def _crear_resultados(self, padre):
        marco = ttk.LabelFrame(padre, text="Resultado estructural", padding=12)
        marco.columnconfigure(1, weight=1)
        for fila, (etiqueta, variable) in enumerate(self.resultado_vars.items()):
            ttk.Label(marco, text=f"{etiqueta}:").grid(
                row=fila, column=0, sticky="w", padx=(0, 18), pady=3
            )
            ttk.Label(
                marco,
                textvariable=variable,
                style="Resultado.TLabel" if fila < 4 else "",
            ).grid(row=fila, column=1, sticky="w", pady=3)
        return marco

    def _actualizar_parametros(self, parametros):
        self.parametros_vars["Poblacion"].set(str(parametros.tamano_poblacion))
        self.parametros_vars["Generaciones"].set(str(parametros.max_generaciones))
        self.parametros_vars["Seleccion"].set("Ruleta")
        self.parametros_vars["Crossover"].set(str(parametros.probabilidad_crossover))
        self.parametros_vars["Mutacion"].set(str(parametros.probabilidad_mutacion))
        self.parametros_vars["Elitismo"].set(str(parametros.elitismo))

    def _actualizar_historial(self, historial):
        if self.historial_tree is None:
            return
        for fila in self.historial_tree.get_children():
            self.historial_tree.delete(fila)
        for entrada in historial:
            self.historial_tree.insert(
                "",
                "end",
                values=(
                    entrada.numero_generacion,
                    entrada.cromosoma,
                    entrada.nombre_perfil,
                    f"{entrada.fitness:.6f}",
                    "Si" if entrada.factible else "No",
                ),
            )

    def _actualizar_resumen(self, resultado):
        if resultado.mejor_individuo is None:
            self.resumen_vars["Generaciones realizadas"].set("-")
            self.resumen_vars["Individuos por generacion"].set("-")
            self.resumen_vars["Mejor solucion encontrada"].set("-")
            self.resumen_vars["Fitness final"].set("-")
            return

        self.resumen_vars["Generaciones realizadas"].set(str(resultado.generaciones_ejecutadas))
        self.resumen_vars["Individuos por generacion"].set(str(resultado.parametros.tamano_poblacion))
        self.resumen_vars["Mejor solucion encontrada"].set(
            resultado.mejor_individuo.evaluacion.nombre_perfil
            if resultado.mejor_individuo.evaluacion is not None
            else "Sin solucion factible"
        )
        self.resumen_vars["Fitness final"].set(f"{resultado.mejor_individuo.fitness:.6f}")

    def _crear_atajos(self):
        self.root.bind("<Return>", lambda _evento: self.ejecutar_optimizacion())
        self.root.bind("<Escape>", lambda _evento: self.limpiar())

    def _leer_entrada(self, texto, nombre):
        valor = texto.strip().replace(",", ".")
        if not valor:
            raise ValueError(f"Ingrese la {nombre}.")
        try:
            numero = float(valor)
        except ValueError as error:
            raise ValueError(f"La {nombre} debe ser numerica.") from error
        if numero <= 0:
            raise ValueError(f"La {nombre} debe ser mayor que cero.")
        return numero

    def ejecutar_optimizacion(self):
        try:
            longitud = self._leer_entrada(self.longitud_var.get(), "longitud")
            carga = self._leer_entrada(self.carga_var.get(), "carga distribuida")
            resultado = ejecutar_algoritmo_genetico(longitud, carga)
        except (TypeError, ValueError) as error:
            messagebox.showerror("Datos invalidos", str(error), parent=self.root)
            self.estado_var.set("Corrija los datos de entrada.")
            return

        self._actualizar_parametros(resultado.parametros)
        self._actualizar_historial(resultado.historial)

        evaluacion = resultado.mejor_solucion or resultado.mejor_individuo.evaluacion
        if resultado.mejor_solucion is None:
            self.estado_var.set(
                "NO EXISTE UNA SOLUCION FACTIBLE EN EL CATALOGO "
                "PARA LAS CONDICIONES INGRESADAS."
            )
            valores_principales = {
                "Perfil seleccionado": "Sin solucion factible",
                "Cromosoma": "-",
                "Masa lineal": "-",
                "Masa total": "-",
            }
        else:
            self.estado_var.set("Optimizacion ejecutada correctamente.")
            valores_principales = {
                "Perfil seleccionado": evaluacion.nombre_perfil,
                "Cromosoma": evaluacion.cromosoma,
                "Masa lineal": f"{evaluacion.masa_lineal_kg_m:.2f} kg/m",
                "Masa total": f"{evaluacion.masa_total_kg:.2f} kg",
            }

        valores_estructurales = {
            "Momento maximo": f"{evaluacion.momento_maximo_n_mm:,.2f} N*mm",
            "Tension maxima": f"{evaluacion.tension_maxima_mpa:.4f} MPa",
            "fy": f"{evaluacion.fy_mpa:.2f} MPa",
            "Deflexion maxima": f"{evaluacion.deflexion_maxima_mm:.4f} mm",
            "Deflexion admisible": f"{evaluacion.deflexion_admisible_mm:.4f} mm",
            "Cumple resistencia": "Si" if evaluacion.cumple_resistencia else "No",
            "Cumple deflexion": "Si" if evaluacion.cumple_deflexion else "No",
            "Factibilidad global": "Si" if evaluacion.factible else "No",
        }
        for etiqueta, valor in {**valores_principales, **valores_estructurales}.items():
            self.resultado_vars[etiqueta].set(valor)

        self._actualizar_resumen(resultado)

    def limpiar(self):
        self.longitud_var.set("")
        self.carga_var.set("")
        self.estado_var.set("Ingrese los datos y ejecute la optimizacion.")
        for variable in self.parametros_vars.values():
            variable.set("-")
        for variable in self.resultado_vars.values():
            variable.set("-")
        for variable in self.resumen_vars.values():
            variable.set("-")
        if self.historial_tree is not None:
            for fila in self.historial_tree.get_children():
                self.historial_tree.delete(fila)


def crear_aplicacion():
    """Crea y devuelve la ventana principal."""
    root = tk.Tk()
    InterfazAplicacion(root)
    return root
