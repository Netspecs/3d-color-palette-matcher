"""
Color utilities for the 3D Print Color Palette Matcher.

Provides:
    * Dominant color extraction from an image using k-means clustering
      (implemented with NumPy so no scikit-learn dependency is required).
    * Color space conversions (sRGB -> CIE L*a*b*).
    * Perceptual color distance (CIE76 Delta E) for filament matching.
    * A helper to find the closest filaments for a given color.
"""

from typing import Dict, List, Tuple

import numpy as np
from PIL import Image


# ---------------------------------------------------------------------------
# Color conversions
# ---------------------------------------------------------------------------
def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert an ``(r, g, b)`` tuple to a ``#RRGGBB`` string."""
    r, g, b = (int(max(0, min(255, round(c)))) for c in rgb)
    return f"#{r:02X}{g:02X}{b:02X}"


def _srgb_to_linear(channel: np.ndarray) -> np.ndarray:
    """Convert gamma-corrected sRGB (0-1) to linear RGB."""
    return np.where(channel <= 0.04045, channel / 12.92, ((channel + 0.055) / 1.055) ** 2.4)


def rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """
    Convert an array of RGB colors (values 0-255, shape (..., 3)) to CIE L*a*b*.

    Uses the D65 reference white. Returns an array of the same leading shape
    with the last axis holding (L, a, b).
    """
    rgb = np.asarray(rgb, dtype=np.float64) / 255.0
    linear = _srgb_to_linear(rgb)

    # Linear sRGB -> XYZ (D65)
    matrix = np.array([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ])
    xyz = linear @ matrix.T

    # Normalize by D65 white point
    white = np.array([0.95047, 1.00000, 1.08883])
    xyz = xyz / white

    # XYZ -> Lab
    epsilon = 0.008856
    kappa = 903.3
    f = np.where(xyz > epsilon, np.cbrt(xyz), (kappa * xyz + 16) / 116)

    fx, fy, fz = f[..., 0], f[..., 1], f[..., 2]
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    return np.stack([L, a, b], axis=-1)


def delta_e(lab1: np.ndarray, lab2: np.ndarray) -> np.ndarray:
    """CIE76 Delta E (Euclidean distance in Lab space)."""
    return np.sqrt(np.sum((lab1 - lab2) ** 2, axis=-1))


# ---------------------------------------------------------------------------
# Brightness / saturation adjustment (HSV based)
# ---------------------------------------------------------------------------
def adjust_rgb(rgb: Tuple[int, int, int], brightness: float = 1.0,
               saturation: float = 1.0) -> Tuple[int, int, int]:
    """
    Adjust the brightness and saturation of an ``(r, g, b)`` color.

    Args:
        rgb: Source color, channels 0-255.
        brightness: Multiplier for the HSV "value" channel (1.0 = unchanged).
        saturation: Multiplier for the HSV "saturation" channel (1.0 = unchanged).

    Returns:
        The adjusted ``(r, g, b)`` tuple with channels clamped to 0-255.
    """
    import colorsys
    r, g, b = (c / 255.0 for c in rgb)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    s = max(0.0, min(1.0, s * saturation))
    v = max(0.0, min(1.0, v * brightness))
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


