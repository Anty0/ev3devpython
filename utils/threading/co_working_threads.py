import time
from threading import Event, Thread, Lock

from utils.threading.dual_event import DualEvent


class ShareAccessInterface:
    def __init__(self, thread_name: str, threads, shared_data):
        self._thread_name = thread_name
        self._threads = threads
        self._shared_data = shared_data

    @property
    def name(self):
        return self._thread_name

    @property
    def data(self):
        return self._shared_data

    def request_resume(self, thread_name: str = None):
        self._threads.request_resume(thread_name)

    def request_pause(self, thread_name: str = None, wait_to_pause: bool = False):
        self._threads.request_pause(thread_name)
        if wait_to_pause:
            self._threads.wait_to_pause(thread_name)

    def should_run(self):
        return self._threads.run

    def _get_events(self):
        return self._threads.events[self._thread_name]

    def should_pause(self):
        return self._get_events().event_request_pause.is_set()

    def wait_resume(self, timeout: float = None, repeat_while_paused: callable = None):
        event_request_pause = self._get_events().event_request_pause
        event_paused = self._get_events().event_paused
        if repeat_while_paused is None:
            try:
                event_paused.set()
                return event_request_pause.wait(timeout=timeout)
            finally:
                event_paused.clear()

        if event_request_pause.is_set():
            try:
                event_paused.set()
                start_time = time.time()
                while event_request_pause.is_set():
                    if time.time() - start_time > timeout:
                        return False
                    repeat_while_paused()
            finally:
                event_paused.clear()
        return True


class Events:
    def __init__(self):
        self.event_stopped = Event()
        self.event_request_pause = Event()
        self.event_paused = DualEvent()
        self.event_stopped_or_paused = Event()

        self.event_stopped.set()
        self.event_stopped_or_paused.set()


class Threads:
    def __init__(self, shared_data: any, **starters: callable):
        self._lock = Lock()

        self.run = False
        self.starters = starters
        self.events = {}
        self.share_access_interfaces = {}
        self.running_threads = {}

        for name, starter in starters.items():
            self.events[name] = Events()
            self.share_access_interfaces[name] = ShareAccessInterface(name, self, shared_data)

    def start(self):
        with self._lock:
            self.run = True
            running_threads = self.running_threads
            for name in self.starters.keys():
                if name not in running_threads:
                    running_threads[name] = thread = Thread(target=lambda: self._handle_thread_start(name),
                                                            name=name + 'Thread', daemon=True)
                    thread.start()

    def _handle_thread_start(self, name):
        thread_events = self.events[name]
        try:
            thread_events.event_stopped.clear()
            thread_events.event_request_pause.clear()
            thread_events.event_paused.clear()
            thread_events.event_stopped_or_paused.clear()

            self.starters[name](self.share_access_interfaces[name])
        finally:
            thread_events.event_stopped.set()
            thread_events.event_paused.clear()
            thread_events.event_stopped_or_paused.set()

            with self._lock:
                self.running_threads[name] = None

    def stop(self):
        with self._lock:
            self.run = False

    def request_pause(self, thread_name: str = None):
        if thread_name is not None:
            return self.events[thread_name].event_request_pause.set()

        for event in self.events.values():
            event.event_request_pause.set()

    def request_resume(self, thread_name: str = None):
        if thread_name is not None:
            return self.events[thread_name].event_request_pause.clear()

        for event in self.events.values():
            event.event_request_pause.clear()

    def _wait_to_event(self, event_name: str, method_name: str = 'wait', thread_name: str = None,
                       timeout: float = None):
        if thread_name is not None:
            return getattr(getattr(self.events[thread_name], event_name), method_name)(timeout=timeout)

        start_time = time.time() if timeout is not None else None
        for thread_events in self.events.values():
            next_timeout = None if timeout is None else timeout - (time.time() - start_time)
            if (next_timeout is not None and next_timeout < 0) \
                    or not getattr(getattr(thread_events, event_name), method_name)(timeout=next_timeout):
                return False

        return True

    def wait_to_resume(self, thread_name: str = None, timeout: float = None):
        return self._wait_to_event('event_paused', method_name='wait_clear',
                                   thread_name=thread_name, timeout=timeout)

    def wait_to_pause(self, thread_name: str = None, timeout: float = None):
        return self._wait_to_event('event_paused', method_name='wait_set',
                                   thread_name=thread_name, timeout=timeout)

    def wait_to_stop(self, thread_name: str = None, timeout: float = None):
        return self._wait_to_event('event_stopped', thread_name=thread_name, timeout=timeout)

    def wait_to_stop_or_pause(self, thread_name: str = None, timeout: float = None):
        return self._wait_to_event('event_stopped_or_paused', thread_name=thread_name, timeout=timeout)


class ThreadsController:
    def __init__(self, shared_data: any, **starters: callable):
        self._threads = Threads(shared_data, **starters)

    def start(self):
        self._threads.start()

    def stop(self):
        self._threads.stop()

    def request_pause(self, thread_name: str = None):
        self._threads.request_pause(thread_name)

    def request_resume(self, thread_name: str = None):
        self._threads.request_resume(thread_name)

    def wait_to_resume(self, thread_name: str = None, timeout: float = None):
        return self._threads.wait_to_resume(thread_name, timeout)

    def wait_to_pause(self, thread_name: str = None, timeout: float = None):
        return self._threads.wait_to_pause(thread_name, timeout)

    def wait_to_stop(self, thread_name: str = None, timeout: float = None):
        return self._threads.wait_to_stop(thread_name, timeout)

    def wait_to_stop_or_pause(self, thread_name: str = None, timeout: float = None):
        return self._threads.wait_to_stop_or_pause(thread_name, timeout)
