from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from PIL import Image

try:
    _BILINEAR = Image.Resampling.BILINEAR
except AttributeError:
    _BILINEAR = Image.BILINEAR


@dataclass(frozen=True)
class ColorSample:
    name: str
    rgb: tuple[int, int, int]
    hex_code: str
    percentage: float


COLOR_REFERENCE_MAP: dict[str, tuple[int, int, int]] = {
    "Black": (0, 0, 0),
    "White": (255, 255, 255),
    "Gray": (128, 128, 128),
    "Red": (220, 20, 60),
    "Orange": (255, 140, 0),
    "Yellow": (255, 215, 0),
    "Green": (34, 139, 34),
    "Lime": (124, 252, 0),
    "Cyan": (0, 206, 209),
    "Blue": (30, 144, 255),
    "Navy": (25, 25, 112),
    "Purple": (138, 43, 226),
    "Pink": (255, 105, 180),
    "Brown": (139, 69, 19),
    "Teal": (0, 128, 128),
}


def rgb_to_hex(rgb: Iterable[int]) -> str:
    red, green, blue = (int(value) for value in rgb)
    return f"#{red:02X}{green:02X}{blue:02X}"


def hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    clean_hex = hex_code.strip().lstrip("#")
    if len(clean_hex) != 6:
        raise ValueError("HEX code must have exactly 6 hexadecimal digits.")
    return tuple(int(clean_hex[index : index + 2], 16) for index in (0, 2, 4))


def format_rgb(rgb: Iterable[int]) -> str:
    red, green, blue = (int(value) for value in rgb)
    return f"({red}, {green}, {blue})"


def closest_color_name(rgb: Iterable[int]) -> str:
    target = np.array(tuple(int(value) for value in rgb), dtype=np.int16)
    best_name = "Unknown"
    best_distance = float("inf")

    for name, reference_rgb in COLOR_REFERENCE_MAP.items():
        reference = np.array(reference_rgb, dtype=np.int16)
        distance = float(np.linalg.norm(target - reference))
        if distance < best_distance:
            best_name = name
            best_distance = distance

    return best_name


def resize_for_analysis(image_rgb: np.ndarray, max_dimension: int = 240) -> np.ndarray:
    if image_rgb.size == 0:
        raise ValueError("Cannot analyze an empty image.")

    height, width = image_rgb.shape[:2]
    longest_side = max(height, width)
    if longest_side <= max_dimension:
        return image_rgb

    scale = max_dimension / float(longest_side)
    new_width = max(1, int(width * scale))
    new_height = max(1, int(height * scale))
    resized_image = Image.fromarray(image_rgb).resize((new_width, new_height), _BILINEAR)
    return np.asarray(resized_image)


def detect_top_colors(image_rgb: np.ndarray, top_n: int = 5) -> list[ColorSample]:
    if image_rgb.ndim != 3 or image_rgb.shape[2] != 3:
        raise ValueError("Expected an RGB image array with three channels.")

    working_image = resize_for_analysis(image_rgb)
    pixels = working_image.reshape(-1, 3).astype(np.uint8)
    quantized_pixels = (pixels // 32) * 32
    unique_colors, counts = np.unique(quantized_pixels, axis=0, return_counts=True)

    if counts.size == 0:
        raise ValueError("Unable to detect colors in the provided image.")

    order = np.argsort(counts)[::-1]
    total_pixels = int(counts.sum())
    samples: list[ColorSample] = []

    for index in order[: max(1, top_n)]:
        rgb = tuple(int(value) for value in unique_colors[index])
        percentage = round((int(counts[index]) / total_pixels) * 100.0, 2)
        samples.append(
            ColorSample(
                name=closest_color_name(rgb),
                rgb=rgb,
                hex_code=rgb_to_hex(rgb),
                percentage=percentage,
            )
        )

    return samples


def detect_dominant_color(image_rgb: np.ndarray, top_n: int = 5) -> tuple[ColorSample, list[ColorSample]]:
    samples = detect_top_colors(image_rgb, top_n=top_n)
    return samples[0], samples