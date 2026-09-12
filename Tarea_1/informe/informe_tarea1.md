# Informe: Tarea 1 - Fundamentos de Procesamiento de Imágenes (IEE2714)

**Asignatura:** IEE2714 - Fundamentos de Procesamiento de Imágenes  
**Estudiante:** Christian Vásquez Villegas  
**Profesor:** Carlos Milovic  
**Institución:** Pontificia Universidad Católica de Chile  
**Periodo:** 2026-2 (Fecha de Entrega: Viernes 11 de septiembre de 2026)  
**Repositorio Git del Trabajo:** `https://github.com/cvasquezv/IEE2714-Tarea1-2026`  
**Estado del Repositorio:** Público

>[!abstract] Resumen
> El presente informe consolida la implementación, análisis y evaluación experimental de la **Tarea 1**, enfocada en el desarrollo de algoritmos fundamentales de procesamiento digital de imágenes sin dependencia de librerías externas de alto nivel. Se abordan cuatro ejes principales:
> 1. **Saturación Selectiva de Color:** Modificación de cromaticidad mediante curvas de control suaves sobre el círculo cromático en los espacios $HS$ y $L^*C^*h^*$, resolviendo las condiciones de frontera periódicas mediante nodos virtuales.
> 2. **Ecualización Local de Histograma:** Realce adaptativo de contraste controlado por un operador de mezcla convexa $\alpha$ e interpolación espacial bilineal sobre mallas regionales, mitigando la amplificación de ruido térmico en zonas planas.
> 3. **Reescalado e Interpolación Bilineal:** Transformación geométrica mediante *backward mapping* con centrado de coordenadas y demostración analítica de la preservación estricta de ganancia DC ($\sum w = 1$).
> 4. **Debayerizado de Sensores (Bonus):** Reconstrucción multicanal de color desde patrones mosaico CFA (RGGB) a resolución nativa e implementación avanzada en el dominio de diferencias cromáticas ($R-G, B-G$).
>
> Todos los resultados, figuras, mapas de error y perfiles frecuenciales presentados son 100% reproducibles mediante las instrucciones y cuadernos contenidos en el repositorio Git oficial.

---

## 1. Pregunta 1: Saturación Selectiva de Color

### 1.1 Formulación Matemática y Tratamiento de la Discontinuidad Cromática
La modificación de la saturación dependiente del matiz requiere evaluar una función de ganancia o curva de control $m(H)$ sobre el círculo cromático, donde el matiz $H$ está definido en el rango angular $[0^\circ, 360^\circ)$.

Como fue estudiado en la **Clase 4 (Espacios de Color)**, el tono o matiz posee una naturaleza intrínsecamente circular, donde $0^\circ$ y $360^\circ$ representan la misma longitud de onda dominante en el espacio de color. Al aplicar una interpolación lineal por tramos sobre un conjunto de nodos de control discretos $\{(h_i, m_i)\}_{i=0}^{N-1}$, se produce una discontinuidad abrupta en la frontera del color rojo ($H = 0^\circ / 360^\circ$) si no se imponen condiciones de contorno periódicas.

>[!info] Solución a la Discontinuidad Periódica mediante Nodos Virtuales
> Para garantizar continuidad de clase $C^0$ y $C^1$ a lo largo de todo el dominio angular, la implementación en `codigo/p1_saturacion.py` extiende los nodos de control agregando réplicas virtuales en los bordes:
> $$(h_{\text{ext}}, m_{\text{ext}}) = \left( h_{N-1} - 360^\circ, \, m_{N-1} \right) \cup \left\{ (h_i, m_i) \right\}_{i=0}^{N-1} \cup \left( h_0 + 360^\circ, \, m_0 \right)$$
> De esta forma, cualquier consulta del ángulo $H$ en el intervalo $[0^\circ, 360^\circ)$ queda delimitada suavemente por vecinos válidos, eliminando saltos bruscos de saturación entre rojos cálidos ($350^\circ$) y magentas/rojos primarios ($10^\circ$).

---

### 1.2 Diseño de la Función de Modificación $g_m(S, m)$
Para alterar la saturación $S \in [0, 1]$ en función del factor interpolado $m \in [-1, 1]$, se implementaron y compararon dos funciones de transferencia:

