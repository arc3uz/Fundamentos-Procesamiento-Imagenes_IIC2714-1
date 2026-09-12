import numpy as np
import matplotlib.pyplot as plt
import cv2


def calcular_cdf_ecualizacion(region: np.ndarray, num_bins: int = 256) -> np.ndarray:
    """
    Construye la función de mapeo T(r) a partir de la CDF empírica de una región.
    Retorna una LUT de tamaño num_bins normalizada en [0, 1].
    """
    # Se permite función externa para cálculo de histograma
    hist, _ = np.histogram(region, bins=num_bins, range=(0.0, 1.0))
    cdf = hist.cumsum().astype(np.float64)
    
    total_pixeles = cdf[-1]
    if total_pixeles > 0:
        cdf_norm = cdf / total_pixeles
    else:
        cdf_norm = np.linspace(0.0, 1.0, num_bins)
        
    return cdf_norm


def recortar_y_redistribuir_clahe(region: np.ndarray, num_bins: int = 256, clip_factor: float = 2.0) -> np.ndarray:
    """
    Implementación conceptual de CLAHE como referencia propia:
    Aplica recorte (clip limit) y redistribución uniforme sobre el histograma local.
    """
    hist, _ = np.histogram(region, bins=num_bins, range=(0.0, 1.0))
    n_pixels = region.size
    
    # Clip limit proporcional al histograma promedio
    limite = clip_factor * (n_pixels / num_bins)
    exceso = np.maximum(0, hist - limite).sum()
    hist_recortado = np.minimum(hist, limite)
    
    # Redistribución uniforme del exceso
    hist_recortado = hist_recortado + (exceso / num_bins)
    
    cdf = hist_recortado.cumsum().astype(np.float64)
    cdf_norm = cdf / cdf[-1]
    return cdf_norm


def ecualizacion_local_malla(
    img_gray: np.ndarray,
    n_regiones_y: int = 8,
    n_regiones_x: int = 8,
    num_bins: int = 256,
    alpha_contraste: float = 1.0,
    modo_control: str = "mezcla",
    clip_factor: float = 2.0
) -> np.ndarray:
    """
    Aplica ecualización local de histograma sobre una malla de regiones M x N
    utilizando interpolación bilineal entre los centros de las regiones.
    
    Parámetros:
    -----------
    img_gray : np.ndarray
        Imagen de entrada en escala de grises [0, 1].
    n_regiones_y, n_regiones_x : int
        Número de bloques en que se particiona la imagen vertical y horizontalmente.
    num_bins : int
        Número de bins para el histograma.
    alpha_contraste : float in [0, 1]
        Parámetro de nuestro mecanismo propio de control (0 = identidad, 1 = no limitado).
    modo_control : str
        'no_limitado', 'mezcla' (propuesto) o 'clip_clahe'.
    """
    img = np.clip(img_gray.astype(np.float64), 0.0, 1.0)
    H, W = img.shape

    # Caso borde o global: si n_regiones es (1, 1), equivale a ecualización global clásica
    if n_regiones_y == 1 and n_regiones_x == 1:
        cdf = calcular_cdf_ecualizacion(img, num_bins=num_bins)
        indices = np.clip((img * (num_bins - 1)).astype(np.int64), 0, num_bins - 1)
        salida = cdf[indices]
        if modo_control == "mezcla":
            salida = alpha_contraste * salida + (1.0 - alpha_contraste) * img
        return np.clip(salida, 0.0, 1.0)

    # 1. Definir dimensiones de bloques y coordenadas de los centros
    tam_by = H / n_regiones_y
    tam_bx = W / n_regiones_x

    centros_y = np.array([(i + 0.5) * tam_by for i in range(n_regiones_y)])
    centros_x = np.array([(j + 0.5) * tam_bx for j in range(n_regiones_x)])

    # 2. Calcular las transformaciones locales (LUTs) para cada bloque
    tablas_mapeo = np.zeros((n_regiones_y, n_regiones_x, num_bins), dtype=np.float64)

    for i in range(n_regiones_y):
        y_ini = int(i * tam_by)
        y_fin = int((i + 1) * tam_by) if i < n_regiones_y - 1 else H
        for j in range(n_regiones_x):
            x_ini = int(j * tam_bx)
            x_fin = int((j + 1) * tam_bx) if j < n_regiones_x - 1 else W

            sub_img = img[y_ini:y_fin, x_ini:x_fin]

            if modo_control == "clip_clahe":
                tablas_mapeo[i, j] = recortar_y_redistribuir_clahe(sub_img, num_bins, clip_factor)
            else:
                tablas_mapeo[i, j] = calcular_cdf_ecualizacion(sub_img, num_bins)

    # 3. Mapear cada píxel mediante interpolación bilineal entre centros de bloques
    indices_img = np.clip((img * (num_bins - 1)).astype(np.int64), 0, num_bins - 1)
    salida_local = np.zeros((H, W), dtype=np.float64)

    # Grillas de coordenadas de píxeles
    y_coords, x_coords = np.indices((H, W))

    # Identificar el intervalo de centros contiguos
    idx_y = np.searchsorted(centros_y, y_coords) - 1
    idx_x = np.searchsorted(centros_x, x_coords) - 1

    idx_y = np.clip(idx_y, 0, n_regiones_y - 2)
    idx_x = np.clip(idx_x, 0, n_regiones_x - 2)

    # Distancias normalizadas respecto a los centros vecinos
    y1 = centros_y[idx_y]
    y2 = centros_y[idx_y + 1]
    x1 = centros_x[idx_x]
    x2 = centros_x[idx_x + 1]

    # Pesos de interpolación acotados en [0, 1]
    delta_y = np.clip((y_coords - y1) / (y2 - y1), 0.0, 1.0)
    delta_x = np.clip((x_coords - x1) / (x2 - x1), 0.0, 1.0)

    # Evaluar las 4 transformaciones contextuales sobre los valores de los píxeles
    T11 = tablas_mapeo[idx_y, idx_x, indices_img]
    T12 = tablas_mapeo[idx_y, idx_x + 1, indices_img]
    T21 = tablas_mapeo[idx_y + 1, idx_x, indices_img]
    T22 = tablas_mapeo[idx_y + 1, idx_x + 1, indices_img]

    # Combinación bilineal
    salida_local = (
        (1.0 - delta_y) * (1.0 - delta_x) * T11 +
        (1.0 - delta_y) * delta_x * T12 +
        delta_y * (1.0 - delta_x) * T21 +
        delta_y * delta_x * T22
    )

    # 4. Mecanismo de Control de Contraste Propuesto (Mezcla convexa con la identidad)
    if modo_control == "mezcla":
        salida = alpha_contraste * salida_local + (1.0 - alpha_contraste) * img
    else:
        salida = salida_local

    return np.clip(salida, 0.0, 1.0)


