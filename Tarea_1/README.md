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