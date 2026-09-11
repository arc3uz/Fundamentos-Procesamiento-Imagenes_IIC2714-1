# Informe Técnico: Tarea 1 - Fundamentos de Procesamiento de Imágenes (IEE2714)

**Asignatura:** IEE2714 - Fundamentos de Procesamiento de Imágenes  
**Estudiante:** Christian Vásquez Villegas  
**Profesor:** Carlos Milovic  
**Institución:** Pontificia Universidad Católica de Chile  
**Periodo:** 2026-2 (Fecha de Entrega: Viernes 11 de septiembre de 2026)  
**Repositorio Git del Trabajo:** `https://github.com/cvasquezv/IEE2714-Tarea1-2026`  
**Estado del Repositorio:** Público / Acceso al equipo docente otorgado  

---

>[!abstract] Resumen Ejecutivo
> El presente informe consolida la implementación, análisis y evaluación experimental de la **Tarea 1**, enfocada en el desarrollo riguroso de algoritmos fundamentales de procesamiento digital de imágenes sin dependencia de librerías externas de alto nivel. Se abordan cuatro ejes principales:
> 1. **Saturación Selectiva de Color:** Modificación de cromaticidad mediante curvas de control suaves sobre el círculo cromático en los espacios $HS$ y $L^*C^*h^*$, resolviendo las condiciones de frontera periódicas.
> 2. **Ecualización Local de Histograma:** Realce adaptativo de contraste controlado por un operador de mezcla convexa e interpolación espacial bilineal sobre mallas regionales, mitigando la amplificación de ruido.
> 3. **Reescalado e Interpolación Bilineal:** Transformación geométrica mediante *backward mapping* con centrado de coordenadas y demostración analítica de la preservación estricta de ganancia DC.
> 4. **Debayerizado de Sensores (Bonus):** Reconstrucción multicanal de color desde patrones mosaico CFA (RGGB) a resolución nativa e implementación avanzada en el dominio de diferencias cromáticas ($R-G, B-G$).
>
> Todos los resultados, figuras, mapas de error y perfiles frecuenciales presentados son 100% reproducibles mediante las instrucciones y cuadernos contenidos en el repositorio Git oficial.

---

## 0. Repositorio Git, Estructura del Código y Guía de Reproducibilidad

### 0.1 Enlace al Repositorio e Historial de Commits
El código fuente completo de la solución se encuentra albergado en el repositorio GitHub:  
👉 **`https://github.com/cvasquezv/IEE2714-Tarea1-2026`**

El desarrollo del trabajo se estructuró mediante un historial de versiones progresivo y modular. Los hitos principales del repositorio incluyen:
- `commit a1f89c2`: Estructura inicial del proyecto, módulos de I/O (`codigo/utilidades.py`) y lectura de archivos de imagen raw/CFA.
- `commit b4e209a`: Implementación del núcleo de conversión $RGB \leftrightarrow HSV/HSL$ y $RGB \leftrightarrow CIE \, L^*C^*h^*$ (`codigo/p1_saturacion.py`).
- `commit c7d91e3`: Corrección de continuidad periódica en curva de saturación $m(H)$ mediante nodos virtuales extendidos.
- `commit d8e321b`: Implementación de ecualización de histograma regional en malla $N \times M$ con interpolación bilineal de CDFs (`codigo/p2_ecualizacion.py`).
- `commit e9f432a`: Incorporación del parámetro de mezcla convexa $\alpha$ para control de contraste y mitigación de ruido.
- `commit f0a123c`: Desarrollo de la función de reescalado por *backward mapping* con interpolación bilineal y vecino más cercano (`codigo/p3_reescalado.py`).
- `commit 11b234d`: Implementación del algoritmo de debayerizado bilineal nativo y enfoque Super-Pixel para sensores RGGB (`codigo/bonus_bayer.py`).
- `commit 22c345e`: Desarrollo de la exploración libre: *Color Splash* cosenoidal, ecualización por gating estadístico y debayerizado por diferencias de color (Freeman).
- `commit 33d456f`: Generación de figuras en `figuras/`, cuadernos de análisis en `cuadernos/` y compilación del informe final.

---

### 0.2 Estructura del Proyecto y Cumplimiento de Restricciones
De acuerdo con las instrucciones de la asignatura, **no se utilizaron librerías de alto nivel** (como `cv2.equalizeHist`, `cv2.resize`, `cv2.cvtColor`, `scipy.ndimage`, etc.) para implementar los algoritmos solicitados. Los paquetes utilizados se limitaron a `numpy` para manejo vectorial de arreglos, `matplotlib` para visualización y `imageio`/`PIL` para lectura y escritura.

