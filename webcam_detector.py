from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

import cv2
from PIL import Image, ImageTk

from color_utils import ColorSample, detect_dominant_color, format_rgb
from history import save_detection

try:
    _THUMB_RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    _THUMB_RESAMPLE = Image.LANCZOS


class WebcamDetectionWindow:
    def __init__(self, parent: tk.Tk) -> None:
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("ColorSense | Webcam Detection")
        self.window.configure(bg="#0f172a")
        self.window.geometry("1100x720")
        self.window.minsize(960, 640)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.bind("<KeyPress-q>", self._handle_quit_key)
        self.window.bind("<KeyPress-Q>", self._handle_quit_key)

        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            messagebox.showerror(
                "Webcam unavailable",
                "No webcam could be opened. Please check your camera permissions or device connection.",
                parent=self.window,
            )
            self.window.destroy()
            return

        self.running = True
        self.frame_index = 0
        self.sample_interval = 12
        self.latest_color: ColorSample | None = None
        self._frame_photo: ImageTk.PhotoImage | None = None

        self._build_interface()
        self.window.after(20, self._update_frame)

    def _build_interface(self) -> None:
        header = tk.Frame(self.window, bg="#0f172a")
        header.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(
            header,
            text="Live Webcam Detection",
            bg="#0f172a",
            fg="#f8fafc",
            font=("Segoe UI", 24, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Press Q to exit webcam mode. The app samples the feed and updates the dominant color in real time.",
            bg="#0f172a",
            fg="#94a3b8",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        body = tk.Frame(self.window, bg="#0f172a")
        body.pack(fill="both", expand=True, padx=24, pady=16)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        video_card = tk.Frame(body, bg="#111827", highlightbackground="#334155", highlightthickness=1)
        video_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        video_card.grid_rowconfigure(0, weight=1)
        video_card.grid_columnconfigure(0, weight=1)

        self.video_label = tk.Label(
            video_card,
            text="Waiting for camera feed...",
            bg="#111827",
            fg="#94a3b8",
            font=("Segoe UI", 13),
        )
        self.video_label.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        details_card = tk.Frame(body, bg="#111827", highlightbackground="#334155", highlightthickness=1)
        details_card.grid(row=0, column=1, sticky="nsew")
        details_card.grid_columnconfigure(0, weight=1)

        tk.Label(
            details_card,
            text="Current Detection",
            bg="#111827",
            fg="#f8fafc",
            font=("Segoe UI", 16, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 8))

        self.color_canvas = tk.Canvas(details_card, width=220, height=160, bg="#0f172a", highlightthickness=0)
        self.color_canvas.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
        self.color_canvas.create_rectangle(8, 8, 212, 152, fill="#1d4ed8", outline="#38bdf8", width=2)

        self.name_label = self._build_value_label(details_card, 2, "Color Name", "--")
        self.rgb_label = self._build_value_label(details_card, 3, "RGB", "--")
        self.hex_label = self._build_value_label(details_card, 4, "HEX", "--")
        self.percentage_label = self._build_value_label(details_card, 5, "Coverage", "--")

        tk.Label(
            details_card,
            text="Top Five Colors",
            bg="#111827",
            fg="#f8fafc",
            font=("Segoe UI", 14, "bold"),
        ).grid(row=6, column=0, sticky="w", padx=18, pady=(16, 8))

        self.palette_rows: list[tuple[tk.Canvas, tk.Label]] = []
        for row_index in range(5):
            row_frame = tk.Frame(details_card, bg="#111827")
            row_frame.grid(row=7 + row_index, column=0, sticky="ew", padx=18, pady=4)
            row_frame.grid_columnconfigure(1, weight=1)

            swatch = tk.Canvas(row_frame, width=24, height=24, bg="#111827", highlightthickness=0)
            swatch.grid(row=0, column=0, padx=(0, 10))
            swatch.create_rectangle(2, 2, 22, 22, fill="#334155", outline="#64748b")

            label = tk.Label(
                row_frame,
                text="-",
                anchor="w",
                justify="left",
                bg="#111827",
                fg="#cbd5e1",
                font=("Segoe UI", 10),
            )
            label.grid(row=0, column=1, sticky="ew")
            self.palette_rows.append((swatch, label))

        button_row = tk.Frame(details_card, bg="#111827")
        button_row.grid(row=12, column=0, sticky="ew", padx=18, pady=(20, 18))
        button_row.grid_columnconfigure(0, weight=1)
        button_row.grid_columnconfigure(1, weight=1)

        self.stop_button = self._build_action_button(button_row, "Stop Webcam", self.close)
        self.stop_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.refresh_button = self._build_action_button(button_row, "Keep Watching", lambda: None)
        self.refresh_button.grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _build_value_label(self, parent: tk.Widget, row: int, heading: str, value: str) -> tk.Label:
        container = tk.Frame(parent, bg="#111827")
        container.grid(row=row, column=0, sticky="ew", padx=18, pady=4)
        container.grid_columnconfigure(0, weight=1)

        tk.Label(container, text=heading, bg="#111827", fg="#94a3b8", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        label = tk.Label(container, text=value, bg="#111827", fg="#f8fafc", font=("Segoe UI", 13, "bold"))
        label.grid(row=1, column=0, sticky="w", pady=(2, 0))
        return label

    def _build_action_button(self, parent: tk.Widget, text: str, command) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg="#38bdf8",
            fg="#082f49",
            activebackground="#0ea5e9",
            activeforeground="#f8fafc",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=10,
            cursor="hand2",
        )

    def _handle_quit_key(self, _event) -> None:
        self.close()

    def _update_palette(self, top_colors: list[ColorSample]) -> None:
        for index, (swatch, label) in enumerate(self.palette_rows):
            if index < len(top_colors):
                color = top_colors[index]
                swatch.delete("all")
                swatch.create_rectangle(2, 2, 22, 22, fill=color.hex_code, outline="#64748b")
                label.configure(text=f"{color.name}  |  {format_rgb(color.rgb)}  |  {color.hex_code}  |  {color.percentage:.2f}%")
            else:
                swatch.delete("all")
                swatch.create_rectangle(2, 2, 22, 22, fill="#334155", outline="#64748b")
                label.configure(text="-")

    def _update_frame(self) -> None:
        if not self.running or not self.window.winfo_exists():
            return

        success, frame_bgr = self.capture.read()
        if not success:
            messagebox.showerror(
                "Camera Error",
                "The webcam feed could not be read. The window will close.",
                parent=self.window,
            )
            self.close()
            return

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        display_image = Image.fromarray(frame_rgb)
        display_image.thumbnail((640, 480), _THUMB_RESAMPLE)
        self._frame_photo = ImageTk.PhotoImage(display_image)
        self.video_label.configure(image=self._frame_photo, text="")
        self.video_label.image = self._frame_photo

        if self.frame_index % self.sample_interval == 0:
            dominant_color, top_colors = detect_dominant_color(frame_rgb, top_n=5)
            self.latest_color = dominant_color
            self._update_palette(top_colors)
            self.color_canvas.delete("all")
            self.color_canvas.create_rectangle(8, 8, 212, 152, fill=dominant_color.hex_code, outline="#38bdf8", width=2)
            self.name_label.configure(text=dominant_color.name)
            self.rgb_label.configure(text=format_rgb(dominant_color.rgb))
            self.hex_label.configure(text=dominant_color.hex_code)
            self.percentage_label.configure(text=f"{dominant_color.percentage:.2f}%")
            save_detection("Webcam", dominant_color.name, dominant_color.rgb, dominant_color.hex_code, dominant_color.percentage)

        self.frame_index += 1
        self.window.after(30, self._update_frame)

    def close(self) -> None:
        if not getattr(self, "running", False):
            return

        self.running = False
        if getattr(self, "capture", None) is not None and self.capture.isOpened():
            self.capture.release()
        if self.window.winfo_exists():
            self.window.destroy()
