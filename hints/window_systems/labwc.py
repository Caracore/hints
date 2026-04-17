"""labwc window system for Raspberry Pi OS.

labwc is the default Wayland compositor on newer PiOS releases (Trixie+).
Since labwc has no IPC, we use AT-SPI to get focused window information.
This approach works for any wlroots-based compositor lacking a dedicated IPC.
"""

from gi import require_version

require_version("Atspi", "2.0")
from gi.repository import Atspi

from hints.window_systems.window_system import WindowSystem


class Labwc(WindowSystem):
    """labwc compositor window system (AT-SPI based)."""

    def __init__(self):
        super().__init__()
        self._active_window_info = self._find_active_window()

    def _find_active_window(self) -> dict | None:
        """Find the active window using AT-SPI accessibility tree.

        First tries to find a window with the ACTIVE state. If labwc
        does not report ACTIVE (common on PiOS), falls back to the
        largest SHOWING frame window that is not a panel or dock.

        :return: Dict with window info or None.
        """
        desktop = Atspi.get_desktop(0)
        candidates: list[dict] = []

        for app_idx in range(desktop.get_child_count()):
            app = desktop.get_child_at_index(app_idx)
            if app is None:
                continue
            for win_idx in range(app.get_child_count()):
                window = app.get_child_at_index(win_idx)
                if window is None:
                    continue
                try:
                    state_set = window.get_state_set()
                    if not state_set:
                        continue

                    extents = window.get_extents(Atspi.CoordType.SCREEN)
                    info = {
                        "x": extents.x,
                        "y": extents.y,
                        "width": extents.width,
                        "height": extents.height,
                        "pid": window.get_process_id(),
                        "name": app.get_name() or "",
                    }

                    # Prefer window with ACTIVE state (works on some compositors)
                    if state_set.contains(Atspi.StateType.ACTIVE):
                        return info

                    # Collect SHOWING frame windows as fallback candidates
                    if (
                        state_set.contains(Atspi.StateType.SHOWING)
                        and window.get_role() == Atspi.Role.FRAME
                        and extents.width > 0
                        and extents.height > 0
                    ):
                        candidates.append(info)
                except Exception:
                    continue

        if not candidates:
            return None

        # Pick the largest visible frame (by area), excluding panels/docks
        candidates.sort(
            key=lambda c: c["width"] * c["height"], reverse=True
        )
        return candidates[0]

    @property
    def window_system_name(self) -> str:
        """Get the name of the window system.

        :return: The window system name.
        """
        return "labwc"

    @property
    def focused_window_extents(self) -> tuple[int, int, int, int]:
        """Get active window extents.

        :return: Active window extents (x, y, width, height).
        """
        if self._active_window_info:
            return (
                self._active_window_info["x"],
                self._active_window_info["y"],
                self._active_window_info["width"],
                self._active_window_info["height"],
            )
        return (0, 0, 0, 0)

    @property
    def focused_window_pid(self) -> int:
        """Get Process ID corresponding to the focused window.

        :return: Process ID of focused window.
        """
        if self._active_window_info:
            return self._active_window_info["pid"]
        return 0

    @property
    def focused_applicaiton_name(self) -> str:
        """Get focused application name.

        :return: Focused application name.
        """
        if self._active_window_info:
            return self._active_window_info["name"]
        return ""
