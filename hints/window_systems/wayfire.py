"""Wayfire window system for Raspberry Pi OS.

Wayfire is the default Wayland compositor on PiOS Bookworm.
It provides an IPC socket for querying window information.
"""

import json
import os
import socket
import struct

from hints.window_systems.window_system import WindowSystem


class WayfireIPCError(Exception):
    """Raised when wayfire IPC communication fails."""


class Wayfire(WindowSystem):
    """Wayfire compositor window system."""

    def __init__(self):
        super().__init__()
        self._focused_view = self._get_focused_view()

    def _ipc_request(self, method: str) -> dict | list | None:
        """Send an IPC request to wayfire and return the parsed response.

        The wayfire IPC uses a Unix socket with length-prefixed JSON messages:
        [4 bytes LE uint32 length][JSON payload]

        :param method: The IPC method to call.
        :return: The parsed JSON response.
        """
        socket_path = os.getenv("WAYFIRE_SOCKET", "")
        if not socket_path:
            return None

        msg = json.dumps({"method": method}).encode("utf-8")

        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.settimeout(2.0)
                sock.connect(socket_path)
                sock.sendall(struct.pack("<I", len(msg)) + msg)

                length_data = b""
                while len(length_data) < 4:
                    chunk = sock.recv(4 - len(length_data))
                    if not chunk:
                        return None
                    length_data += chunk

                length = struct.unpack("<I", length_data)[0]
                response = b""
                while len(response) < length:
                    chunk = sock.recv(length - len(response))
                    if not chunk:
                        break
                    response += chunk

                return json.loads(response.decode("utf-8"))
        except (OSError, json.JSONDecodeError, struct.error):
            return None

    def _get_focused_view(self) -> dict | None:
        """Get the currently focused view from wayfire IPC.

        :return: The focused view dict or None.
        """
        views = self._ipc_request("window-rules/list-views")
        if isinstance(views, list):
            for view in views:
                if view.get("focused", False):
                    return view
        return None

    @property
    def window_system_name(self) -> str:
        """Get the name of the window system.

        :return: The window system name.
        """
        return "wayfire"

    @property
    def focused_window_extents(self) -> tuple[int, int, int, int]:
        """Get active window extents.

        :return: Active window extents (x, y, width, height).
        """
        if self._focused_view and "geometry" in self._focused_view:
            g = self._focused_view["geometry"]
            return (g["x"], g["y"], g["width"], g["height"])
        return (0, 0, 0, 0)

    @property
    def focused_window_pid(self) -> int:
        """Get Process ID corresponding to the focused window.

        :return: Process ID of focused window.
        """
        if self._focused_view:
            return self._focused_view.get("pid", 0)
        return 0

    @property
    def focused_applicaiton_name(self) -> str:
        """Get focused application name.

        :return: Focused application name.
        """
        if self._focused_view:
            return self._focused_view.get("app-id", "")
        return ""