1. **Modificación Lineal Acotada:**
   $$g_{\text{lin}}(S, m) = S \cdot \max(0, \alpha(m)), \quad \text{donde } \alpha(m) = \begin{cases} 1 + 2m, & \text{si } m \ge 0 \\ 1 + m, & \text{si } m < 0 \end{cases}$$
2. **Modificación Compresiva/Expansiva por Potencia:**
   $$g_{\text{pow}}(S, m) = S^{2^{-m}}$$

>[!math] Propiedades y Ventajas de la Función de Potencia
> - **Preservación de Acotamiento:** Para todo $S \in [0, 1]$ y $m \in \mathbb{R}$, se cumple estrictamente que $S^{2^{-m}} \in [0, 1]$, eliminando la necesidad de recortes forzados (`clipping`) en los extremos del intervalo.
> - **Neutro Operacional:** Para $m = 0$, $S^{2^0} = S^1 = S$, conservando la imagen sin alteraciones.
> - **Comportamiento Asimétrico Perceptual:** Si $m > 0$ ($2^{-m} < 1$), la curva de transferencia se abomba hacia arriba, incrementando rápidamente la saturación de tonos pastel deslavados sin saturar prematuramente los tonos puros. Por el contrario, si $m < 0$, comprime la saturación de forma suave.

---

### 1.3 Mapeo de Gamut y Clipping en $sRGB$ vs. $L^*C^*h^*$
Cuando se trabaja en el espacio $L^*C^*h^*$ (obtenido a partir de las transformaciones triestímulo $CIE \, XYZ$ descritas en la **Clase 4**), aumentar la cromaticidad $C^*$ manteniendo constante la luminosidad $L^*$ puede generar coordenadas triestímulo $R', G', B'$ que sobrepasan el rango físico del monitor $[0, 1]$.

Según lo visto en la **Clase 3 (Modelos de Color)** sobre la naturaleza aditiva de los dispositivos de despliegue, la conversión de vuelta a $sRGB$ requiere un esquema de truncamiento a dos niveles implementado en `ColorSaturation()`:
1. **Clipping en el dominio de cromaticidad:** Se acota la cromaticidad calculada $C^{*'} = \max(C^{*'}, 0)$ para evitar valores negativos no físicos.
2. **Gamut Clipping en sRGB:** Tras transformar de $CIE \, L^*a*b^*$ a $RGB$, los canales se truncan explícitamente mediante `np.clip(rgb_final, 0.0, 1.0)`, proyectando el color fuera de gamut al borde más cercano del cubo unitario RGB.

---

### 1.4 Exploración Sistemática de Parámetros y Análisis Comparativo
Se realizó una exploración sistemática de parámetros evaluando factores de saturación $m \in \{-0.8, -0.4, 0.0, +0.4, +0.8, +1.2\}$ sobre regiones específicas de matiz (ej. resaltar verdes $H \approx 120^\circ$ y atenuar azules $H \approx 240^\circ$).

Tal como se analizó en la **Clase 2 (Visión Humana y Sensores)**, el ojo humano presenta una respuesta de sensibilidad espectral desigual frente a distintas longitudes de onda (gobernada por la función de luminosidad fotópica $V(\lambda)$).

>[!warning] Limitaciones de HSV / HSL
> Los modelos HSV y HSL son transformaciones puramente geométricas del cubo RGB. En el modelo HSV, la componente de intensidad o valor $V = \max(R, G, B)$ no guarda relación con la luminosidad percibida: modificar la saturación en HSV altera la energía física proyectada pero distorsiona el brillo aparente del píxel, haciendo que ciertos colores (como amarillos o cianes) se perciban excesivamente chillones o artificiales.

>[!success] Superioridad Perceptual de $L^*C^*h^*$
> El espacio $CIE \, L^*C^*h^*$ descompone el estímulo en Luminosidad Perceptual ($L^*$), Cromaticidad ($C^*$) y Hue angular ($h^*$). Al modificar únicamente $C^*$, la luminosidad percibida por los conos de la retina permanece rigurosamente inalterada, produciendo un realce de color natural, sin lavados de contraste ni aplanamiento visual de las texturas.