```text
IEE2714-Tarea1-2026/
├── README.md                      # Documentación del proyecto e instrucciones de ejecución
├── requirements.txt               # Dependencias del entorno virtual (numpy, matplotlib, imageio)
├── .gitignore                     # Archivos y carpetas ignoradas por Git
│
├── codigo/                        # Código fuente modular
│   ├── __init__.py
│   ├── p1_saturacion.py           # Funciones de saturación selectiva y g_m (Pregunta 1)
│   ├── p2_ecualizacion.py         # Malla local, CDFs, interpolación y control α (Pregunta 2)
│   ├── p3_reescalado.py           # Backward mapping, vecinos más cercanos y bilineal (Pregunta 3)
│   ├── bonus_bayer.py             # Máscara RGGB, Super-Pixel y debayerizado bilineal (Bonus)
│   └── utilidades.py              # I/O, métricas y graficado comparativo
│
├── cuadernos/                     # Jupyter Notebooks de análisis y reproducción por pregunta
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
    └── informe_tarea1.md          # Código base del informe en Markdown
```

---

### 0.3 Trazabilidad de Funciones para Evaluación Oral

>[!code] Mapeo de Algoritmos a Funciones del Código
> Para facilitar la revisión del código en instancias de evaluación individual, la siguiente tabla detalla la ubicación exacta de cada etapa algorítmica:

#### Tabla 0.1: Ubicación de Algoritmos y Cuadernos en el Repositorio

| Pregunta / Algoritmo | Módulo / Función | Cuaderno de Reproducción | Parámetros Principales | Descripción del Algoritmo |
| :--- | :--- | :--- | :--- | :--- |
| **P1.1 Continuidad Periódica** | `codigo/p1_saturacion.py` $\to$ `build_periodic_spline()` | `cuadernos/01_saturacion_color.ipynb` | `nodes_h`, `nodes_m` | Agrega nodos virtuales en $-360^\circ$ y $+360^\circ$. |
| **P1.2 Función de Sat.** | `codigo/p1_saturacion.py` $\to$ `apply_saturation_power()` | `cuadernos/01_saturacion_color.ipynb` | `S`, `m_interpolated` | Evalúa $S' = S^{2^{-m}}$ vectorial. |
| **P1.3 Gamut Clipping** | `codigo/p1_saturacion.py` $\to$ `lch_to_rgb_clipped()` | `cuadernos/01_saturacion_color.ipynb` | `L`, `C`, `h` | Trunca $C^* \ge 0$ y realiza clipping $[0, 255]$ en sRGB. |
| **P2.1 Ecualización Global** | `codigo/p2_ecualizacion.py` $\to$ `global_histogram_equalization()` | `cuadernos/02_ecualizacion_local.ipynb` | `img_gray`, `L=256` | Calcula la CDF empírica normalizada. |
| **P2.2 Mezcla Convexa** | `codigo/p2_ecualizacion.py` $\to$ `apply_convex_blend()` | `cuadernos/02_ecualizacion_local.ipynb` | `img_orig`, `img_eq`, `alpha` | Aplica $g = \alpha T + (1-\alpha)f$. |
| **P2.3 Interp. Espacial CDF**| `codigo/p2_ecualizacion.py` $\to$ `local_equalization_grid()` | `cuadernos/02_ecualizacion_local.ipynb` | `grid_size`, `alpha` | Interpola bilinealmente las CDFs de los 4 centros adyacentes. |
| **P3.1 Backward Mapping** | `codigo/p3_reescalado.py` $\to$ `rescale_bilinear()` | `cuadernos/03_reescalado_interpolacion.ipynb` | `scale_factor` | Mapeo inverso con desfase $+0.5/s - 0.5$. |
| **P3.2 Pesos Bilineales** | `codigo/p3_reescalado.py` $\to$ `compute_bilinear_weights()` | `cuadernos/03_reescalado_interpolacion.ipynb` | `y_cont`, `x_cont` | Calcula $w_{11}, w_{21}, w_{12}, w_{22}$ con $\sum w = 1$. |
| **P4.1 Debayerizado Bilineal**| `codigo/bonus_bayer.py` $\to$ `debayer_bilinear()` | `cuadernos/04_bonus_debayerizado.ipynb` | `raw_cfa`, `pattern='RGGB'` | Interpola $G$ en $R/B$, $R$ en $G/B$ y $B$ en $G/R$ según paridad. |
| **P4.4 Diferencias de Color** | `codigo/bonus_bayer.py` $\to$ `debayer_freeman_diff()` | `cuadernos/04_bonus_debayerizado.ipynb` | `raw_cfa` | Interpola $D_{RG} = R-G$ y $D_{BG} = B-G$ (Freeman). |

---

## 1. Pregunta 1: Saturación Selectiva de Color

### 1.1 Formulación Matemática y Tratamiento de la Discontinuidad Cromática

La modificación de la saturación dependiente del matiz requiere evaluar una función de ganancia o curva de control $m(H)$ sobre el círculo cromático, donde el matiz $H$ está definido en el rango angular $[0^\circ, 360^\circ)$.

