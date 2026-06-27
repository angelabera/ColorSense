from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from color_utils import ColorSample, format_rgb
from history import HISTORY_FILE, clear_history, export_history, ensure_history_file, load_history, save_detection
from image_detector import analyze_image_file
from webcam_detector import WebcamDetectionWindow

try:
    _THUMB_RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    _THUMB_RESAMPLE = Image.LANCZOS


class ColorSenseApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        ensure_history_file()
        self.title("ColorSense - Smart Color Detection App")
        self.geometry("1180x760")
        self.minsize(1000, 680)
        self.configure(bg="#0f172a")

        self._setup_style()
        self._build_home_screen()

    def _setup_style(self) -> None:
        self.option_add("*Font", ("Segoe UI", 10))

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background="#111827",
            fieldbackground="#111827",
            foreground="#e2e8f0",
            rowheight=28,
            bordercolor="#334155",
            lightcolor="#334155",
            darkcolor="#334155",
        )
        style.configure(
            "Treeview.Heading",
            background="#1e293b",
            foreground="#f8fafc",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Treeview", background=[("selected", "#0f766e")], foreground=[("selected", "#ffffff")])

    def _build_home_screen(self) -> None:
        root = tk.Frame(self, bg="#0f172a")
        root.pack(fill="both", expand=True)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)

        left_panel = tk.Frame(root, bg="#0f172a")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(36, 18), pady=36)
        left_panel.grid_rowconfigure(1, weight=1)

        tk.Label(left_panel, text="ColorSense", bg="#0f172a", fg="#38bdf8", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(
            left_panel,
            text="Smart Color Detection App",
            bg="#0f172a",
            fg="#f8fafc",
            font=("Segoe UI", 30, "bold"),
            justify="left",
            wraplength=560,
        ).pack(anchor="w", pady=(10, 8))
        tk.Label(
            left_panel,
            text="Detect dominant colors from images or a live webcam feed, review your history, and export the results with a clean dark-themed interface.",
            bg="#0f172a",
            fg="#94a3b8",
            font=("Segoe UI", 12),
            justify="left",
            wraplength=560,
        ).pack(anchor="w", pady=(0, 22))

        stats_frame = tk.Frame(left_panel, bg="#111827", highlightbackground="#334155", highlightthickness=1)
        stats_frame.pack(fill="x", pady=(0, 18))
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)

        self._build_stat_card(stats_frame, 0, "Image Analysis", "Upload JPG, JPEG, or PNG files")
        self._build_stat_card(stats_frame, 1, "Live Webcam", "Track colors in real time with OpenCV")

        button_frame = tk.Frame(left_panel, bg="#0f172a")
        button_frame.pack(fill="x", pady=(8, 0))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        self._build_main_button(button_frame, "Detect Color from Image", self.open_image_detector).grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 12))
        self._build_main_button(button_frame, "Detect Color from Webcam", self.open_webcam_detector).grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 12))
        self._build_main_button(button_frame, "View Detection History", self.open_history_window).grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 12))
        self._build_main_button(button_frame, "Exit", self.destroy, accent="#ef4444", accent_active="#dc2626").grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 12))

        right_panel = tk.Frame(root, bg="#0f172a")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(18, 36), pady=36)
        right_panel.grid_rowconfigure(0, weight=1)

        hero_card = tk.Frame(right_panel, bg="#111827", highlightbackground="#334155", highlightthickness=1)
        hero_card.pack(fill="both", expand=True)
        hero_card.grid_columnconfigure(0, weight=1)

        tk.Label(hero_card, text="Feature Highlights", bg="#111827", fg="#f8fafc", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        feature_texts = [
            ("Dominant color detection", "Calculates the closest named color, RGB value, HEX code, and coverage percentage."),
            ("Top five palette", "Displays multiple major colors from the image for a richer summary."),
            ("History tracking", "Stores every detection in history.csv and lets you clear or export it."),
            ("Utilities", "Copy HEX codes and save the detected color as a PNG swatch."),
        ]

        for index, (title, description) in enumerate(feature_texts, start=1):
            feature_card = tk.Frame(hero_card, bg="#0f172a", highlightbackground="#334155", highlightthickness=1)
            feature_card.grid(row=index, column=0, sticky="ew", padx=20, pady=10)
            feature_card.grid_columnconfigure(1, weight=1)

            accent = tk.Canvas(feature_card, width=16, height=16, bg="#0f172a", highlightthickness=0)
            accent.grid(row=0, column=0, rowspan=2, padx=14, pady=14)
            accent.create_oval(2, 2, 14, 14, fill="#38bdf8", outline="#38bdf8")

            tk.Label(
                feature_card,
                text=title,
                bg="#0f172a",
                fg="#f8fafc",
                font=("Segoe UI", 11, "bold"),
                anchor="w",
                justify="left",
                wraplength=360,
            ).grid(row=0, column=1, sticky="w", padx=(0, 14), pady=(12, 0))
            tk.Label(
                feature_card,
                text=description,
                bg="#0f172a",
                fg="#94a3b8",
                font=("Segoe UI", 10),
                anchor="w",
                justify="left",
                wraplength=360,
            ).grid(row=1, column=1, sticky="w", padx=(0, 14), pady=(2, 12))

        footer = tk.Label(right_panel, text=f"History file: {HISTORY_FILE.name}    |    Q closes webcam mode", bg="#0f172a", fg="#64748b", font=("Segoe UI", 9))
        footer.pack(anchor="e", pady=(10, 0))

    def _build_stat_card(self, parent: tk.Widget, column: int, title: str, description: str) -> None:
        card = tk.Frame(parent, bg="#111827")
        card.grid(row=0, column=column, sticky="ew", padx=12, pady=12)
        card.grid_columnconfigure(0, weight=1)

        tk.Label(card, text=title, bg="#111827", fg="#38bdf8", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 4))
        tk.Label(card, text=description, bg="#111827", fg="#e2e8f0", font=("Segoe UI", 10), wraplength=250, justify="left").grid(row=1, column=0, sticky="w", padx=14, pady=(0, 14))

    def _build_main_button(self, parent: tk.Widget, text: str, command, accent: str = "#38bdf8", accent_active: str = "#0ea5e9") -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=accent,
            fg="#082f49",
            activebackground=accent_active,
            activeforeground="#f8fafc",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=16,
            pady=14,
            cursor="hand2",
        )

    def open_image_detector(self) -> None:
        ImageDetectionWindow(self)

    def open_webcam_detector(self) -> None:
        WebcamDetectionWindow(self)

    def open_history_window(self) -> None:
        HistoryWindow(self)