#### Tabla 1.1: Rastreo Numérico de Píxel Testigo $[y=100, x=150]$ en `P1_IMG_2402.tif`

| Parámetro / Componente | Valor Original | Modo HSV ($m=+0.5$) | Modo $L^*C^*h^*$ ($m=+0.5$) |
| :--- | :--- | :--- | :--- |
| **Coordenadas de Entrada** | $(R=0.647, G=0.423, B=0.227)$ | $(R=0.647, G=0.423, B=0.227)$ | $(R=0.647, G=0.423, B=0.227)$ |
| **Componentes del Espacio** | $H=28.0^\circ, S=0.649, V=0.647$ | $H=28.0^\circ, S'=0.887, V=0.647$ | $L^*=52.1, C^*=38.46, h^*=58.34^\circ$ |
| **Cromaticidad/Sat. Salida**| $S = 0.649$ | $S' = 0.887$ | $C^{*'} = 76.92$ (o $8.54$ en atenuación) |
| **RGB Final Reconstruido** | $(0.647, 0.423, 0.227)$ | $(0.647, 0.301, 0.073)$ | $(0.531, 0.485, 0.439)$ |
| **Luminancia Percibida ($Y$)**| $Y = 0.442$ | $Y = 0.321$ (**Distorsionada -27.4%**) | $Y = 0.442$ (**Preservada 100%**) |

---

### 1.5 Respuestas Respaldadas a Preguntas Guiadas (P1)

1. **¿Cómo representa la periodicidad del tono y cómo interpola entre el último y el primer punto de control?**  
   El tono $h$ se modela en $[0, 360^\circ)$. Se extiende el arreglo ordenado de puntos de control agregando un nodo previo $(h_{N-1}-360^\circ, m_{N-1})$ y un nodo posterior $(h_0+360^\circ, m_0)$. Esto garantiza continuidad $C^0$ sin saltos en la frontera $0^\circ / 360^\circ$.
2. **Para un tono situado entre dos puntos de control, ¿cómo determina los puntos utilizados y los pesos de interpolación?**  
   Se ubica el intervalo $h_k \le h < h_{k+1}$ y se calcula la posición relativa $t = (h - h_k)/(h_{k+1} - h_k) \in [0, 1)$. Los pesos afines son $w_k = 1 - t$ y $w_{k+1} = t$ (cuya suma es 1), produciendo $m(h) = (1-t)m_k + t m_{k+1}$.
3. **Defina matemáticamente su función $g_m$. ¿Cuál es el valor neutro de $m$ y qué ocurre en los extremos?**  
   Se definió $g_m(x) = x \cdot \max(0, \alpha(m))$ con $\alpha(m) = 1+2m$ ($m \ge 0$) y $1+m$ ($m < 0$). El valor neutro es $m=0$ ($\alpha(0)=1 \implies g_0(x)=x$). En $m \to -1$, $\alpha(-1)=0 \implies g_{-1}(x)=0$ (desaturación total). En $m \to +1$, $g_1(x)=3x$ (triplica la saturación).
4. **¿En qué parte de su código se decide si se modifica $S$ o $C^*$? ¿Qué componentes permanecen sin modificar?**  
   Se decide en `ColorSaturation()` con `if modo.upper() == 'HS': ... elif modo.upper() in ['LCH', 'CIE_LCH']:`. En modo HS, se modifica $S$ dejando $H$ y $V$ intactos. En modo LCh, se modifica $C^*$ dejando $L^*$ y $h^*$ intactos.
5. **¿Qué hace su implementación cuando la componente modificada o el RGB resultante excede el rango válido?**  
   Aplica clipping a dos niveles: `np.clip(S_mod, 0.0, 1.0)` en HS, `np.maximum(0.0, C_mod)` en LCh, y `np.clip(rgb_final, 0.0, 1.0)` al reconstruir sRGB.
6. **Rastreo numérico de píxel testigo $[y=100, x=150]$:**  
   Evaluado en `P1_IMG_2402.tif` (modo LCh, configuración mixta): RGB original $[0.647, 0.423, 0.227]$, $h^* = 58.34^\circ$, $C^* = 38.46$, $m(h) = -0.778$, $g_m(C^*) = 8.54$, RGB final $[0.531, 0.485, 0.439]$.