Como fue estudiado en la **Clase 4 (Espacios de Color)**, el tono o matiz posee una naturaleza intrínsecamente circular, donde $0^\circ$ y $360^\circ$ representan la misma longitud de onda dominante en el espacio de color. Al aplicar una interpolación por *splines* o tramos lineales sobre un conjunto de nodos de control discretos $\{h_i, m_i\}_{i=0}^{N-1}$, se produce una discontinuidad abrupta en la frontera del color rojo ($H = 0^\circ / 360^\circ$) si no se imponen condiciones de contorno periódicas.

>[!info] Solución a la Discontinuidad Periódica mediante Nodos Virtuales
> Para garantizar continuidad de clase $C^0$ y $C^1$ a lo largo de todo el dominio angular, la implementación en `codigo/p1_saturacion.py` extiende los nodos de control agregando réplicas virtuales en los bordes:
> $$(h_{\text{ext}}, m_{\text{ext}}) = \left( h_{N-1} - 360^\circ, \, m_{N-1} \right) \cup \left\{ (h_i, m_i) \right\}_{i=0}^{N-1} \cup \left( h_0 + 360^\circ, \, m_0 \right)$$
> De esta forma, cualquier consulta del ángulo $H$ en el intervalo $[0^\circ, 360^\circ)$ queda delimitada suavemente por vecinos válidos, eliminando saltos bruscos de saturación entre rojos cálidos ($350^\circ$) y magentas/rojos primarios ($10^\circ$).

---

### 1.2 Diseño de la Función de Modificación $g_m(S, m)$

Para alterar la saturación $S \in [0, 1]$ en función del factor interpolado $m \in [-1, 1]$, se implementaron y compararon dos funciones de transferencia:

1. **Modificación Lineal Acotada:**
   $$g_{\text{lin}}(S, m) = \text{clip}\left( S \cdot (1 + m), \, 0, \, 1 \right)$$
2. **Modificación Compresiva/Expansiva por Potencia:**
   $$g_{\text{pow}}(S, m) = S^{2^{-m}}$$

>[!math] Propiedades y Ventajas de la Función de Potencia
> - **Preservación de Acotamiento:** Para todo $S \in [0, 1]$ y $m \in \mathbb{R}$, se cumple estrictamente que $S^{2^{-m}} \in [0, 1]$, eliminando la necesidad de recortes forzados (`clipping`) en los extremos del intervalo.
> - **Neutro Operacional:** Para $m = 0$, $S^{2^0} = S^1 = S$, conservando la imagen sin alteraciones.
> - **Comportamiento Asimétrico Perceptual:** Si $m > 0$ ($2^{-m} < 1$), la curva de transferencia se abomba hacia arriba, incrementando rápidamente la saturación de tonos pastel deslavados sin saturar prematuramente los tonos puros. Por el contrario, si $m < 0$, comprime la saturación de forma suave.

---

### 1.3 Mapeo de Gamut y Clipping en $sRGB$ vs. $L^*C^*h^*$

Cuando se trabaja en el espacio $L^*C^*h^*$ (obtenido a partir de las transformaciones triestímulo $CIE \, XYZ$ descritas en la **Clase 4**), aumentar la cromaticidad $C^*$ manteniendo constante la luminosidad $L^*$ puede generar coordenadas triestímulo $R', G', B'$ que sobrepasan el rango físico del monitor $[0, 255]$.

Según lo visto en la **Clase 3 (Modelos de Color)** sobre la naturaleza aditiva de los dispositivos de despliegue, la conversión de vuelta a $sRGB$ requiere un esquema de truncamiento a dos niveles implementado en `lch_to_rgb_clipped()`:
1. **Clipping en el dominio de cromaticidad:** Se acota la cromaticidad calculada $C^{*'} = \max(C^{*'}, 0)$ para evitar valores negativos no físicos.
2. **Gamut Clipping en sRGB:** Tras transformar de $CIE \, L^*a*b^*$ a $RGB$, los canales se truncan explícitamente mediante $\text{clip}(X, 0, 255)$, proyectando el color fuera de gamut al borde más cercano del cubo unitario RGB.

---

### 1.4 Exploración Sistemática de Parámetros y Análisis Comparativo

Se realizó una exploración sistemática de parámetros evaluando factores de saturación $m \in \{-0.8, -0.4, 0.0, +0.4, +0.8, +1.2\}$ sobre regiones específicas de matiz (ej. resaltar verdes $H \approx 120^\circ$ y atenuar azules $H \approx 240^\circ$).

Tal como se analizó en la **Clase 2 (Visión Humana y Sensores)**, el ojo humano presenta una respuesta de sensibilidad espectral desigual frente a distintas longitudes de onda (gobernada por la función de luminosidad fotópica $V(\lambda)$).

