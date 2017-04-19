import time
from threading import Thread, Event

from .utils import wait_to_cycle_time


class Action:
    def actual_progress(self) -> float:
        pass

    def on_start(self):
        pass

    def handle_loop(self, elapsed_time, progress_error):
        pass

    def on_stop(self):
        pass


class Coordinator:
    def __init__(self, actions):
        self._actions = actions
        self._start_time = time.time()

    def on_start(self):
        for action in self._actions:
            action.on_start()

        self._start_time = time.time()

    def handle_loop(self):
        if len(self._actions) == 0:
            return

        actual = []
        for action in self._actions:
            actual.append(action.actual_progress())

        target = []
        for i in range(len(self._actions)):
            total = 0
            count = 0
            for j in range(len(actual)):
                if j == i or actual[j] is None:
                    continue
                total += actual[j]
                count += 1
            target.append(total / count if count != 0 else None)

        loop_time = time.time()
        elapsed_time = loop_time - self._start_time
        for i in range(len(self._actions)):
            diff = target[i] - actual[i] if target[i] is not None and actual[i] is not None else 0
            self._actions[i].handle_loop(elapsed_time, diff)

    def on_stop(self):
        for action in self._actions:
            action.on_stop()


class ThreadCoordinator(Thread, Coordinator):
    def __init__(self, actions, group=None, name=None, daemon=None):
        Thread.__init__(self, group=group, name=name, daemon=daemon)
        Coordinator.__init__(self, actions)
        self._request_stop = False
        self._stop_event = Event()

    def run(self):
        try:
            self.on_start()
            while not self._is_stop_loop():
                self.handle_loop()
            self.on_stop()
        finally:
            self._stop_event.set()

    def _is_stop_loop(self):
        return self._request_stop

    def stop(self):
        self._request_stop = True

    def wait_to_stop(self):
        self._stop_event.wait()


class CycleThreadCoordinator(ThreadCoordinator):
    def __init__(self, actions, cycle_time=0.01):
        ThreadCoordinator.__init__(self, actions)
        self._cycle_time = cycle_time
        self._last_time = self._start_time

    def on_start(self):
        ThreadCoordinator.on_start(self)
        self._last_time = self._start_time

    def handle_loop(self):
        ThreadCoordinator.handle_loop(self)
        self._last_time = wait_to_cycle_time(__name__, self._last_time, self._cycle_time)