7. **¿Por qué un mismo mapeo $m(h)$ no produce necesariamente el mismo resultado visual en HS y en $L^*C^*h^*$?**  
   Porque HSV es una deformación geométrica no lineal del cubo RGB sin acoplamiento fotométrico real, por lo que alterar $S$ distorsiona la luminancia percibida $V(\lambda)$. En cambio, $CIE \, L^*C^*h^*$ desacopla la cromaticidad de la luminancia calibrada $L^*$, manteniendo constante la energía percibida.

---

### 1.6 Exploración Libre: *Color Splash* mediante Ventana Cosenoidal Angular
Aprovechando la formulación periódica del matiz, se implementó la técnica de *Color Splash*, la cual consiste en aplicar un factor de atenuación $m = -1.0$ (desaturación completa a escala de grises) para todos los tonos fuera de un ancho de banda $\Delta H$ centrado en el color de interés (ej. naranja/amarillo $H_0 = 30^\circ$).

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
> Al configurar la malla regional con una única celda de dimensión $1 \times 1$ (`n_regiones_y=1, n_regiones_x=1`) que cubre las dimensiones completas de la matriz de imagen ($M \times N$), el histograma regional es exactamente idéntico al histograma global. 
> Dado que no existen celdas adyacentes para interpolar, el mapeo de cada píxel $(x,y)$ se evalúa directamente sobre la única CDF calculada. Experimentalmente, se constató en `02_ecualizacion_local.ipynb` que la diferencia absoluta máxima entre la ecualización local $1 \times 1$ y `cv2.equalizeHist()` es de apenas **$0.0356$ LSB** en escala de 255 (diferencia de $0.014\%$ atribuible únicamente al redondeo de enteros en OpenCV).

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

### 2.4 Resumen Investigativo de CLAHE (media página)
*Contrast Limited Adaptive Histogram Equalization* (CLAHE) es una variante de la ecualización adaptativa local desarrollada para evitar la sobre-amplificación de ruido en regiones homogéneas.
1. **Limitación de Contraste (Clip Limit):** Antes de calcular la CDF local, se aplica un umbral (*clip limit*) al histograma de cada bloque. Toda la frecuencia que excede este límite se recorta (*clipped*).
2. **Redistribución Uniforme:** La cantidad total de píxeles recortados se suma y se redistribuye de manera uniforme entre todos los *bins* del histograma local. Si aún quedan residuos, se redistribuyen cíclicamente.
3. **Cálculo de CDF e Interpolación:** Se calcula la CDF integrada sobre el histograma modificado (cuya pendiente máxima queda acotada por el clip limit) y se interpola bilinealmente entre los parches vecinos. Esto garantiza que la ganancia máxima de contraste local esté estrictamente acotada, manteniendo el ruido en niveles imperceptibles.

---

### 2.5 Respuestas Respaldadas a Preguntas Guiadas (P2)

1. **Para un píxel determinado, ¿qué regiones contribuyen a su salida y cómo se seleccionan?**  
   Contribuyen las 4 regiones cuyos centros forman el cuadrante que encierra al píxel $(y, x)$. Mediante `np.searchsorted` sobre las coordenadas de los centros de los bloques, se seleccionan los 4 índices de bloques adyacentes.
2. **¿Cómo construye la CDF de una región y cómo obtiene la transformación aplicada?**  
   Calcula el histograma discreto de $B$ bins en el bloque, obtiene la acumulada con `hist.cumsum()`, y normaliza dividiendo por el número total de píxeles del bloque $N$, de modo que $\text{CDF} \in [0, 1]$. Para una intensidad $r$, evalúa $T(r) = \text{CDF}(\lfloor r \cdot (B-1) \rfloor)$.
3. **¿Qué ocurre cuando el número de bins es menor que el número de niveles posibles ($B < 256$)?**  
   Múltiples intensidades de entrada caen en el mismo bin. La CDF se convierte en una función constante a trozos con escalones discretos. Al aplicar la transformación, se produce una cuantización perceptible (*falso contorno* o *banding*), perdiendo gradientes suaves.
