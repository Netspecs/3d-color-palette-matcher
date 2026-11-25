"""
Color utilities for the 3D Print Color Palette Matcher.

Provides:
    * Dominant color extraction from an image using k-means clustering
      (implemented with NumPy so no scikit-learn dependency is required).
    * Color space conversions (sRGB -> CIE L*a*b*).
    * Perceptual color distance (CIEDE2000 Delta E) for filament matching.
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


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """
    Parse a hex color string into an ``(r, g, b)`` int tuple.

    Accepts values with or without a leading ``#`` and supports both the
    3-digit shorthand (``#abc``) and the full 6-digit form (``#aabbcc``).
    Raises ``ValueError`` if the string is not a valid hex color.
    """
    s = hex_str.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) != 6:
        raise ValueError(f"'{hex_str}' is not a valid hex color")
    try:
        return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        raise ValueError(f"'{hex_str}' is not a valid hex color")


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


def _lab_f_inv(t: np.ndarray) -> np.ndarray:
    delta = 6.0 / 29.0
    return np.where(t > delta, t ** 3, 3 * delta ** 2 * (t - 4.0 / 29.0))


def lab_to_rgb(lab: np.ndarray) -> np.ndarray:
    """
    Convert CIE L*a*b* colors back to sRGB (0-255, float) using D65.

    Inverse of :func:`rgb_to_lab`. Returns an array of the same leading shape
    with the last axis holding (r, g, b), clamped to 0-255.
    """
    lab = np.asarray(lab, dtype=np.float64)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]

    fy = (L + 16) / 116.0
    fx = fy + a / 500.0
    fz = fy - b / 200.0

    white = np.array([0.95047, 1.00000, 1.08883])
    xyz = np.stack([_lab_f_inv(fx), _lab_f_inv(fy), _lab_f_inv(fz)], axis=-1) * white

    # XYZ -> linear sRGB (D65)
    matrix = np.array([
        [3.2404542, -1.5371385, -0.4985314],
        [-0.9692660, 1.8760108, 0.0415560],
        [0.0556434, -0.2040259, 1.0572252],
    ])
    linear = xyz @ matrix.T
    # linear -> gamma sRGB
    srgb = np.where(linear <= 0.0031308, 12.92 * linear,
                    1.055 * np.clip(linear, 0, None) ** (1 / 2.4) - 0.055)
    return np.clip(srgb * 255.0, 0, 255)


def delta_e76(lab1: np.ndarray, lab2: np.ndarray) -> np.ndarray:
    """CIE76 Delta E (plain Euclidean distance in Lab space)."""
    return np.sqrt(np.sum((lab1 - lab2) ** 2, axis=-1))


def delta_e2000(lab1: np.ndarray, lab2: np.ndarray) -> np.ndarray:
    """
    CIEDE2000 color difference (the modern perceptual standard).

    This corrects CIE76's well-known weaknesses in the blue and neutral
    regions and is noticeably better at ranking "which filament looks closest"
    the way a human would judge it.

    Both inputs are arrays whose last axis is (L, a, b). They are broadcast
    against each other, so you can pass one (N, 3) array and one (3,) array.
    Returns an array of the broadcast shape (minus the last axis).
    """
    lab1 = np.asarray(lab1, dtype=np.float64)
    lab2 = np.asarray(lab2, dtype=np.float64)

    L1, a1, b1 = lab1[..., 0], lab1[..., 1], lab1[..., 2]
    L2, a2, b2 = lab2[..., 0], lab2[..., 1], lab2[..., 2]

    # Weighting factors (unity for the reference conditions).
    kL = kC = kH = 1.0

    C1 = np.sqrt(a1 ** 2 + b1 ** 2)
    C2 = np.sqrt(a2 ** 2 + b2 ** 2)
    C_bar = (C1 + C2) / 2.0

    C_bar7 = C_bar ** 7
    G = 0.5 * (1 - np.sqrt(C_bar7 / (C_bar7 + 25.0 ** 7)))

    a1p = (1 + G) * a1
    a2p = (1 + G) * a2

    C1p = np.sqrt(a1p ** 2 + b1 ** 2)
    C2p = np.sqrt(a2p ** 2 + b2 ** 2)

    h1p = np.degrees(np.arctan2(b1, a1p)) % 360.0
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360.0

    dLp = L2 - L1
    dCp = C2p - C1p

    dhp = h2p - h1p
    dhp = np.where(dhp > 180, dhp - 360, dhp)
    dhp = np.where(dhp < -180, dhp + 360, dhp)
    # When either chroma is zero, hue difference is undefined -> 0.
    dhp = np.where((C1p * C2p) == 0, 0.0, dhp)
    dHp = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dhp) / 2.0)

    Lp_bar = (L1 + L2) / 2.0
    Cp_bar = (C1p + C2p) / 2.0

    hsum = h1p + h2p
    habs = np.abs(h1p - h2p)
    hp_bar = np.where(
        (C1p * C2p) == 0, hsum,
        np.where(habs <= 180, hsum / 2.0,
                 np.where(hsum < 360, (hsum + 360) / 2.0, (hsum - 360) / 2.0)),
    )

    T = (1
         - 0.17 * np.cos(np.radians(hp_bar - 30))
         + 0.24 * np.cos(np.radians(2 * hp_bar))
         + 0.32 * np.cos(np.radians(3 * hp_bar + 6))
         - 0.20 * np.cos(np.radians(4 * hp_bar - 63)))

    d_theta = 30 * np.exp(-(((hp_bar - 275) / 25.0) ** 2))
    Cp_bar7 = Cp_bar ** 7
    Rc = 2 * np.sqrt(Cp_bar7 / (Cp_bar7 + 25.0 ** 7))
    Sl = 1 + (0.015 * (Lp_bar - 50) ** 2) / np.sqrt(20 + (Lp_bar - 50) ** 2)
    Sc = 1 + 0.045 * Cp_bar
    Sh = 1 + 0.015 * Cp_bar * T
    Rt = -np.sin(np.radians(2 * d_theta)) * Rc

    dE = np.sqrt(
        (dLp / (kL * Sl)) ** 2
        + (dCp / (kC * Sc)) ** 2
        + (dHp / (kH * Sh)) ** 2
        + Rt * (dCp / (kC * Sc)) * (dHp / (kH * Sh))
    )
    return dE


def delta_e(lab1: np.ndarray, lab2: np.ndarray) -> np.ndarray:
    """Default Delta E used across the app: CIEDE2000."""
    return delta_e2000(lab1, lab2)


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
    Simple k-means clustering (vectorized, NumPy-only).

    Returns ``(centroids, labels)``. ``labels`` gives the cluster index for
    every input row, which lets callers compute robust per-cluster statistics
    (medians, counts) afterwards.
    """
    rng = np.random.default_rng(seed)
    n = data.shape[0]
    k = max(1, min(k, n))

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
        dists = np.sum((data[:, None, :] - centroids[None, :, :]) ** 2, axis=2)
        new_labels = np.argmin(dists, axis=1)
        if np.array_equal(new_labels, labels):
            labels = new_labels
            break
        labels = new_labels
        for i in range(k):
            members = data[labels == i]
            if len(members) > 0:
                centroids[i] = members.mean(axis=0)
            else:
                centroids[i] = data[rng.integers(n)]

    return centroids, labels


# ---------------------------------------------------------------------------
# Image loading, background estimation and mask building
# ---------------------------------------------------------------------------
def load_rgb_array(image_path: str, max_dimension: int = 480) -> np.ndarray:
    """
    Load an image as an ``(H, W, 3)`` uint8 RGB array, flattening transparency
    onto white and downscaling so the longest side is at most ``max_dimension``.
    """
    img = Image.open(image_path)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        background = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(background, img).convert("RGB")
    else:
        img = img.convert("RGB")
    if max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
    return np.asarray(img, dtype=np.uint8)


def estimate_background_colors(arr: np.ndarray, n_colors: int = 4,
                               border_frac: float = 0.07) -> List[Tuple[int, int, int]]:
    """
    Estimate likely background colors by clustering the pixels around the image
    border (the frame is far more likely to be background than the subject).

    Returns a list of ``(r, g, b)`` tuples, most common border color first.
    """
    h, w = arr.shape[:2]
    bw = max(1, int(round(min(h, w) * border_frac)))
    top = arr[:bw].reshape(-1, 3)
    bottom = arr[-bw:].reshape(-1, 3)
    left = arr[:, :bw].reshape(-1, 3)
    right = arr[:, -bw:].reshape(-1, 3)
    border = np.concatenate([top, bottom, left, right], axis=0).astype(np.float64)
    if border.shape[0] == 0:
        return []

    # Cluster border pixels in Lab for perceptually sensible grouping.
    lab = rgb_to_lab(border)
    k = min(n_colors, max(1, len(np.unique(border, axis=0))))
    centroids, labels = _kmeans(lab, k)
    counts = np.bincount(labels, minlength=centroids.shape[0])
    order = np.argsort(counts)[::-1]

    colors = []
    for idx in order:
        if counts[idx] == 0:
            continue
        # Representative = border pixel nearest this cluster's Lab centroid.
        members = np.where(labels == idx)[0]
        d = np.sum((lab[members] - centroids[idx]) ** 2, axis=1)
        rgb = border[members[np.argmin(d)]]
        colors.append(tuple(int(round(c)) for c in rgb))
    return colors


def compute_keep_mask(arr: np.ndarray, exclusions=None, crop_norm=None,
                      extra_tol: float = 0.0) -> np.ndarray:
    """
    Build a boolean ``(H, W)`` keep-mask (True = analyze this pixel).

    Args:
        arr: ``(H, W, 3)`` RGB array.
        exclusions: iterable of ``{"rgb": (r,g,b), "tol": float}`` entries. Every
            pixel within ``tol`` (Euclidean distance in Lab) of an excluded
            color is dropped — this works across the WHOLE image, not just a
            connected region, so a build plate visible inside a loop is removed
            too.
        crop_norm: optional ``(x0, y0, x1, y1)`` in 0-1 fractions; pixels outside
            this rectangle are dropped.
        extra_tol: added to every exclusion tolerance (used for live tuning).

    The mask is defined purely by color + crop data, so it can be recomputed at
    any resolution and stays consistent across extraction, preview and cost.
    """
    h, w = arr.shape[:2]
    keep = np.ones((h, w), dtype=bool)

    if crop_norm:
        x0, y0, x1, y1 = crop_norm
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))
        cx0, cx1 = int(round(x0 * w)), int(round(x1 * w))
        cy0, cy1 = int(round(y0 * h)), int(round(y1 * h))
        region = np.zeros((h, w), dtype=bool)
        region[max(0, cy0):max(0, cy1), max(0, cx0):max(0, cx1)] = True
        keep &= region

    if exclusions:
        lab = rgb_to_lab(arr.astype(np.float64))
        for ex in exclusions:
            ex_lab = rgb_to_lab(np.array(ex["rgb"], dtype=np.float64))
            tol = float(ex.get("tol", 15.0)) + extra_tol
            dist = np.sqrt(np.sum((lab - ex_lab) ** 2, axis=-1))
            keep &= dist > tol

    return keep