class ImageDetectionWindow:
    def __init__(self, parent: tk.Tk) -> None:
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("ColorSense | Image Detection")
        self.window.configure(bg="#0f172a")
        self.window.geometry("1180x780")
        self.window.minsize(1020, 700)
        self.window.transient(parent)

        self.selected_path: str | None = None
        self.image_photo: ImageTk.PhotoImage | None = None
        self.current_detection: dict[str, object] | None = None

        self._build_interface()

    def _build_interface(self) -> None:
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        header = tk.Frame(self.window, bg="#0f172a")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)

        tk.Label(header, text="Image Color Detection", bg="#0f172a", fg="#f8fafc", font=("Segoe UI", 24, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(
            header,
            text="Upload an image to detect the dominant color, preview the palette, copy the HEX code, or save the detected color as a PNG.",
            bg="#0f172a",
            fg="#94a3b8",
            font=("Segoe UI", 10),
            wraplength=840,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        body = tk.Frame(self.window, bg="#0f172a")
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        preview_card = tk.Frame(body, bg="#111827", highlightbackground="#334155", highlightthickness=1)
        preview_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        preview_card.grid_rowconfigure(1, weight=1)
        preview_card.grid_columnconfigure(0, weight=1)

        controls = tk.Frame(preview_card, bg="#111827")
        controls.grid(row=0, column=0, sticky="ew", padx=18, pady=18)
        controls.grid_columnconfigure(0, weight=1)
        controls.grid_columnconfigure(1, weight=1)
        controls.grid_columnconfigure(2, weight=1)

        self._build_small_button(controls, "Upload Image", self.choose_image).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._build_small_button(controls, "Copy HEX", self.copy_hex).grid(row=0, column=1, sticky="ew", padx=8)
        self._build_small_button(controls, "Save Color as PNG", self.save_color_png).grid(row=0, column=2, sticky="ew", padx=(8, 0))

        self.image_label = tk.Label(preview_card, text="No image selected yet", bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 13), anchor="center", justify="center")
        self.image_label.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))

        detail_card = tk.Frame(body, bg="#111827", highlightbackground="#334155", highlightthickness=1)
        detail_card.grid(row=0, column=1, sticky="nsew")
        detail_card.grid_columnconfigure(0, weight=1)

        tk.Label(detail_card, text="Detection Results", bg="#111827", fg="#f8fafc", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 10))

        self.color_preview_canvas = tk.Canvas(detail_card, width=220, height=160, bg="#0f172a", highlightthickness=0)
        self.color_preview_canvas.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 16))
        self.color_preview_canvas.create_rectangle(8, 8, 212, 152, fill="#334155", outline="#64748b", width=2)

        self.name_value = self._build_info_row(detail_card, 2, "Color Name")
        self.rgb_value = self._build_info_row(detail_card, 3, "RGB")
        self.hex_value = self._build_info_row(detail_card, 4, "HEX")
        self.coverage_value = self._build_info_row(detail_card, 5, "Coverage")
        self.size_value = self._build_info_row(detail_card, 6, "Image Size")

        tk.Label(detail_card, text="Top Five Colors", bg="#111827", fg="#f8fafc", font=("Segoe UI", 14, "bold")).grid(row=7, column=0, sticky="w", padx=18, pady=(16, 8))

        self.palette_rows: list[tuple[tk.Canvas, tk.Label]] = []
        for row_index in range(5):
            row_frame = tk.Frame(detail_card, bg="#111827")
            row_frame.grid(row=8 + row_index, column=0, sticky="ew", padx=18, pady=4)
            row_frame.grid_columnconfigure(1, weight=1)

            swatch = tk.Canvas(row_frame, width=24, height=24, bg="#111827", highlightthickness=0)
            swatch.grid(row=0, column=0, padx=(0, 10))
            swatch.create_rectangle(2, 2, 22, 22, fill="#334155", outline="#64748b")

            label = tk.Label(row_frame, text="-", bg="#111827", fg="#cbd5e1", font=("Segoe UI", 10), anchor="w", justify="left")
            label.grid(row=0, column=1, sticky="ew")
            self.palette_rows.append((swatch, label))

        bottom = tk.Frame(detail_card, bg="#111827")
        bottom.grid(row=13, column=0, sticky="ew", padx=18, pady=(18, 18))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)

        self._build_small_button(bottom, "Export History", self.export_history).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._build_small_button(bottom, "Close", self.window.destroy).grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _build_small_button(self, parent: tk.Widget, text: str, command) -> tk.Button:
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

    def _build_info_row(self, parent: tk.Widget, row: int, title: str) -> tk.Label:
        container = tk.Frame(parent, bg="#111827")
        container.grid(row=row, column=0, sticky="ew", padx=18, pady=4)
        container.grid_columnconfigure(0, weight=1)

        tk.Label(container, text=title, bg="#111827", fg="#94a3b8", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        label = tk.Label(container, text="--", bg="#111827", fg="#f8fafc", font=("Segoe UI", 13, "bold"))
        label.grid(row=1, column=0, sticky="w", pady=(2, 0))
        return label

    def choose_image(self) -> None:
        file_path = filedialog.askopenfilename(
            parent=self.window,
            title="Select an image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("All files", "*.*"),
            ],
        )
        if not file_path:
            return

        try:
            analysis = analyze_image_file(file_path, top_n=5)
        except ValueError as error:
            messagebox.showerror("Invalid image", str(error), parent=self.window)
            return
        except Exception as error:
            messagebox.showerror("Detection error", f"Unable to analyze the image:\n{error}", parent=self.window)
            return

        self.selected_path = file_path
        self.current_detection = analysis
        self._render_analysis(analysis)

        dominant: ColorSample = analysis["dominant"]  # type: ignore[assignment]
        save_detection("Image", dominant.name, dominant.rgb, dominant.hex_code, dominant.percentage)

    def _render_analysis(self, analysis: dict[str, object]) -> None:
        preview_image: Image.Image = analysis["image_preview"]  # type: ignore[assignment]
        display_image = preview_image.copy()
        display_image.thumbnail((660, 520), _THUMB_RESAMPLE)
        self.image_photo = ImageTk.PhotoImage(display_image)
        self.image_label.configure(image=self.image_photo, text="")
        self.image_label.image = self.image_photo

        dominant: ColorSample = analysis["dominant"]  # type: ignore[assignment]
        top_colors: list[ColorSample] = analysis["top_colors"]  # type: ignore[assignment]

        self.color_preview_canvas.delete("all")
        self.color_preview_canvas.create_rectangle(8, 8, 212, 152, fill=dominant.hex_code, outline="#38bdf8", width=2)
        self.name_value.configure(text=dominant.name)
        self.rgb_value.configure(text=format_rgb(dominant.rgb))
        self.hex_value.configure(text=dominant.hex_code)
        self.coverage_value.configure(text=f"{dominant.percentage:.2f}%")
        self.size_value.configure(text=f"{analysis['width']} x {analysis['height']}")

        for index, (swatch, label) in enumerate(self.palette_rows):
            if index < len(top_colors):
                color = top_colors[index]
                swatch.delete("all")
                swatch.create_rectangle(2, 2, 22, 22, fill=color.hex_code, outline="#64748b")
                label.configure(text=f"{index + 1}. {color.name}  |  {format_rgb(color.rgb)}  |  {color.hex_code}  |  {color.percentage:.2f}%")
            else:
                swatch.delete("all")
                swatch.create_rectangle(2, 2, 22, 22, fill="#334155", outline="#64748b")
                label.configure(text="-")

    def copy_hex(self) -> None:
        if not self.current_detection:
            messagebox.showinfo("Copy HEX", "Detect a color first.", parent=self.window)
            return

        dominant: ColorSample = self.current_detection["dominant"]  # type: ignore[assignment]
        self.window.clipboard_clear()
        self.window.clipboard_append(dominant.hex_code)
        self.window.update()
        messagebox.showinfo("Copied", f"{dominant.hex_code} copied to clipboard.", parent=self.window)

    def save_color_png(self) -> None:
        if not self.current_detection:
            messagebox.showinfo("Save Color", "Detect a color first.", parent=self.window)
            return

        dominant: ColorSample = self.current_detection["dominant"]  # type: ignore[assignment]
        file_path = filedialog.asksaveasfilename(
            parent=self.window,
            title="Save detected color as PNG",
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            initialfile=f"{dominant.name.lower().replace(' ', '_')}_color.png",
        )
        if not file_path:
            return

        Image.new("RGB", (512, 512), dominant.rgb).save(file_path)
        messagebox.showinfo("Saved", f"Detected color saved to:\n{file_path}", parent=self.window)

    def export_history(self) -> None:
        destination = filedialog.asksaveasfilename(
            parent=self.window,
            title="Export history to CSV",
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv")],
            initialfile="colorsense_history.csv",
        )
        if not destination:
            return

        export_history(destination)
        messagebox.showinfo("Export complete", f"History exported to:\n{destination}", parent=self.window)


