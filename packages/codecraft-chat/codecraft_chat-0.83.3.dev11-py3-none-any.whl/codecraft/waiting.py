#!/usr/bin/env python

"""
Thread-based, killable spinner utility.

Use it like:

    from codecraft.waiting import WaitingSpinner

    spinner = WaitingSpinner("Waiting for LLM")
    spinner.start()
    ...  # long task
    spinner.stop()
"""

import threading
import time

from codecraft.utils import Spinner


class WaitingSpinner:
    """Background spinner that can be started/stopped safely."""

    def __init__(self, text: str = "Waiting for LLM", delay: float = 0.15):
        self.spinner = Spinner(text)
        self.delay = delay
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._spin, daemon=True)

    def _spin(self):
        while not self._stop_event.is_set():
            time.sleep(self.delay)
            self.spinner.step()
        self.spinner.end()

    def start(self):
        """Start the spinner in a background thread."""
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self):
        """Request the spinner to stop and wait briefly for the thread to exit."""
        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join(timeout=0.1)
        self.spinner.end()

    # Allow use as a context-manager
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()