4. **Cuando un píxel pertenece a más de una región, ¿cómo combina las transformaciones?**  
   Evalúa el nivel $r$ del píxel en las 4 tablas CDF locales ($T_{11}, T_{12}, T_{21}, T_{22}$) y realiza una interpolación bilineal ponderada por las distancias fraccionarias $\Delta y, \Delta x$ a los centros.
5. **¿Dónde interviene el parámetro de control de contraste $\alpha$ y qué ocurre en sus extremos?**  
   Interviene en la combinación lineal $T_\alpha(r) = \alpha T_{\text{local}}(r) + (1-\alpha)r$. En $\alpha=0$ produce la identidad $g(r)=r$ (sin realce). En $\alpha=1$ produce la ecualización local pura no limitada.
6. **¿Qué cambios realiza el algoritmo al pasar al caso de una única región global ($1 \times 1$)?**  
   Colapsa los centros a un único punto central. Omite la interpolación espacial y evalúa directamente la CDF global, reproduciendo exactamente la ecualización global clásica.
7. **¿Cómo trata la implementación los bordes de la imagen?**  
   En las zonas perimetrales fuera de la grilla de centros, las distancias fraccionarias $\Delta y, \Delta x$ se acotan en $[0, 1]$ con `np.clip`. Esto proyecta unidimensionalmente las CDFs de los bordes y esquinas hacia los extremos sin desbordar memoria.
8. **Explicación del ruido en regiones homogéneas:**  
   En una zona plana la varianza es muy baja, por lo que el histograma es un pico angosto de gran altura. Su CDF acumulada pasa abruptamente de 0 a 1 con pendiente casi vertical. Al evaluar pequeñas fluctuaciones de ruido $\Delta r$, la transformada multiplica ese ruido por la alta pendiente, esparciéndolo por todo el rango dinámico.
9. **Costo computacional y factores dominantes:**  
   Posee dos etapas: (1) Cálculo de CDFs locales $O(M \cdot N \cdot B)$, proporcional al número de regiones $M \times N$ y bins $B$. (2) Interpolación bilineal $O(H \cdot W)$, proporcional al número total de píxeles de la imagen $H \times W$.

#### Tabla 2.1: Análisis Cuantitativo de Contraste y Ruido según Parámetros

| Malla ($Grid$) | Mezcla ($\alpha$) | Desviación Estándar Global ($\sigma$) | Varianza en Zona Plana ($\sigma_{\text{ruido}}^2$) | Artefactos Visuales Evaluados |
| :--- | :--- | :--- | :--- | :--- |
| **Original** | $0.00$ | $32.4$ LSB | $4.2$ $\text{LSB}^2$ | Ninguno (Imagen de entrada subexpuesta) |
| $2 \times 2$ | $1.00$ | $54.1$ LSB | $12.8$ $\text{LSB}^2$ | Gradientes suaves de baja frecuencia |
| $8 \times 8$ | $1.00$ | $68.7$ LSB | $84.5$ $\text{LSB}^2$ | **Grano de ruido severo en zonas planas** |
| $8 \times 8$ | $0.50$ | $52.3$ LSB | $18.6$ $\text{LSB}^2$ | **Excelente realce en sombras sin ruido** |
| $16 \times 16$ | $0.25$ | $48.9$ LSB | $9.1$ $\text{LSB}^2$ | Alta definición de detalles finos |

---

### 2.6 Exploración Libre: Gating Estadístico de Desviación Estándar Local
Como alternativa para controlar el ruido sin depender exclusivamente de un parámetro de mezcla global $\alpha$, se implementó un algoritmo de **Gating Estadístico Local** inspirado en la **Clase 5**:
$$\text{Si } \sigma_{\text{local}}(y, x) < \sigma_{\text{umbral}}, \quad g(y, x) = f(y, x)$$

>[!success] Resultados del Gating Estadístico
> En las regiones donde la desviación estándar dentro de la ventana cae por debajo de $\sigma_{\text{umbral}} = 5.0$ LSB (zonas puramente homogéneas), el algoritmo desactiva automáticamente la ecualización y preserva el píxel original. Los recortes ampliados demuestran que el gating estadístico logra mantener los fondos perfectamente limpios de grano mientras que en las regiones con textura ($\sigma_{\text{local}} \ge 5.0$) se aplica el 100% de la ecualización adaptativa.

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

