from utils.utils import crop_m


class RegulatorBase:
    def __init__(self, const_p: float = None, const_i: float = None, const_d: float = None, const_target: float = None,
                 getter_p: callable = None, getter_i: callable = None, getter_d: callable = None,
                 getter_target: callable = None):
        self.p = (lambda: const_p) if getter_p is None else getter_p
        self.i = (lambda: const_i) if getter_i is None else getter_i
        self.d = (lambda: const_d) if getter_d is None else getter_d
        self.target = (lambda: const_target) if getter_target is None else getter_target

        self.loop_count = 0
        self.last_error = 0
        self.last_derivative = 0
        self.last_integral = 0

    def reset(self):
        self.loop_count = 0
        self.last_error = 0
        self.last_derivative = 0
        self.last_integral = 0

    def regulate(self, input_val) -> float:
        self.loop_count += 1
        return 0


class ValueRegulator(RegulatorBase):
    def __init__(self, const_p: float = None, const_i: float = None, const_d: float = None, const_target: float = None,
                 getter_p=None, getter_i=None, getter_d=None, getter_target=None):
        RegulatorBase.__init__(self, const_p, const_i, const_d, const_target,
                               getter_p, getter_i, getter_d, getter_target)

    def regulate(self, input_val) -> float:
        RegulatorBase.regulate(self, input_val)

        target = self.target()
        error = target - input_val
        return self.regulate_error(error)

    def regulate_error(self, error) -> float:
        integral = float(0.5) * self.last_integral + error
        self.last_integral = integral

        derivative = error - self.last_error
        self.last_error = error
        self.last_derivative = derivative

        return self.p() * error + self.i() * integral + self.d() * derivative


class RangeRegulator(ValueRegulator):
    def __init__(self, min_input: float = 0, max_input: float = 100, const_p: float = None, const_i: float = None,
                 const_d: float = None, const_target: float = None, getter_p=None, getter_i=None, getter_d=None,
                 getter_target=None):
        ValueRegulator.__init__(self, const_p, const_i, const_d, const_target,
                                getter_p, getter_i, getter_d, getter_target)
        self.min_input = min_input
        self.max_input = max_input

    def regulate(self, input_val) -> float:
        RegulatorBase.regulate(self, input_val)

        input_val = crop_m(input_val, min_out=self.min_input, max_out=self.max_input)
        target = self.target()

        error = target - input_val
        if error != 0:
            max_error = min(abs(self.max_input - target), abs(self.min_input - target)) * 0.8
            error *= 100 / max_error

        return self.regulate_error(error)