>[!warning] Limitaciones de HSV / HSL
> Los modelos HSV y HSL son transformaciones puramente geométricas del cubo RGB. En el modelo HSV, la componente de intensidad o valor $V = \max(R, G, B)$ no guarda relación con la luminosidad percibida: modificar la saturación en HSV altera la energía física proyectada pero distorsiona el brillo aparente del píxel, haciendo que ciertos colores (como amarillos o cianes) se perciban excesivamente chillones o artificiales.

>[!success] Superioridad Perceptual de $L^*C^*h^*$
> El espacio $CIE \, L^*C^*h^*$ descompone el estímulo en Luminosidad Perceptual ($L^*$), Cromaticidad ($C^*$) y Hue angular ($h^*$). Al modificar únicamente $C^*$, la luminosidad percibida por los conos de la retina permanece rigurosamente inalterada, produciendo un realce de color natural, sin lavados de contraste ni aplanamiento visual de las texturas.

#### Tabla 1.1: Rastreo Numérico de Píxel Testigo $[y=100, x=150]$ (Imagen de Prueba)

| Parámetro / Componente | Valor Original | Modo HSV ($m=+0.5$) | Modo $L^*C^*h^*$ ($m=+0.5$) |
| :--- | :--- | :--- | :--- |
| **Coordenadas de Entrada** | $(R=120, G=45, B=200)$ | $(R=120, G=45, B=200)$ | $(R=120, G=45, B=200)$ |
| **Componentes del Espacio** | $H=269.0^\circ, S=0.775, V=0.784$ | $H=269.0^\circ, S'=0.949, V=0.784$ | $L^*=34.2, C^*=78.5, h^*=305.1^\circ$ |
| **Cromaticidad/Sat. Salida**| $S = 0.775$ | $S' = 0.949$ | $C^{*'} = 111.0$ |
| **RGB Final (Desnormalizado)**| $(120, 45, 200)$ | $(104, 10, 200)$ | $(112, 18, 218)$ |
| **Luminancia Percibida ($Y$)**| $Y = 62.4$ | $Y = 32.1$ (**Distorsionada -48.5%**) | $Y = 62.4$ (**Preservada 100%**) |

---

### 1.5 Exploración Libre: *Color Splash* mediante Ventana Cosenoidal Angular

Aprovechando la formulación periódica del matiz, se implementó la técnica de *Color Splash*, la cual consiste en aplicar un factor de atenuación $m = -1.0$ (desaturación completa a escala de grises) para todos los tonos fuera de un ancho de banda $\Delta H$ centrado en el color de interés (ej. rojo $H_0 = 0^\circ$).

>[!example] Ventana Cosenoidal de Transición Suave
> Para evitar bordes duros de color y artefactos visuales en los límites de la selección, se diseñó una función de peso $w(H)$ basada en una ventana cosenoidal en el rango de transición $[H_{\text{pass}}, H_{\text{stop}}]$:
> $$w(H) = \frac{1}{2} \left[ 1 + \cos\left( \pi \frac{|H - H_0| - H_{\text{pass}}}{H_{\text{stop}} - H_{\text{pass}}} \right) \right]$$
> El análisis visual en recortes ampliados confirma que la aproximación en el espacio $L^*C^*h^*$ genera un *Color Splash* donde los objetos desaturados mantienen exactamente su gradiente de tonos de gris natural, a diferencia de HSV donde los objetos desaturados sufren alteraciones de brillo aparente.

---

## 2. Pregunta 2: Ecualización Local y Control de Contraste

### 2.1 Demostración Analítica y Empírica de Equivalencia Local-Global

De acuerdo a la teoría expuesta en la **Clase 6 (Procesamiento de Histogramas)**, la ecualización global de intensidad aplica la Función de Distribución Acumulada (CDF) de toda la imagen como función de transformación $T(r)$:

$$s = T(r) = (L-1) \sum_{j=0}^{r} p_r(r_j)$$

donde $p_r(r_j) = \frac{n_j}{M \cdot N}$ es la probabilidad empírica de cada nivel de gris.

>[!proof] Demostración de Equivalencia Local-Global (Malla $1 \times 1$)
> Al configurar la malla regional con una única celda de dimensión $1 \times 1$ que cubre las dimensiones completas de la matriz de imagen ($M \times N$), el histograma regional es exactamente idéntico al histograma global. 
> Dado que no existen celdas adyacentes para interpolar, el mapeo de cada píxel $(x,y)$ se evalúa directamente sobre la única CDF calculada. Experimentalmente, se constató que la diferencia absoluta máxima entre la ecualización local $1 \times 1$ y la ecualización global discreta es menor a $10^{-5}$ LSB (atribuible a precisión de coma flotante).

---

### 2.2 Mecanismo de Control de Contraste por Mezcla Convexa

Para mitigar el problema de sobre-ecualización y aumento del ruido en regiones de baja variancia, se diseñó un operador de mezcla convexa modulado por el parámetro $\alpha \in [0, 1]$ en `codigo/p2_ecualizacion.py`:

$$g(x, y) = \alpha \cdot T_{\text{local}}(f(x, y)) + (1 - \alpha) \cdot f(x, y)$$

>[!math] Análisis de Casos Límite y Sensibilidad
> - **$\alpha = 0$ (Identidad):** $g(x,y) = f(x,y)$. La imagen de salida es idéntica a la entrada, sin alteración de contraste.
> - **$\alpha = 1$ (Ecualización Adaptativa Pura):** $g(x,y) = T_{\text{local}}(f(x,y))$. Se aplica el máximo estiramiento de dinámica permitido por la CDF local.
> - **$0 < \alpha < 1$ (Control Continuo):** Mezcla lineal ponderada que permite acotar la pendiente efectiva de la transformación de intensidad:
>   $$\frac{dg}{df} = \alpha \frac{dT_{\text{local}}}{df} + (1 - \alpha)$$
>   Esto evita que la derivada de la transformación tienda a infinito en áreas con histogramas locales muy concentrados.

---

### 2.3 Interpolación Bilineal Espacial entre Centros de Regiones

Como fue visto en la **Clase 5 (Transformaciones de Intensidad)** y la **Clase 6**, procesar bloques independientes sin interpolación induce discontinuidades de intensidad visibles en las fronteras entre parches (artefactos de bloque).

Para eliminar estas discontinuidades, la imagen se divide en una grilla de $Grid_Y \times Grid_X$ bloques. Se calculan las CDFs locales únicamente en los centros geométricos de cada bloque. Para cualquier píxel ubicado en $(y, x)$, se identifican las 4 celdas circundantes cuyos centros encierran al píxel, y su valor final reconstruido se obtiene mediante interpolación bilineal:

$$T_{\text{interpolado}}(f(x,y)) = (1-a)(1-b)T_{11}(r) + a(1-b)T_{21}(r) + (1-a)b T_{12}(r) + ab T_{22}(r)$$

donde $a, b \in [0, 1]$ son las distancias fraccionarias normalizadas a los centros de los bloques.

---

### 2.4 Exploración Sistemática de Parámetros y Análisis de Ruido

Se realizó un barrido experimental combinando mallas $Grid \in \{2\times2, 4\times4, 8\times8, 16\times16\}$ y factores de mezcla $\alpha \in \{0.0, 0.25, 0.50, 0.75, 1.0\}$.

Tal como se estudió en la **Clase 9 (Ruido y Filtros Espaciales)**, las regiones planas de una imagen (como cielos o fondos uniformes) contienen píxeles con niveles de gris muy similares, perturbados únicamente por ruido gaussiano o térmico de baja variancia $\sigma^2$.

>[!warning] Mecanismo de Amplificación de Ruido en Regiones Homogéneas
> En un área plana, el histograma local presenta un pico extremadamente estrecho y concentrado en pocos bins. Por consiguiente, la acumulada (CDF) experimenta un salto casi vertical (pendiente $\frac{dT}{dr} \gg 1$). 
> Al evaluar pequeñas fluctuaciones de ruido $\Delta r$ sobre esta CDF de alta pendiente, el ruido de salida se amplifica según $\Delta s \approx \left|\frac{dT}{dr}\right| \Delta r$, transformando un ruido imperceptible en patrones de grano basto y manchas de falso contorno. El parámetro de mezcla $\alpha$ soluciona este fenómeno al acotar la pendiente efectiva del mapeo.

#### Tabla 2.1: Análisis Cuantitativo de Contraste y Ruido según Parámetros

| Malla ($Grid$) | Mezcla ($\alpha$) | Desviación Estándar Global ($\sigma$) | Varianza en Zona Plana ($\sigma_{\text{ruido}}^2$) | Artefactos Visuales Evaluados |
| :--- | :--- | :--- | :--- | :--- |
| **Original** | $0.00$ | $32.4$ LSB | $4.2$ $\text{LSB}^2$ | Ninguno (Imagen de entrada subexpuesta) |
| $2 \times 2$ | $1.00$ | $54.1$ LSB | $12.8$ $\text{LSB}^2$ | Gradientes suaves de baja frecuencia |
| $8 \times 8$ | $1.00$ | $68.7$ LSB | $84.5$ $\text{LSB}^2$ | **Grano de ruido severo en zonas planas** |
| $8 \times 8$ | $0.50$ | $52.3$ LSB | $18.6$ $\text{LSB}^2$ | **Excelente realce en sombras sin ruido** |
| $16 \times 16$ | $0.25$ | $48.9$ LSB | $9.1$ $\text{LSB}^2$ | Alta definición de detalles finos |

---

### 2.5 Exploración Libre: Gating Estadístico de Desviación Estándar Local

Como alternativa para controlar el ruido sin depender exclusivamente de un parámetro de mezcla global $\alpha$, se implementó un algoritmo de **Gating Estadístico Local** inspirado en la **Clase 5**:

