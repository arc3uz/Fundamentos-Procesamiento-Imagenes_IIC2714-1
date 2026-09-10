"""
Módulo para la Pregunta 3: Reescalado e Interpolación Bilineal
IEE2714 Fundamentos de Procesamiento de Imágenes
"""

import numpy as np


def reescalar_imagen(
    img: np.ndarray,
    s: float,
    metodo: str = "bilineal"
) -> np.ndarray:
    """
    Reescala una imagen (escala de grises o RGB) mediante un factor real s en [0.5, 2.0]
    usando mapeo hacia atrás (backward mapping).
    
    Parámetros:
    -----------
    img : np.ndarray
        Imagen de entrada 2D (H, W) o 3D (H, W, C), valores flotantes en [0, 1].
    s : float
        Factor de escala real (0.5 <= s <= 2.0).
    metodo : str
        'vecino' (Nearest Neighbor) o 'bilineal'.
        
    Retorna:
    --------
    np.ndarray con la imagen reescalada.
    """
    if not (0.49 <= s <= 2.01):
        raise ValueError(f"El factor s={s} está fuera del rango [0.5, 2.0].")

    img_in = np.clip(img.astype(np.float64), 0.0, 1.0)
    es_gris = (img_in.ndim == 2)
    if es_gris:
        img_in = img_in[:, :, np.newaxis]

    H_in, W_in, C = img_in.shape

    # 1. Dimensiones de salida redondeadas al entero más cercano
    H_out = int(np.round(H_in * s))
    W_out = int(np.round(W_in * s))

    # 2. Mapeo hacia atrás con alineación de centros
    i_out, j_out = np.indices((H_out, W_out), dtype=np.float64)
    y_in = (i_out + 0.5) / s - 0.5
    x_in = (j_out + 0.5) / s - 0.5

    if metodo.lower() in ["vecino", "nn", "nearest"]:
        # Vecino más cercano: redondeo y saturación en los bordes
        y_nn = np.clip(np.round(y_in).astype(np.int64), 0, H_in - 1)
        x_nn = np.clip(np.round(x_in).astype(np.int64), 0, W_in - 1)
        salida = img_in[y_nn, x_nn, :]

    elif metodo.lower() in ["bilineal", "bilinear"]:
        # Coordenadas de los 4 vecinos
        y1 = np.floor(y_in).astype(np.int64)
        x1 = np.floor(x_in).astype(np.int64)
        y2 = y1 + 1
        x2 = x1 + 1

        # Distancias fraccionarias en [0, 1)
        dy = y_in - y1
        dx = x_in - x1

        # Tratamiento de bordes: saturar índices a la grilla válida [0, H-1] y [0, W-1]
        y1_c = np.clip(y1, 0, H_in - 1)
        y2_c = np.clip(y2, 0, H_in - 1)
        x1_c = np.clip(x1, 0, W_in - 1)
        x2_c = np.clip(x2, 0, W_in - 1)

        # Cálculo de los 4 pesos (suma igual a 1)
        w11 = ((1.0 - dy) * (1.0 - dx))[:, :, np.newaxis]
        w12 = ((1.0 - dy) * dx)[:, :, np.newaxis]
        w21 = (dy * (1.0 - dx))[:, :, np.newaxis]
        w22 = (dy * dx)[:, :, np.newaxis]

        # Interpolación bilineal sobre todos los canales
        salida = (
            w11 * img_in[y1_c, x1_c, :] +
            w12 * img_in[y1_c, x2_c, :] +
            w21 * img_in[y2_c, x1_c, :] +
            w22 * img_in[y2_c, x2_c, :]
        )
    else:
        raise ValueError(f"Método '{metodo}' no reconocido. Use 'vecino' o 'bilineal'.")

    salida = np.clip(salida, 0.0, 1.0)
    return salida[:, :, 0] if es_gris else salida