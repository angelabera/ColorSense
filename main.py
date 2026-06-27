from __future__ import annotations

from gui import ColorSenseApp
from history import ensure_history_file


def main() -> None:
    ensure_history_file()
    app = ColorSenseApp()
    app.mainloop()


if __name__ == "__main__":
    main()