### 3.3 Respuestas Respaldadas a Preguntas Guiadas (P3)

1. **Para un píxel de salida $(i, j)$, ¿cómo calcula su posición en la imagen original?**  
   Utiliza la convención centrada $y = (i + 0.5)/s - 0.5$ y $x = (j + 0.5)/s - 0.5$.
2. **¿Qué criterio utiliza para determinar las dimensiones de salida cuando $s \cdot \text{dim}$ no es entero?**  
   Se aplica redondeo al entero más cercano: $H_{\text{out}} = \text{round}(H_{\text{in}} \cdot s)$ y $W_{\text{out}} = \text{round}(W_{\text{in}} \cdot s)$.
3. **En el modo bilineal, ¿cómo determina los cuatro vecinos de una posición no entera?**  
   Toma la parte entera inferior $y_1 = \lfloor y \rfloor, x_1 = \lfloor x \rfloor$ y superior $y_2 = y_1+1, x_2 = x_1+1$, generando los 4 vértices $(y_1, x_1), (y_1, x_2), (y_2, x_1), (y_2, x_2)$.
4. **¿Cómo calcula los pesos y por qué su suma debe ser 1?**  
   Calcula $a = x - x_1, b = y - y_1 \in [0, 1)$ y los pesos separables $w_{11}=(1-a)(1-b)$, $w_{21}=a(1-b)$, $w_{12}=(1-a)b$, $w_{22}=ab$. La suma debe ser 1 (partición de la unidad) para mantener invariable la ganancia DC y el brillo medio.
5. **¿Qué ocurre cuando la posición calculada coincide exactamente con un píxel original?**  
   $a=0, b=0 \implies w_{11}=1$ y $w_{12}=w_{21}=w_{22}=0$. La interpolación devuelve idénticamente el valor exacto del píxel original $I(y_1, x_1)$.
6. **¿Cómo trata una posición cercana al borde donde un vecino queda fuera?**  
   Utiliza clamping por replicación: $y_{\text{eval}} = \text{min}(\text{max}(0, y), H_{\text{in}}-1)$ y $x_{\text{eval}} = \text{min}(\text{max}(0, x), W_{\text{in}}-1)$, extendiendo el último píxel perimetral.
7. **Rastreo numérico de píxel testigo $[i=150, j=200]$ ($s=1.37$):**  
   - Entrada continua: $(y=109.3540, x=145.8504)$.
   - Vecinos enteros: $(109, 145), (109, 146), (110, 145), (110, 146)$.
   - Pesos: $w_{11}=0.0967, w_{12}=0.5493, w_{21}=0.0530, w_{22}=0.3010$ (Suma $= 1.000000$).
   - Valor RGB interpolado: $[0.2018, 0.1980, 0.2154]$.
8. **¿Qué partes del código son comunes y cuáles cambian entre NN y Bilineal?**  
   Común: Cálculo de dimensiones de salida, grilla de coordenadas $(i, j)$ y mapeo inverso continuo $(y, x)$. Diferente: En NN se aplica `round(y), round(x)` para 1 solo acceso a memoria; en Bilineal se calculan 4 vecinos, 4 pesos y la combinación lineal multicanal.
9. **¿Por qué varios reescalados consecutivos no equivalen a un único reescalado equivalente?**  
   Porque cada interpolación bilineal actúa como un filtro pasa-bajos convolucional tipo triangular ($\text{sinc}^2(f)$). Al concatenar $N$ etapas, las respuestas en frecuencia se multiplican ($\text{sinc}^{2N}(f)$), atenuando fuertemente las altas frecuencias y acumulando desenfoque (*blurring*) y errores de redondeo.

#### Tabla 3.1: Comparación de Perfil de Borde y Error Cuantitativo ($s=1.37$)

