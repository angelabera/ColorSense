from __future__ import annotations

import csv
import shutil
from datetime import datetime
from pathlib import Path
from typing import Iterable

HISTORY_FILE = Path(__file__).with_name("history.csv")
HISTORY_HEADERS = ["Date", "Time", "Source", "Color Name", "RGB", "HEX", "Percentage"]


def ensure_history_file(history_path: str | Path | None = None) -> Path:
    path = Path(history_path) if history_path is not None else HISTORY_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as file_handle:
            writer = csv.writer(file_handle)
            writer.writerow(HISTORY_HEADERS)

    return path


def _rgb_to_string(rgb: Iterable[int]) -> str:
    red, green, blue = (int(value) for value in rgb)
    return f"({red}, {green}, {blue})"


def save_detection(
    source: str,
    color_name: str,
    rgb: Iterable[int],
    hex_code: str,
    percentage: float | None = None,
    history_path: str | Path | None = None,
) -> Path:
    path = ensure_history_file(history_path)
    timestamp = datetime.now()

    row = {
        "Date": timestamp.strftime("%Y-%m-%d"),
        "Time": timestamp.strftime("%H:%M:%S"),
        "Source": source,
        "Color Name": color_name,
        "RGB": _rgb_to_string(rgb),
        "HEX": hex_code,
        "Percentage": "" if percentage is None else f"{percentage:.2f}%",
    }

    with path.open("a", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=HISTORY_HEADERS)
        writer.writerow(row)

    return path


def load_history(history_path: str | Path | None = None) -> list[dict[str, str]]:
    path = ensure_history_file(history_path)
    with path.open("r", newline="", encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle)
        return list(reader)


def clear_history(history_path: str | Path | None = None) -> Path:
    path = ensure_history_file(history_path)
    with path.open("w", newline="", encoding="utf-8") as file_handle:
        writer = csv.writer(file_handle)
        writer.writerow(HISTORY_HEADERS)
    return path


def export_history(destination_path: str | Path, history_path: str | Path | None = None) -> Path:
    source_path = ensure_history_file(history_path)
    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination)
    return destination
