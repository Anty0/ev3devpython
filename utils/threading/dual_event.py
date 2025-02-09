from threading import Event, Lock


class DualEvent:
    def __init__(self):
        self._lock = Lock()
        self._event = Event()
        self._inverted_event = Event()
        self._inverted_event.set()

    def is_set(self):
        with self._lock:
            return self._event.is_set()

    def set(self):
        with self._lock:
            self._event.set()
            self._inverted_event.clear()

    def clear(self):
        with self._lock:
            self._event.clear()
            self._inverted_event.set()

    def wait(self, timeout=None):
        return self.wait_set(timeout=timeout)

    def wait_set(self, timeout=None):
        return self._event.wait(timeout)

    def wait_clear(self, timeout=None):
        return self._inverted_event.wait(timeout)