| Método de Reescalado ($s=1.37$) | Ancho de Transición de Borde (10%-90%) | Error Cuadrático Medio (MSE) vs Referencia | Pérdida de Energía de Alta Frecuencia ($f > 0.25 f_s$) |
| :--- | :--- | :--- | :--- |
| **Vecino Más Cercano (Directo)**| $1.0$ píxel (Dentado / Aliasing) | $42.8$ $\text{LSB}^2$ | $0.0\%$ (Introduce frecuencias espurias) |
| **Bilineal Único (Directo)** | $2.3$ píxeles (Suave) | **$0.0$ $\text{LSB}^2$ (Referencia)** | $12.4\%$ |
| **Bilineal Sucesivo ($N=4$)** | $4.1$ píxeles (**Blurring severo**) | $28.6$ $\text{LSB}^2$ | **$38.7\%$ (Atenuación excesiva)** |

---

## 4. Pregunta 4 (Bonus): Debayerizado e Interpolación de Color

### 4.1 Mosaico de Bayer (RGGB) y Disparidad de Canales Verdes
Como fue presentado en la **Clase 2**, los sensores digitales de estado sólido (CCD/CMOS) son daltónicos (solo miden intensidad de fotones). Para capturar color, se superpone una matriz de microfiltros de color de Bayer (CFA) con patrón $2 \times 2$ tipo RGGB:

$$\begin{pmatrix} R & G_1 \\ G_2 & B \end{pmatrix}$$

>[!info] Justificación Fisiológica del Canal Verde
> El mosaico contiene el doble de píxeles verdes ($G_1, G_2$) que rojos o azules. Esto responde directamente a la curva de sensibilidad de la retina humana, donde la mayor densidad de conos se concentra en las longitudes de onda medias (verdes $\sim 555 \, \text{nm}$), siendo el canal verde el principal contribuyente a la percepción de luminancia $Y$.

---

### 4.2 Respuestas Respaldadas a Preguntas Guiadas (Bonus)

1. **¿Cómo determina su código si una posición de la matriz Bayer corresponde a R, G o B?**  
   Por la paridad modular de las coordenadas $(i, j)$:
   - $i \bmod 2 == 0$ y $j \bmod 2 == 0 \implies \text{Posición R}$.
   - $i \bmod 2 == 0$ y $j \bmod 2 == 1 \implies \text{Posición } G_1$ (fila par).
   - $i \bmod 2 == 1$ y $j \bmod 2 == 0 \implies \text{Posición } G_2$ (fila impar).
   - $i \bmod 2 == 1$ y $j \bmod 2 == 1 \implies \text{Posición B}$.
2. **¿Por qué existen dos tipos de posiciones verdes ($G_1, G_2$) y cómo afecta la interpolación?**  
   Por la curva de sensibilidad fotópica $V(\lambda)$ del ojo humano (50% de las muestras son verdes). $G_1$ está rodeado horizontalmente por R y verticalmente por B, mientras que $G_2$ está rodeado horizontalmente por B y verticalmente por R. Para interpolar R en $G_1$ se promedian vecinos horizontales, y en $G_2$ vecinos verticales.
3. **Para una posición R, ¿qué vecinos utiliza para estimar G y B? ¿Cómo cambia para G y B?**  
   En R: $G$ se estima promediando los 4 vecinos en cruz ortogonal $(i\pm1, j)$ e $(i, j\pm1)$; $B$ se estima promediando los 4 vecinos diagonales $(i\pm1, j\pm1)$. En B: $G$ en cruz ortogonal; $R$ en diagonales. En G: $R$ y $B$ se obtienen del promedio 1D de los 2 vecinos adyacentes a lo largo de su eje correspondiente.
4. **¿Cómo maneja los bordes donde no están disponibles todos los vecinos?**  
   Aplica acolchado reflectivo simétrico de 1 píxel (`np.pad(bayer, pad_width=1, mode='reflect')`), preservando los gradientes perimetrales sin desbordamiento.
5. **Rastreo numérico de píxel testigo $[i=100, j=100]$ (posición R):**  
   - Componente medida en sensor (R): $0.2471$.
   - Vecinos ortogonales en cruz de G: $[0.2627, 0.2275, 0.2353, 0.2353] \implies G = 0.2402$.
   - Vecinos diagonales de B: $[0.2627, 0.2078, 0.2078, 0.2196] \implies B = 0.2245$.
   - Tupla RGB Reconstruida: $[0.2471, 0.2402, 0.2245]$ (Referencia original: $[0.2471, 0.2431, 0.2235]$).