# ---------------------------------------------------------------------------
# K-means clustering (NumPy implementation)
# ---------------------------------------------------------------------------
def _kmeans(data: np.ndarray, k: int, max_iters: int = 50, seed: int = 42):
    """
    Simple k-means clustering.

    Returns (centroids, counts) where ``counts`` is the number of pixels
    assigned to each centroid (used to rank colors by prevalence).
    """
    rng = np.random.default_rng(seed)
    n = data.shape[0]
    k = min(k, n)

    # k-means++ style initialization for more stable results
    centroids = np.empty((k, data.shape[1]), dtype=np.float64)
    centroids[0] = data[rng.integers(n)]
    for i in range(1, k):
        dists = np.min(
            np.sum((data[:, None, :] - centroids[None, :i, :]) ** 2, axis=2), axis=1
        )
        total = dists.sum()
        if total == 0:
            centroids[i] = data[rng.integers(n)]
            continue
        probs = dists / total
        centroids[i] = data[rng.choice(n, p=probs)]

    labels = np.zeros(n, dtype=np.int32)
    for _ in range(max_iters):
        # Assign step
        dists = np.sum((data[:, None, :] - centroids[None, :, :]) ** 2, axis=2)
        new_labels = np.argmin(dists, axis=1)
        if np.array_equal(new_labels, labels):
            labels = new_labels
            break
        labels = new_labels
        # Update step
        for i in range(k):
            members = data[labels == i]
            if len(members) > 0:
                centroids[i] = members.mean(axis=0)
            else:
                # Reseed empty cluster to a random point
                centroids[i] = data[rng.integers(n)]

    counts = np.bincount(labels, minlength=k)
    return centroids, counts


def extract_colors(image_path: str, num_colors: int = 4, max_dimension: int = 200) -> List[Dict]:
    """
    Extract the dominant colors from an image using k-means clustering.

    Args:
        image_path: Path to the image file.
        num_colors: Number of colors to extract (1-16).
        max_dimension: Image is downscaled so its longest side is at most this
            many pixels, which keeps clustering fast without hurting accuracy.

    Returns:
        A list of dicts sorted by prevalence (most dominant first), each with:
            rgb        : (r, g, b) int tuple
            hex        : "#RRGGBB" string
            percentage : float share of pixels (0-100)
    """
    num_colors = max(1, min(16, int(num_colors)))

    img = Image.open(image_path)
    # Flatten transparency onto white and ensure RGB
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        background = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(background, img).convert("RGB")
    else:
        img = img.convert("RGB")

    # Downscale for speed
    img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)

    data = np.asarray(img, dtype=np.float64).reshape(-1, 3)
    if data.shape[0] == 0:
        raise ValueError("The selected image contains no pixel data.")

    centroids, counts = _kmeans(data, num_colors)

    total = counts.sum()
    order = np.argsort(counts)[::-1]  # most prevalent first

    results = []
    for idx in order:
        if counts[idx] == 0:
            continue
        rgb = tuple(int(round(c)) for c in centroids[idx])
        results.append({
            "rgb": rgb,
            "hex": rgb_to_hex(rgb),
            "percentage": round(100.0 * counts[idx] / total, 1),
        })
    return results


# ---------------------------------------------------------------------------
# Filament matching
# ---------------------------------------------------------------------------
def match_filaments(
    target_rgb: Tuple[int, int, int],
    filaments: List[Dict],
    top_n: int = 3,
    brand_filter: str = None,
    material_filter: str = None,
) -> List[Dict]:
    """
    Find the closest filament colors to ``target_rgb`` using Delta E (CIE76).

    Args:
        target_rgb: The color to match, as an (r, g, b) tuple.
        filaments: List of filament dicts (each must contain an ``rgb`` key).
        top_n: Number of matches to return.
        brand_filter: If given, only consider filaments of this brand.
        material_filter: If given, only consider filaments of this material.

    Returns:
        A list of filament dicts (copies) sorted by closeness, each with an
        added ``distance`` key (lower is better).
    """
    candidates = filaments
    if brand_filter and brand_filter != "All":
        candidates = [f for f in candidates if f["brand"] == brand_filter]
    if material_filter and material_filter != "All":
        candidates = [f for f in candidates if f["material"] == material_filter]

    if not candidates:
        return []

    target_lab = rgb_to_lab(np.array(target_rgb, dtype=np.float64))
    cand_rgb = np.array([f["rgb"] for f in candidates], dtype=np.float64)
    cand_lab = rgb_to_lab(cand_rgb)

    distances = delta_e(cand_lab, target_lab[None, :])
    order = np.argsort(distances)

    matches = []
    for idx in order[:top_n]:
        match = dict(candidates[idx])
        match["distance"] = round(float(distances[idx]), 2)
        matches.append(match)
    return matches
