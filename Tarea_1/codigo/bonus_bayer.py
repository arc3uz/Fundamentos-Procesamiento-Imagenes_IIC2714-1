"""
Módulo para el Bonus: Debayerizado e Interpolación de Color
IEE2714 Fundamentos de Procesamiento de Imágenes
"""

import numpy as np
from codigo.p3_reescalado import reescalar_imagen


def simular_mosaico_bayer_rggb(img_rgb: np.ndarray) -> np.ndarray:
    """
    Genera una matriz monocanal simulando el sensor con patrón Bayer RGGB.
    """
    H, W, _ = img_rgb.shape
    # Asegurar dimensiones pares
    H = H - (H % 2)
    W = W - (W % 2)
    img = img_rgb[:H, :W]

    bayer = np.zeros((H, W), dtype=np.float64)
    # Patrón RGGB
    bayer[0::2, 0::2] = img[0::2, 0::2, 0]  # R
    bayer[0::2, 1::2] = img[0::2, 1::2, 1]  # G1
    bayer[1::2, 0::2] = img[1::2, 0::2, 1]  # G2
    bayer[1::2, 1::2] = img[1::2, 1::2, 2]  # B
    return bayer


def debayer_super_pixel(bayer: np.ndarray) -> np.ndarray:
    """
    Reconstruye una imagen RGB agrupando bloques 2x2: (R, (G1+G2)/2, B).
    La salida tiene la mitad del tamaño en cada dimensión.
    """
    H, W = bayer.shape
    H_half, W_half = H // 2, W // 2

    R = bayer[0::2, 0::2][:H_half, :W_half]
    G1 = bayer[0::2, 1::2][:H_half, :W_half]
    G2 = bayer[1::2, 0::2][:H_half, :W_half]
    B = bayer[1::2, 1::2][:H_half, :W_half]

    G = 0.5 * (G1 + G2)
    rgb_super = np.stack([R, G, B], axis=-1)
    return np.clip(rgb_super, 0.0, 1.0)


def debayer_bilineal(bayer: np.ndarray) -> np.ndarray:
    """
    Debayerizado bilineal a resolución original para patrón RGGB.
    Manejo de bordes por padding reflectivo.
    """
    H, W = bayer.shape
    # Padding de 1 píxel para evaluar vecinos en los bordes de la imagen
    pad = np.pad(bayer, pad_width=1, mode='reflect')

    R_out = np.zeros((H, W), dtype=np.float64)
    G_out = np.zeros((H, W), dtype=np.float64)
    B_out = np.zeros((H, W), dtype=np.float64)

    # Coordenadas internas desplazadas por el padding (+1)
    p = pad

    # 1. Posiciones R (i par, j par) -> índices en pad: (2k+1, 2m+1)
    # R conocido
    R_out[0::2, 0::2] = p[1:-1:2, 1:-1:2]
    # G = cruz (4 vecinos)
    G_out[0::2, 0::2] = 0.25 * (p[0:-2:2, 1:-1:2] + p[2::2, 1:-1:2] + p[1:-1:2, 0:-2:2] + p[1:-1:2, 2::2])
    # B = diagonal (4 vecinos)
    B_out[0::2, 0::2] = 0.25 * (p[0:-2:2, 0:-2:2] + p[0:-2:2, 2::2] + p[2::2, 0:-2:2] + p[2::2, 2::2])

    # 2. Posiciones B (i impar, j impar) -> índices en pad: (2k+2, 2m+2)
    # B conocido
    B_out[1::2, 1::2] = p[2:-1:2, 2:-1:2]
    # G = cruz (4 vecinos)
    G_out[1::2, 1::2] = 0.25 * (p[1:-2:2, 2:-1:2] + p[3::2, 2:-1:2] + p[2:-1:2, 1:-2:2] + p[2:-1:2, 3::2])
    # R = diagonal (4 vecinos)
    R_out[1::2, 1::2] = 0.25 * (p[1:-2:2, 1:-2:2] + p[1:-2:2, 3::2] + p[3::2, 1:-2:2] + p[3::2, 3::2])

    # 3. Posiciones G1 (i par, j impar) -> índices en pad: (2k+1, 2m+2)
    # G conocido
    G_out[0::2, 1::2] = p[1:-1:2, 2:-1:2]
    # R = vecinos horizontales (izquierda, derecha)
    R_out[0::2, 1::2] = 0.5 * (p[1:-1:2, 1:-2:2] + p[1:-1:2, 3::2])
    # B = vecinos verticales (arriba, abajo)
    B_out[0::2, 1::2] = 0.5 * (p[0:-2:2, 2:-1:2] + p[2::2, 2:-1:2])

    # 4. Posiciones G2 (i impar, j par) -> índices en pad: (2k+2, 2m+1)
    # G conocido
    G_out[1::2, 0::2] = p[2:-1:2, 1:-1:2]
    # R = vecinos verticales (arriba, abajo)
    R_out[1::2, 0::2] = 0.5 * (p[1:-2:2, 1:-1:2] + p[3::2, 1:-1:2])
    # B = vecinos horizontales (izquierda, derecha)
    B_out[1::2, 0::2] = 0.5 * (p[2:-1:2, 0:-2:2] + p[2:-1:2, 2::2])

    rgb_reconst = np.stack([R_out, G_out, B_out], axis=-1)
    return np.clip(rgb_reconst, 0.0, 1.0)


def reconstruir_comparaciones_bayer(bayer: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Ejecuta las tres reconstrucciones exigidas para comparar a resolución completa:
    1. Super-Pixel + Vecino más cercano (factor 2)
    2. Super-Pixel + Bilineal (factor 2)
    3. Debayerizado Bilineal a resolución nativa
    """
    # 1. Super-Pixel base
    sp_base = debayer_super_pixel(bayer)

    # 2. Reescalado x2 con módulo de la Pregunta 3
    sp_nn_x2 = reescalar_imagen(sp_base, s=2.0, metodo="vecino")
    sp_bi_x2 = reescalar_imagen(sp_base, s=2.0, metodo="bilineal")

    # 3. Debayerizado directo
    debayer_nativo = debayer_bilineal(bayer)

    # Ajuste simétrico de bordes
    H_min = min(bayer.shape[0], sp_nn_x2.shape[0], sp_bi_x2.shape[0], debayer_nativo.shape[0])
    W_min = min(bayer.shape[1], sp_nn_x2.shape[1], sp_bi_x2.shape[1], debayer_nativo.shape[1])

    return sp_nn_x2[:H_min, :W_min], sp_bi_x2[:H_min, :W_min], debayer_nativo[:H_min, :W_min]