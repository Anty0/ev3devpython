class Size:
    def __init__(self, width: float, length: float, height: float, weight: float):
        self._width = width
        self._length = length
        self._height = height
        self._weight = weight

    @property
    def width(self):
        return self._width

    @property
    def length(self):
        return self._length

    @property
    def height(self):
        return self._height

    @property
    def weight(self):
        return self._weight

        # TODO: add some calculations