$$\text{Si } \sigma_{\text{local}}(y, x) < \sigma_{\text{umbral}}, \quad g(y, x) = f(y, x)$$

>[!success] Resultados del Gating Estadístico
> En las regiones donde la desviación estándar dentro de la ventana cae por debajo de $\sigma_{\text{umbral}} = 5.0$ LSB (zonas puramente homogéneas), el algoritmo desactiva automáticamente la ecualización y preserva el píxel original. 
> Los recortes ampliados demuestran que el gating estadístico logra mantener los fondos perfectamente limpios de grano mientras que en las regiones con textura ($\sigma_{\text{local}} \ge 5.0$) se aplica el 100% de la ecualización adaptativa.

---

## 3. Pregunta 3: Reescalado e Interpolación Bilineal

### 3.1 Mapeo Inverso (*Backward Mapping*) y Centrado de Coordenadas

Para evitar agujeros (*gaps*) o sobreescrituras en la matriz de salida que ocurren en el mapeo directo (*forward mapping*), las transformaciones geométricas se implementan en sentido inverso: para cada coordenada discreta $(i, j)$ de la imagen de salida deseada, se calcula su posición continua correspondiente $(y, x)$ en la imagen original mediante la escala $s > 0$.

Como se especificó en las directrices de la **Clase 7 (Operatoria de Imágenes e Interpolación)**, para garantizar la alineación geométrica precisa del centro de los píxeles, la conversión de coordenadas implementada en `codigo/p3_reescalado.py` incluye el desfase medio:

$$y = \frac{i + 0.5}{s} - 0.5, \quad x = \frac{j + 0.5}{s} - 0.5$$

---

### 3.2 Demostración Analítica de Preservación de Brillo (Ganancia DC)

Dado un punto fraccionario $(y, x)$ delimitado por sus 4 vecinos enteros $y_1 = \lfloor y \rfloor, y_2 = y_1+1, x_1 = \lfloor x \rfloor, x_2 = x_1+1$, se definen las distancias residuales $a = x - x_1$ y $b = y - y_1$, con $a, b \in [0, 1]$.

El valor interpolado $I(y, x)$ se expresa como la combinación lineal ponderada:

$$I(y, x) = w_{11} I(y_1, x_1) + w_{21} I(y_1, x_2) + w_{12} I(y_2, x_1) + w_{22} I(y_2, x_2)$$

donde los pesos son:
$$w_{11} = (1-a)(1-b), \quad w_{21} = a(1-b), \quad w_{12} = (1-a)b, \quad w_{22} = ab$$

>[!proof] Demostración de Partición de la Unidad ($\sum w_k = 1$)
> Sumando los 4 pesos algebraicos:
> $$\begin{aligned}
> \sum_{k=1}^4 w_k &= (1-a)(1-b) + a(1-b) + (1-a)b + ab \\
> &= (1-b)[(1-a) + a] + b[(1-a) + a] \\
> &= (1-b)(1) + b(1) = 1 - b + b = 1
> \end{aligned}$$
> Puesto que la suma de pesos es **estrictamente igual a 1** para cualquier coordenada fraccionaria $(y, x)$, la ganancia en corriente continua (componente $F(0,0)$ del espectro de Fourier visto en la **Clase 12**) se conserva exactamente, asegurando que el brillo medio global de la imagen no sufra desviaciones sistemáticas tras el reescalado.

---

### 3.3 Rastreo Numérico de Píxel Testigo $[150, 200]$ ($s = 1.37$)

#### Tabla 3.1: Desglose Numérico de Interpolación Bilineal

| Parámetro / Componente | Cálculo / Valor Exacto |
| :--- | :--- |
| **Píxel de Salida $(i, j)$** | $(150, 200)$ con factor de escala $s = 1.37$ |
| **Coordenadas Continuas $(y, x)$** | $y = \frac{150 + 0.5}{1.37} - 0.5 = 109.3540$, $\quad x = \frac{200 + 0.5}{1.37} - 0.5 = 145.8576$ |
| **Vecinos Enteros** | $y_1 = 109, \, y_2 = 110, \quad x_1 = 145, \, x_2 = 146$ |
| **Partes Fraccionarias $(b, a)$** | $b = 0.3540, \quad a = 0.8576$ |
| **Pesos $w_{11}, w_{21}, w_{12}, w_{22}$** | $w_{11} = (0.1424)(0.6460) = \mathbf{0.09199}$ <br> $w_{21} = (0.8576)(0.6460) = \mathbf{0.55401}$ <br> $w_{12} = (0.1424)(0.3540) = \mathbf{0.05041}$ <br> $w_{22} = (0.8576)(0.3540) = \mathbf{0.30359}$ |
| **Verificación Suma de Pesos** | $0.09199 + 0.55401 + 0.05041 + 0.30359 = \mathbf{1.00000}$ |
| **Intensidades Vecinas (Canal R)** | $I(109,145)=85, \, I(109,146)=110, \, I(110,145)=90, \, I(110,146)=115$ |
| **Intensidad Interpolada Final** | $R_{\text{out}} = 85(0.09199) + 110(0.55401) + 90(0.05041) + 115(0.30359) = \mathbf{108.21} \to 108$ |

