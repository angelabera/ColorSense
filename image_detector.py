from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from color_utils import detect_dominant_color


def load_image_as_rgb(image_path: str | Path) -> np.ndarray:
    path = Path(image_path)
    image_bgr = cv2.imread(str(path))
    if image_bgr is None:
        raise ValueError("The selected file is not a valid JPG, JPEG, or PNG image.")

    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)


def analyze_image_file(image_path: str | Path, top_n: int = 5) -> dict[str, object]:
    image_rgb = load_image_as_rgb(image_path)
    dominant_color, top_colors = detect_dominant_color(image_rgb, top_n=top_n)

    return {
        "path": str(Path(image_path)),
        "image_rgb": image_rgb,
        "image_preview": Image.fromarray(image_rgb),
        "dominant": dominant_color,
        "top_colors": top_colors,
        "width": int(image_rgb.shape[1]),
        "height": int(image_rgb.shape[0]),
    }
