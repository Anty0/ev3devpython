# import threading
# from threading import Event

# from .program import RobotProgramController


class Behaviour:
    def on_take_control(self):
        pass

    def on_loose_control(self):
        pass

    def should_take_control(self) -> bool:
        pass

    def handle_loop(self):
        pass


class Behaviours:
    def __init__(self, behaviours):
        self.behaviours = behaviours
        self.last_behaviour = None

    def force_loose_control(self):
        if self.last_behaviour is not None:
            self.last_behaviour.on_loose_control()
            self.last_behaviour = None
        pass

    def _select_new_behaviour(self) -> Behaviour or None:
        for behaviour in self.behaviours:
            if behaviour.should_take_control():
                return behaviour
        return None

    def handle_loop(self):
        behaviour = self._select_new_behaviour()
        if behaviour != self.last_behaviour:
            if self.last_behaviour is not None:
                self.last_behaviour.on_loose_control()
            self.last_behaviour = behaviour
            if behaviour is not None:
                behaviour.on_take_control()

        if behaviour is not None:
            behaviour.handle_loop()


class MultiBehaviour(Behaviours):
    def __init__(self, behaviours):
        super().__init__(behaviours)

    def on_take_control(self):
        pass

    def on_loose_control(self):
        self.force_loose_control()

    def should_take_control(self) -> bool:
        for behaviour in self.behaviours:
            if not behaviour.should_take_control():
                return False
            return True

# class BehaviourController(RobotProgramController, Behaviours):
#     def __init__(self, robot_program, behaviours):
#         RobotProgramController.__init__(self, robot_program)
#         Behaviours.__init__(self, behaviours)
#
#         self.stop = False
#         self.exit_event = Event()
#         self.thread = threading.Thread(target=self._run, daemon=True)
#         self.thread.start()
#
#     def on_start(self):
#         pass
#
#     def _run(self):
#         try:
#             self.on_start()
#             while not self.stop_loop():
#                 self.handle_loop()
#             self.on_exit()
#         finally:
#             self.exit_event.set()
#
#     def on_exit(self):
#         pass
#
#     def stop_loop(self):
#         return self.stop
#
#     def request_exit(self):
#         self.stop = True
#
#     def wait_to_exit(self):
#         self.exit_event.wait()