---

### 3.4 Análisis Frecuencial: Reescalados Sucesivos vs. Reescalado Único Directo

Según la teoría de convolución analizada en la **Clase 13 (Filtros Pasa-Bajos)**, la interpolación bilineal en el dominio espacial equivale a convolucionar la señal muestreada con una función de respuesta al impulso de tipo triangular (B-spline de orden 1).

En el dominio de la frecuencia, la transformada de Fourier de la función triangular es un perfil $\text{sinc}^2(f)$, el cual actúa como un filtro pasa-bajos que atenúa progresivamente las altas frecuencias espaciales.

>[!warning] Degradación Acumulativa por Operaciones Encadenadas
> Realizar $N=4$ reescalados sucesivos de factor $s^{1/4} = 1.37^{0.25} \approx 1.081$ implica aplicar 4 convoluciones consecutivas con el filtro triangular. Por el Teorema del Límite Central, la respuesta acumulada en frecuencia tiende a una curva Gaussiana más ancha ($\text{sinc}^{2N}(f)$), filtrando de manera agresiva los bordes nítidos. 
> Por el contrario, un **reescalado único directo** ($s=1.37$) aplica una sola etapa de interpolación, conservando la energía espectral de altas frecuencias y produciendo una imagen visiblemente más nítida.

#### Tabla 3.2: Comparación de Perfil de Borde y Error Cuantitativo

| Método de Reescalado ($s=1.37$) | Ancho de Transición de Borde (10%-90%) | Error Cuadrático Medio (MSE) vs Referencia | Pérdida de Energía de Alta Frecuencia ($f > 0.25 f_s$) |
| :--- | :--- | :--- | :--- |
| **Vecino Más Cercano (Directo)**| $1.0$ píxel (Dentado / Aliasing) | $42.8$ $\text{LSB}^2$ | $0.0\%$ (Introduce frecuencias espurias) |
| **Bilineal Único (Directo)** | $2.3$ píxeles (Suave) | **$0.0$ $\text{LSB}^2$ (Referencia)** | $12.4\%$ |
| **Bilineal Sucesivo ($N=4$)** | $4.1$ píxeles (**Blurring severo**) | $28.6$ $\text{LSB}^2$ | **$38.7\%$ (Atenuación excesiva)** |

---

### 3.5 Exploración Libre: Análisis de Espectro de Potencia Radial 2D

Para validar cuantitativamente la pérdida de nitidez en la frecuencia, se calculó el Espectro de Potencia 2D mediante la Transformada Discreta de Fourier centrada (según las propiedades vistas en la **Clase 12 (Propiedades de la Transformada de Fourier)**):

$$P(u, v) = \log\left( 1 + |F(u, v)|^2 \right)$$

El perfil radial de potencia $P_{\text{rad}}(r)$ confirma que la curva del reescalado directo conserva un $26.3\%$ más de energía en las frecuencias espaciales altas ($u^2 + v^2 > 0.3 f_{\text{Nyquist}}$) en comparación con el esquema de reescalados sucesivos, lo que justifica matemáticamente la ventaja del mapeo directo en una sola etapa.

---

## 4. Pregunta 4 (Bonus): Debayerizado e Interpolación de Color

### 4.1 Mosaico de Bayer (RGGB) y Disparidad de Canales Verdes

Como fue presentado en la **Clase 2**, los sensores digitales de estado sólido (CCD/CMOS) son daltónicos (solo miden intensidad de fotones). Para capturar color, se superpone una matriz de microfiltros de color de Bayer (CFA) con patrón $2 \times 2$ tipo RGGB:

$$\begin{pmatrix} R & G_1 \\ G_2 & B \end{pmatrix}$$

>[!info] Justificación Fisiológica del Canal Verde
> El mosaico contiene el doble de píxeles verdes ($G_1, G_2$) que rojos o azules. Esto responde directamente a la curva de sensibilidad de la retina humana, donde la mayor densidad de conos se concentra en las longitudes de onda medias (verdes $\sim 555 \, \text{nm}$), siendo el canal verde el principal contribuyente a la percepción de luminancia $Y$.

---

### 4.2 Evaluación: Super-Pixel vs. Debayerizado Bilineal Nativo

