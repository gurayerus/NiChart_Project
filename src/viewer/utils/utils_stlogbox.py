from datetime import datetime
from typing import List
import streamlit.delta_generator as dg


class StreamlitJobLogger:
    committed_box: dg.DeltaGenerator
    live_box: dg.DeltaGenerator
    committed_lines: List[str]
    live_buffer: str

    def __init__(self, committed_box: dg.DeltaGenerator, live_box: dg.DeltaGenerator) -> None:
        self.committed_box = committed_box
        self.live_box = live_box
        self.committed_lines = []
        self.live_buffer = ""

    def _timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def commit(self, text: str) -> None:
        """Commit the full text (e.g. job output) to permanent log."""
        for line in text.strip().splitlines():
            self.committed_lines.append(f"[{self._timestamp()}] {line}")
        self._refresh_committed()

    def info(self, msg: str) -> None:
        """Quick single-line commit."""
        self.committed_lines.append(f"[{self._timestamp()}] INFO: {msg}")
        self._refresh_committed()

    def error(self, msg: str) -> None:
        self.committed_lines.append(f"[{self._timestamp()}] ERROR: {msg}")
        self._refresh_committed()

    def update_live(self, live_text: str) -> None:
        """Update live log for current job polling result."""
        self.live_buffer = live_text
        self.live_box.code(self.live_buffer, language="log")

    def clear_live(self) -> None:
        self.live_buffer = ""
        self.live_box.empty()

    def _refresh_committed(self) -> None:
        self.committed_box.code("\n".join(self.committed_lines), language="log")
