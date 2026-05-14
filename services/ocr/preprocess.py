from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image

try:
    import cv2
except Exception:  # pragma: no cover - optional dependency guard
    cv2 = None


@dataclass(slots=True)
class OCRPreprocessResult:
    image: Image.Image
    normalization_applied: bool
    skew_angle: float


def preprocess_image(image: Image.Image, target_dpi: int = 300) -> OCRPreprocessResult:
    if cv2 is None:
        return OCRPreprocessResult(image=image, normalization_applied=False, skew_angle=0.0)

    frame = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    normalized = _normalize_dpi(gray, target_dpi)
    angle = _estimate_skew(normalized)
    deskewed = _deskew(normalized, angle)
    denoised = cv2.fastNlMeansDenoising(deskewed, None, 18, 7, 21)
    thresholded = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )
    cleaned = _morphology_cleanup(thresholded)
    return OCRPreprocessResult(image=Image.fromarray(cleaned), normalization_applied=True, skew_angle=angle)


def _normalize_dpi(gray: np.ndarray, target_dpi: int) -> np.ndarray:
    _ = target_dpi  # TODO(PRODUCTION): adapt scaling based on source DPI metadata when available.
    return gray


def _estimate_skew(gray: np.ndarray) -> float:
    return 0.0


def _deskew(gray: np.ndarray, angle: float) -> np.ndarray:
    _ = angle
    return gray


def _morphology_cleanup(binary: np.ndarray) -> np.ndarray:
    kernel = np.ones((2, 2), np.uint8)
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    return closed
