import time
from threading import Thread, Event


class CycleThread(Thread):
    def __init__(self, target: callable = None, sleep_time: float = None,
                 group=None, name=None, daemon=None):
        Thread.__init__(self, group=group, name=name, daemon=daemon)
        self._target = target
        self._sleep_time = sleep_time
        self._run = True
        self._event_started = Event()
        self._event_stopped = Event()

    def stop(self):
        self._run = False

    def wait_to_start(self, timeout=None):
        return self._event_started.wait(timeout)

    def wait_to_stop(self, timeout=None):
        return self._event_stopped.wait(timeout)

    def on_start(self):
        pass

    def cycle(self):
        if self._target is not None:
            self._target()

    def on_stop(self):
        pass

    def should_stop(self):
        return not self._run

    def run(self):
        try:
            self.on_start()
            self._event_started.set()
            while not self.should_stop():
                self.cycle()
                if self._sleep_time is not None:
                    time.sleep(self._sleep_time)
        finally:
            self._event_stopped.set()
            self.on_stop()
            del self._target