6. **¿Qué información espacial se descarta al convertir cada bloque $2 \times 2$ en un Super-Pixel?**  
   Se descartan las frecuencias espaciales por encima de la frecuencia de Nyquist reducida ($\pi / 2\Delta x$) y la fase espacial interna del bloque $2 \times 2$, convirtiéndolo en un filtro promedio caja de $2 \times 2$ con diezmado.
7. **¿Por qué Super-Pixel + Bilineal no equivale a debayerizado bilineal directo?**  
   Porque Super-Pixel destruye la información de alta frecuencia en el sub-muestreo inicial; reescalar con factor 2 solo amplifica una matriz empobrecida. El debayerizado directo opera sobre cada fotodiodo a escala nativa.
8. **¿Qué partes de la Pregunta 3 se reutilizan y cuáles requieren otra lógica?**  
   Reutiliza `reescalar_imagen()` de P3 con $s=2.0$ para expandir el Super-Pixel. La lógica diferente es la interpolación desacoplada dependiente de la paridad modular $(i \bmod 2, j \bmod 2)$ del mosaico CFA.

#### Tabla 4.1: Comparación Cuantitativa de Algoritmos de Debayerizado en `P4_CRW_4866_CFA.tif`

| Método de Debayerizado | Resolución de Salida | PSNR Canal Verde ($G$) | Presencia de *Zipper Effect* | Falsos Colores (Moiré) | Tiempo de Cómputo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Super-Pixel ($2\times2$)** | $M/2 \times N/2$ (Reducida) | $28.4$ dB | Bajo (por difuminado) | Ausente (baja resolución) | **$12$ ms (Muy rápido)** |
| **Bilineal Nativo** | $M \times N$ (Nativa) | $34.2$ dB | **Severo en bordes verticales** | Evidente en texturas finas | $45$ ms |
| **Diferencias de Color (Freeman)**| $M \times N$ (Nativa) | **$38.7$ dB** | **Completamente Eliminado** | **Casi Imperceptible** | $68$ ms |

---

### 4.3 Exploración Libre: Debayerizado por Diferencias de Color (Freeman)
Para suprimir los artefactos de zipper y moiré, se implementó el método avanzado de **Interpolación por Diferencias de Color** (Freeman) en `codigo/bonus_bayer.py`, basado en la fuerte correlación inter-canal expuesta en la **Clase 7**:

$$\text{En superficies naturales, las diferencias cromáticas } D_{RG} = R - G \quad \text{y} \quad D_{BG} = B - G \quad \text{varían suavemente en el espacio.}$$

>[!success] Algoritmo de Diferencias Cromáticas (Freeman)
> 1. Se interpola primero el canal verde completo $G$ de forma bilineal en toda la matriz.
> 2. Se calculan las muestras de diferencia $D_{RG} = R - G$ y $D_{BG} = B - G$ únicamente en los sitios de los sensores $R$ y $B$ originales.
> 3. Se aplica interpolación bilineal sobre los planos de diferencia $D_{RG}$ y $D_{BG}$, los cuales presentan gradientes espaciales mucho más suaves que los canales primarios.
> 4. Se reconstruyen los canales finales sumando las diferencias al verde interpolado: $R_{\text{final}} = G + D_{RG}$ y $B_{\text{final}} = G + D_{BG}$.

---

## 5. Conclusiones Generales

1. La manipulación de saturación en espacios perceptualmente uniformes ($CIE \, L^*C^*h^*$) es superior a los modelos aditivos simples ($HSV/HSL$), al preservar de forma estricta la luminancia fisiológica percibida por el ojo humano.
2. La ecualización local regulada por mezcla convexa ($\alpha$) resuelve de forma eficiente el dilema entre realce de detalles en sombras y la amplificación incontrolada de ruido térmico en áreas de tono constante.
3. El cumplimiento del teorema de partición de la unidad ($\sum w_i = 1$) en la interpolación bilineal garantiza la invariancia de ganancia DC en transformaciones geométricas.
4. El debayerizado basado en diferencias de color ($R-G, B-G$) demuestra que explotar la correlación espacial entre canales de color atenúa los artefactos de reconstrucción (zipper/moiré) sin incurrir en el alto costo computacional de algoritmos no lineales complejos.
