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

        Iterates through all accessible applications and their windows
        to find the one with the ACTIVE state, then extracts its screen
        geometry, PID, and application name.

        :return: Dict with window info or None.
        """
        desktop = Atspi.get_desktop(0)
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
                    if state_set and state_set.contains(Atspi.StateType.ACTIVE):
                        extents = window.get_extents(Atspi.CoordType.SCREEN)
                        return {
                            "x": extents.x,
                            "y": extents.y,
                            "width": extents.width,
                            "height": extents.height,
                            "pid": window.get_process_id(),
                            "name": app.get_name() or "",
                        }
                except Exception:
                    continue
        return None

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