# ---------------------------------------------------------------------------
# Dominant color extraction (Lab clustering + CIEDE2000 de-duplication)
# ---------------------------------------------------------------------------
def extract_colors_from_pixels(pixels: np.ndarray, num_colors: int = 4,
                               max_pixels: int = 40000, merge_delta: float = 7.0,
                               seed: int = 42) -> List[Dict]:
    """
    Extract dominant colors from a flat ``(N, 3)`` array of RGB pixels.

    Accuracy improvements over a plain RGB k-means:
      * Clustering happens in **CIE Lab** space (perceptually uniform).
      * The image is intentionally over-segmented, then near-duplicate clusters
        are merged with **CIEDE2000** so shadows/highlights of one real color
        don't show up as separate muddy entries.
      * Each cluster's representative is the member pixel nearest the cluster's
        **Lab median** (robust to shadow/specular outliers), so colors stay
        vivid instead of being averaged into mud.
    """
    num_colors = max(1, min(16, int(num_colors)))
    pixels = np.asarray(pixels, dtype=np.float64).reshape(-1, 3)
    if pixels.shape[0] == 0:
        raise ValueError("No pixels to analyze (the mask/crop removed everything).")

    rng = np.random.default_rng(seed)
    if pixels.shape[0] > max_pixels:
        pixels = pixels[rng.choice(pixels.shape[0], max_pixels, replace=False)]

    lab = rgb_to_lab(pixels)

    # Over-segment so minority colors (e.g. a thin green accent) get their own
    # cluster before we merge duplicates back down.
    n_unique = len(np.unique(np.round(pixels), axis=0))
    k_over = min(max(num_colors * 2 + 2, num_colors + 4), 16, n_unique)
    centroids_lab, labels = _kmeans(lab, k_over, seed=seed)

    clusters = []  # each: {"lab": rep_lab, "rgb": rep_rgb, "count": int}
    for i in range(centroids_lab.shape[0]):
        members = np.where(labels == i)[0]
        if members.size == 0:
            continue
        med = np.median(lab[members], axis=0)
        # Representative = real member pixel closest to the robust median.
        d = np.sum((lab[members] - med) ** 2, axis=1)
        rep_idx = members[int(np.argmin(d))]
        clusters.append({
            "lab": lab[rep_idx],
            "rgb": tuple(int(round(c)) for c in pixels[rep_idx]),
            "count": int(members.size),
        })

    # Merge near-duplicate clusters using CIEDE2000 (largest absorbs smaller).
    clusters.sort(key=lambda c: c["count"], reverse=True)
    merged = []
    for c in clusters:
        hit = None
        for m in merged:
            if delta_e2000(np.array(m["lab"]), np.array(c["lab"])) < merge_delta:
                hit = m
                break
        if hit is not None:
            hit["count"] += c["count"]
        else:
            merged.append(c)

    merged.sort(key=lambda c: c["count"], reverse=True)
    merged = merged[:num_colors]
    total = sum(c["count"] for c in merged) or 1

    results = []
    for c in merged:
        rgb = c["rgb"]
        results.append({
            "rgb": rgb,
            "hex": rgb_to_hex(rgb),
            "percentage": round(100.0 * c["count"] / total, 1),
        })
    return results


def extract_colors(image_path: str, num_colors: int = 4,
                   max_dimension: int = 240) -> List[Dict]:
    """
    Extract the dominant colors from an image file (no mask).

    Backwards-compatible entry point: loads the image and delegates to
    :func:`extract_colors_from_pixels`. For background-aware extraction, build a
    keep-mask with :func:`compute_keep_mask` and call
    ``extract_colors_from_pixels(arr[mask])`` directly.
    """
    arr = load_rgb_array(image_path, max_dimension)
    if arr.size == 0:
        raise ValueError("The selected image contains no pixel data.")
    return extract_colors_from_pixels(arr.reshape(-1, 3), num_colors)


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
    Find the closest filament colors to ``target_rgb`` using Delta E (CIEDE2000).

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