class HistoryWindow:
    def __init__(self, parent: tk.Tk) -> None:
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("ColorSense | Detection History")
        self.window.configure(bg="#0f172a")
        self.window.geometry("1120x700")
        self.window.minsize(980, 620)
        self.window.transient(parent)

        self._build_interface()
        self.refresh_history()

    def _build_interface(self) -> None:
        self.window.grid_rowconfigure(2, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        header = tk.Frame(self.window, bg="#0f172a")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)

        tk.Label(header, text="Detection History", bg="#0f172a", fg="#f8fafc", font=("Segoe UI", 24, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(
            header,
            text="Every detection is stored in history.csv. You can refresh, export, or clear the log from here.",
            bg="#0f172a",
            fg="#94a3b8",
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        toolbar = tk.Frame(self.window, bg="#0f172a")
        toolbar.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        for column in range(4):
            toolbar.grid_columnconfigure(column, weight=1)

        self._build_toolbar_button(toolbar, "Refresh", self.refresh_history).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._build_toolbar_button(toolbar, "Export CSV", self.export_history).grid(row=0, column=1, sticky="ew", padx=8)
        self._build_toolbar_button(toolbar, "Clear History", self.clear_history).grid(row=0, column=2, sticky="ew", padx=8)
        self._build_toolbar_button(toolbar, "Close", self.window.destroy).grid(row=0, column=3, sticky="ew", padx=(8, 0))

        table_card = tk.Frame(self.window, bg="#111827", highlightbackground="#334155", highlightthickness=1)
        table_card.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 24))
        table_card.grid_rowconfigure(0, weight=1)
        table_card.grid_columnconfigure(0, weight=1)

        columns = ("Date", "Time", "Source", "Color Name", "RGB", "HEX", "Percentage")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 12), pady=12)
        self.tree.configure(yscrollcommand=scrollbar.set)

        for column in columns:
            self.tree.heading(column, text=column)

        widths = {
            "Date": 110,
            "Time": 90,
            "Source": 110,
            "Color Name": 150,
            "RGB": 160,
            "HEX": 110,
            "Percentage": 110,
        }
        for column, width in widths.items():
            self.tree.column(column, width=width, anchor="center", stretch=True)

    def _build_toolbar_button(self, parent: tk.Widget, text: str, command) -> tk.Button:
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

    def refresh_history(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in load_history():
            self.tree.insert(
                "",
                "end",
                values=(
                    row.get("Date", ""),
                    row.get("Time", ""),
                    row.get("Source", ""),
                    row.get("Color Name", ""),
                    row.get("RGB", ""),
                    row.get("HEX", ""),
                    row.get("Percentage", ""),
                ),
            )

    def export_history(self) -> None:
        destination = filedialog.asksaveasfilename(
            parent=self.window,
            title="Export history to CSV",
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv")],
            initialfile="colorsense_history.csv",
        )
        if not destination:
            return

        export_history(destination)
        messagebox.showinfo("Export complete", f"History exported to:\n{destination}", parent=self.window)

    def clear_history(self) -> None:
        confirm = messagebox.askyesno(
            "Clear history",
            "This will remove every saved detection from history.csv. Continue?",
            parent=self.window,
        )
        if not confirm:
            return

        clear_history()
        self.refresh_history()
        messagebox.showinfo("History cleared", "The detection history has been reset.", parent=self.window)
