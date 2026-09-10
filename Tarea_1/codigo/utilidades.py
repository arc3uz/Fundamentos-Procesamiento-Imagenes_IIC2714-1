"""
Módulo de funciones de utilidad general.
"""

import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
import tifffile


def ruta_datos(*subrutas: str) -> str:
    """Retorna ruta absoluta hacia la carpeta datos/."""
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(base, "..", "datos", *subrutas))


def cargar_imagen_rgb(nombre_archivo: str) -> np.ndarray:
    """Carga imagen TIF/PNG/JPG en flotante [0, 1] RGB."""
    ruta = ruta_datos("originales", nombre_archivo)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta}")

    img_bgr = cv2.imread(ruta)
    if img_bgr is not None:
        return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype(np.float64) / 255.0

    img_tif = tifffile.imread(ruta)
    if img_tif.ndim == 3 and img_tif.shape[2] == 3:
        divisor = 255.0 if img_tif.max() <= 255 else 65535.0
        return img_tif.astype(np.float64) / divisor

    raise ValueError(f"No fue posible cargar {nombre_archivo} como imagen RGB de 3 canales.")


def graficar_triptico(
    img_orig: np.ndarray, img_hs: np.ndarray, img_lch: np.ndarray, titulo: str, ruta_guardado: str = None
):
    """Genera figura comparativa de 3 paneles y la exporta opcionalmente."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    axes[0].imshow(img_orig)
    axes[0].set_title("Original")
    axes[0].axis("off")

    axes[1].imshow(img_hs)
    axes[1].set_title("Modo HS (HSV)")
    axes[1].axis("off")

    axes[2].imshow(img_lch)
    axes[2].set_title("Modo CIE $L^*C^*h^*$")
    axes[2].axis("off")

    fig.suptitle(titulo, fontsize=14, y=0.98)
    plt.tight_layout()

    if ruta_guardado:
        os.makedirs(os.path.dirname(ruta_guardado), exist_ok=True)
        plt.savefig(ruta_guardado, dpi=300, bbox_inches="tight")
    plt.show()