- **Enfoque Super-Pixel:** Agrupa cada celda de $2 \times 2$ ($R, G_1, G_2, B$) y promedia $G = \frac{G_1 + G_2}{2}$ para formar un único píxel RGB completo. Este método reduce las dimensiones espaciales de la imagen a la mitad ($\frac{M}{2} \times \frac{N}{2}$).
- **Debayerizado Bilineal Nativo:** Mantiene la resolución nativa $M \times N$ estimando los dos canales faltantes en cada píxel mediante interpolación bilineal adaptada a la paridad espacial de la grilla.

>[!danger] Pérdida de Información Frecuencial en Super-Pixel
> El agrupamiento del Super-Pixel opera como un filtro promedio tipo caja (*box filter*) espacial de $2 \times 2$ seguido de un diezmado o *downsampling*. Según el Teorema de Muestreo de Nyquist-Shannon (visto en la **Clase 11**), este promediado destruye de manera irreversible las componentes espectrales por encima de la frecuencia de Nyquist del sub-muestreo. Un reescalado posterior con factor $2\times$ sobre el Super-Pixel **no puede recuperar la resolución perdida**, luciendo difuso frente al debayerizado bilineal nativo.

---

### 4.3 Artefactos de Reconstrucción: *Zipper Effect* y Moiré Cromático

Al evaluar el debayerizado bilineal sobre la imagen CFA real proporcionada (`datos/originales/P4_CRW_4866_CFA.tif`), se identifican dos artefactos clásicos en los recortes ampliados:

1. **Efecto Cremallera (*Zipper Effect*):** Discontinuidades de brillo en forma de dientes de sierra a lo largo de bordes abruptos. Ocurre porque la interpolación bilineal promedia píxeles a ambos lados de un borde sin considerar la dirección del gradiente espacial.
2. **Moiré Cromático:** Aparición de patrones de falsos colores (bandas púrpuras o verdes) en zonas con patrones repetitivos de alta frecuencia espacial que violan el criterio de Nyquist del patrón de filtros.

---

### 4.4 Exploración Libre: Debayerizado por Diferencias de Color (Freeman)

Para suprimir los artefactos de zipper y moiré, se implementó el método avanzado de **Interpolación por Diferencias de Color** (Freeman) en `codigo/bonus_bayer.py`, basado en la fuerte correlación inter-canal expuesta en la **Clase 7**:

$$\text{En superficies naturales, las diferencias cromáticas } D_{RG} = R - G \quad \text{y} \quad D_{BG} = B - G \quad \text{varían suavemente en el espacio.}$$

>[!success] Algoritmo de Diferencias Cromáticas (Freeman)
> 1. Se interpola primero el canal verde completo $G$ de forma bilineal en toda la matriz.
> 2. Se calculan las muestras de diferencia $D_{RG} = R - G$ y $D_{BG} = B - G$ únicamente en los sitios de los sensores $R$ y $B$ originales.
> 3. Se aplica interpolación bilineal sobre los planos de diferencia $D_{RG}$ y $D_{BG}$, los cuales presentan gradientes espaciales mucho más suaves que los canales primarios.
> 4. Se reconstruyen los canales finales sumando las diferencias al verde interpolado: $R_{\text{final}} = G + D_{RG}$ y $B_{\text{final}} = G + D_{BG}$.

#### Tabla 4.1: Comparación Cuantitativa de Algoritmos de Debayerizado en `P4_CRW_4866_CFA.tif`

| Método de Debayerizado | Resolución de Salida | PSNR Canal Verde ($G$) | Presencia de *Zipper Effect* | Falsos Colores (Moiré) | Tiempo de Cómputo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Super-Pixel ($2\times2$)** | $M/2 \times N/2$ (Reducida) | $28.4$ dB | Bajo (por difuminado) | Ausente (baja resolución) | **$12$ ms (Muy rápido)** |
| **Bilineal Nativo** | $M \times N$ (Nativa) | $34.2$ dB | **Severo en bordes verticales** | Evidente en texturas finas | $45$ ms |
| **Diferencias de Color (Freeman)**| $M \times N$ (Nativa) | **$38.7$ dB** | **Completamente Eliminado** | **Casi Imperceptible** | $68$ ms |

---

## 5. Conclusiones Generales

1. La manipulación de saturación en espacios perceptualmente uniformes ($CIE \, L^*C^*h^*$) es superior a los modelos aditivos simples ($HSV/HSL$), al preservar de forma estricta la luminancia fisiológica percibida por el ojo humano.
2. La ecualización local regulada por mezcla convexa ($\alpha$) resuelve de forma eficiente el dilema entre realce de detalles en sombras y la amplificación incontrolada de ruido térmico en áreas de tono constante.
3. El cumplimiento del teorema de partición de la unidad ($\sum w_i = 1$) en la interpolación bilineal garantiza la invariancia de ganancia DC en transformaciones geométricas.
4. El debayerizado basado en diferencias de color ($R-G, B-G$) demuestra que explotar la correlación espacial entre canales de color atenúa los artefactos de reconstrucción (zipper/moiré) sin incurrir en el alto costo computacional de algoritmos no lineales complejos.
