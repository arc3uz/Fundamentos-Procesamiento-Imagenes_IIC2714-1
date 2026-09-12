import cv2
import numpy as np


def interpolar_m_periodico(h_grados: np.ndarray, puntos_control: list[tuple[float, float]]) -> np.ndarray:
    """Calcula m(h) mediante interpolación lineal por tramos periódica en [0, 360)."""
    pts = sorted(puntos_control, key=lambda x: x[0])
    h_pts = np.array([p[0] for p in pts], dtype=np.float64)
    m_pts = np.array([p[1] for p in pts], dtype=np.float64)

    # Extensión circular para eliminar la discontinuidad en 0° / 360° (rojos)
    h_ext = np.concatenate(([h_pts[-1] - 360.0], h_pts, [h_pts[0] + 360.0]))
    m_ext = np.concatenate(([m_pts[-1]], m_pts, [m_pts[0]]))

    h_norm = np.mod(h_grados, 360.0)
    return np.interp(h_norm, h_ext, m_ext)


def funcion_g_m(componente: np.ndarray, m: np.ndarray, metodo: str = "lineal_escalado") -> np.ndarray:
    """
    Familia de funciones g_m:
      m = 0 : Valor neutro (sin cambio)
      m > 0 : Amplificación
      m < 0 : Atenuación
    """
    if metodo == "lineal_escalado":
        factor = np.where(m >= 0, 1.0 + 2.0 * m, 1.0 + m)
        return componente * np.maximum(0.0, factor)
    elif metodo == "potencia":
        gamma = np.power(2.0, -m)
        return np.power(np.clip(componente, 0.0, 1.0), gamma)
    else:  # Exponencial
        return np.maximum(0.0, componente * np.exp(m))


def rgb_a_lch(img_rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convierte RGB [0, 1] a CIE L*C*h* (h en grados [0, 360))."""
    img_lab = cv2.cvtColor((img_rgb * 255.0).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float64)
    L = img_lab[:, :, 0]
    a = img_lab[:, :, 1] - 128.0
    b = img_lab[:, :, 2] - 128.0

    C = np.sqrt(a**2 + b**2)
    h_deg = np.mod(np.degrees(np.arctan2(b, a)), 360.0)
    return L, C, h_deg


def lch_a_rgb(L: np.ndarray, C: np.ndarray, h_deg: np.ndarray) -> np.ndarray:
    """Reconstruye RGB [0, 1] a partir de L*, C* y h* (grados)."""
    h_rad = np.radians(h_deg)
    a = C * np.cos(h_rad) + 128.0
    b = C * np.sin(h_rad) + 128.0

    lab = np.stack([L, a, b], axis=-1)
    lab = np.clip(lab, 0, 255).astype(np.uint8)
    rgb = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB).astype(np.float64) / 255.0
    return np.clip(rgb, 0.0, 1.0)


def ColorSaturation(
    img_rgb: np.ndarray,
    puntos_control: list[tuple[float, float]],
    modo: str = "HS",
    metodo_gm: str = "lineal_escalado",
) -> np.ndarray:
    """Herramienta central de saturación selectiva por tono."""
    img_norm = img_rgb.astype(np.float64) / 255.0 if img_rgb.dtype == np.uint8 else np.clip(img_rgb, 0.0, 1.0)

    if modo.upper() == "HS":
        # Conversión RGB -> HSV
        img_hsv = cv2.cvtColor((img_norm * 255.0).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float64)
        H_deg = img_hsv[:, :, 0] * 2.0  # OpenCV escala H a [0, 180)
        S = img_hsv[:, :, 1] / 255.0
        V = img_hsv[:, :, 2] / 255.0

        # Mapeo y transformación
        m_map = interpolar_m_periodico(H_deg, puntos_control)
        S_mod = np.clip(funcion_g_m(S, m_map, metodo=metodo_gm), 0.0, 1.0)

        # Reconstrucción (H y V intactos)
        hsv_out = np.stack([H_deg / 2.0, S_mod * 255.0, V * 255.0], axis=-1)
        res = cv2.cvtColor(np.clip(hsv_out, 0, 255).astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float64) / 255.0

    elif modo.upper() in ["LCH", "CIE_LCH"]:
        L, C, h_deg = rgb_a_lch(img_norm)

        # Mapeo y transformación
        m_map = interpolar_m_periodico(h_deg, puntos_control)
        C_mod = np.maximum(0.0, funcion_g_m(C, m_map, metodo=metodo_gm))

        # Reconstrucción (L* y h* intactos)
        res = lch_a_rgb(L, C_mod, h_deg)

    else:
        raise ValueError(f"Modo '{modo}' desconocido. Debe ser 'HS' o 'LCh'.")

    return np.clip(res, 0.0, 1.0)