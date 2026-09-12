# IEE2714 Fundamentos de Procesamiento de Imágenes — Tarea 1 (2° Semestre 2026)

- **Estudiante:** Christian Vásquez Villegas  
- **Profesor:** Carlos Milovic
- **Fecha de Entrega:** Viernes 11 de septiembre de 2026

---

## Descripción del Proyecto

Este repositorio contiene el código, experimentos, notebooks e informe de la **Tarea 1** del curso IEE2714 (Pontificia Universidad Católica de Chile). 

El trabajo aborda la implementación desde cero (sin librerías de alto nivel para los algoritmos centrales) de cuatro problemáticas fundamentales en procesamiento de imágenes:

1. **Pregunta 1:** Saturación selectiva de color dependiente del tono en espacios HS y CIE $L^*C^*h^*$.
2. **Pregunta 2:** Ecualización local de histograma basada en mallas paramétricas con interpolación y control propio de contraste (comparado con CLAHE).
3. **Pregunta 3:** Reescalado geométrico arbitrario e interpolación espacial (Vecino Más Cercano y Bilineal).
4. **Bonus:** Reconstrucción de imágenes desde mosaicos Bayer RGGB (Super-Pixel y Debayerizado Bilineal).

---

## Estructura del Repositorio

El repositorio está organizado en módulos reutilizables y cuadernos de análisis:

```text
├── README.md                      # Documentación del proyecto e instrucciones
├── requirements.txt               # Dependencias del entorno virtual
├── .gitignore                     # Archivos y carpetas ignoradas por Git
│
├── codigo/                        # Código fuente
│   ├── __init__.py
│   ├── p1_saturacion.py           # Funciones de saturación selectiva y g_m
│   ├── p2_ecualizacion.py         # Malla local, CDFs, interpolación y control de contraste
│   ├── p3_reescalado.py           # Backward mapping, vecinos más cercanos y bilineal
│   ├── bonus_bayer.py             # Máscara RGGB, Super-Pixel y debayerizado bilineal
│   └── utilidades.py              # I/O, métricas y graficado comparativo
│
├── cuadernos/                     # Jupyter Notebooks por pregunta
│   ├── 01_saturacion_color.ipynb
│   ├── 02_ecualizacion_local.ipynb
│   ├── 03_reescalado_interpolacion.ipynb
│   └── 04_bonus_debayerizado.ipynb
│
├── datos/                         # Imágenes de entrada para pruebas
│   ├── originales/                # Imágenes de prueba utilizadas
│   └── muestras/                  # Recortes o sintéticos
│
├── figuras/                       # Figuras generadas para el informe
│   ├── p1/
│   ├── p2/
│   ├── p3/
│   └── bonus/
│
└── informe/
    ├── informe_tarea1.pdf         # Informe final entregable
    └── informe_tarea1.md         # Código base del informe
```



### Trazabilidad de Funciones y Cuadernos
Para facilitar la revisión del código en instancias de evaluación individual, la siguiente tabla detalla la ubicación exacta de cada etapa algorítmica:

#### Tabla 0.1: Ubicación de Algoritmos y Cuadernos en el Repositorio

| Pregunta / Algoritmo | Módulo / Función | Cuaderno de Reproducción | Parámetros Principales | Descripción del Algoritmo |
| :--- | :--- | :--- | :--- | :--- |
| **P1.1 Continuidad Periódica** | `codigo/p1_saturacion.py` $\to$ `interpolar_m_periodico()` | `cuadernos/01_saturacion_color.ipynb` | `puntos_control` | Agrega nodos virtuales en $-360^\circ$ y $+360^\circ$. |
| **P1.2 Función de Sat.** | `codigo/p1_saturacion.py` $\to$ `funcion_g_m()` | `cuadernos/01_saturacion_color.ipynb` | `S`, `m`, `metodo` | Evalúa $g_m(S)$ lineal o por potencia ($S^{2^{-m}}$). |
| **P1.3 Gamut Clipping** | `codigo/p1_saturacion.py` $\to$ `ColorSaturation()` | `cuadernos/01_saturacion_color.ipynb` | `img`, `puntos_control`, `modo` | Trunca $C^* \ge 0$ y realiza clipping $[0, 1]$ en sRGB. |
| **P2.1 Ecualización Global** | `codigo/p2_ecualizacion.py` $\to$ `ecualizacion_local_malla()` | `cuadernos/02_ecualizacion_local.ipynb` | `n_regiones_y=1`, `n_regiones_x=1` | Malla $1 \times 1$ idéntica a ecualización global. |
| **P2.2 Mezcla Convexa** | `codigo/p2_ecualizacion.py` $\to$ `ecualizacion_local_malla()` | `cuadernos/02_ecualizacion_local.ipynb` | `alpha` | Aplica combinación $g = \alpha T_{\text{local}} + (1-\alpha)f$. |
| **P2.3 Interp. Espacial CDF**| `codigo/p2_ecualizacion.py` $\to$ `ecualizacion_local_malla()` | `cuadernos/02_ecualizacion_local.ipynb` | `n_regiones_y`, `n_regiones_x` | Interpola bilinealmente las CDFs de los 4 centros adyacentes. |
| **P3.1 Backward Mapping** | `codigo/p3_reescalado.py` $\to$ `reescalar_imagen()` | `cuadernos/03_reescalado_interpolacion.ipynb` | `s`, `metodo` | Mapeo inverso con desfase $+0.5/s - 0.5$. |
| **P3.2 Pesos Bilineales** | `codigo/p3_reescalado.py` $\to$ `reescalar_imagen()` | `cuadernos/03_reescalado_interpolacion.ipynb` | `dy`, `dx` | Calcula $w_{11}, w_{12}, w_{21}, w_{22}$ con $\sum w = 1$. |
| **P4.1 Debayerizado Bilineal**| `codigo/bonus_bayer.py` $\to$ `debayer_bilinear()` | `cuadernos/04_bonus_debayerizado.ipynb` | `bayer` | Interpola $G$ en $R/B$, $R$ en $G/B$ y $B$ en $G/R$ según paridad. |
| **P4.4 Diferencias de Color** | `codigo/bonus_bayer.py` $\to$ `debayer_freeman_diff()` | `cuadernos/04_bonus_debayerizado.ipynb` | `bayer` | Interpola $D_{RG} = R-G$ y $D_{BG} = B-G$ (Freeman). |

---