def clahe_referencia_cv2(img_gray: np.ndarray, clip_limit: float = 2.0, tile_grid_size: tuple[int, int] = (8, 8)) -> np.ndarray:
    """Ejecución de CLAHE externo (OpenCV) autorizado únicamente como referencia comparativa."""
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    img_uint8 = (np.clip(img_gray, 0.0, 1.0) * 255.0).astype(np.uint8)
    res_uint8 = clahe.apply(img_uint8)
    return res_uint8.astype(np.float64) / 255.0


def graficar_histograma_comparativo(img_original, img_procesada, titulo="Comparación de Histogramas"):
    """
    Genera y grafica los histogramas de una imagen original y una procesada
    para evidenciar el estiramiento o redistribución del contraste.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 4))
    
    # Histograma de la imagen original
    hist_orig, _ = np.histogram(img_original.ravel(), bins=256, range=(0.0, 1.0))
    axes[0].plot(hist_orig, color='black', lw=1.5)
    axes[0].fill_between(range(256), hist_orig, color='gray', alpha=0.3)
    axes[0].set_title(f"Histograma: {titulo} (Original)")
    axes[0].set_xlabel("Nivel de Intensidad [0, 1]")
    axes[0].set_ylabel("Número de Píxeles")
    axes[0].grid(True, alpha=0.3)
    
    # Histograma de la imagen procesada
    hist_proc, _ = np.histogram(img_procesada.ravel(), bins=256, range=(0.0, 1.0))
    axes[1].plot(hist_proc, color='blue', lw=1.5)
    axes[1].fill_between(range(256), hist_proc, color='dodgerblue', alpha=0.3)
    axes[1].set_title(f"Histograma: {titulo} (Procesada)")
    axes[1].set_xlabel("Nivel de Intensidad [0, 1]")
    axes[1].set_ylabel("Número de Píxeles")
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()