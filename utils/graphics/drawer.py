class Drawer:  # TODO: implement
    def clear(self):
        raise NotImplementedError()

    def line(self, x1, y1, x2, y2, fill='black', width=1.0):
        raise NotImplementedError()

    def oval(self, x1, y1, x2, y2, fill='black', width=1.0):
        raise NotImplementedError()

    def polygon(self, x1, y1, x2, y2, fill='black', width=1.0):
        raise NotImplementedError()

    def rectangle(self, x1, y1, x2, y2, fill='black', width=1.0):
        raise NotImplementedError()

    def text(self, x, y, anchor='center', fill='black', text=''):
        raise NotImplementedError()


class CanvasDrawer(Drawer):
    def __init__(self, canvas, tag=None):
        self._canvas = canvas
        self._tag = tag

    def clear(self):
        self._canvas.delete(self._tag if self._tag is not None else 'all')

    def line(self, x1, y1, x2, y2, fill='black', width=1.0):
        self._canvas.create_line(x1, y1, x2, y2, fill=fill, width=width, tags=self._tag)

    def oval(self, x1, y1, x2, y2, fill='black', width=1.0):
        self._canvas.create_oval(x1, y1, x2, y2, fill=fill, width=width, tags=self._tag)

    def polygon(self, x1, y1, x2, y2, fill='black', width=1.0):
        self._canvas.create_polygon(x1, y1, x2, y2, fill=fill, width=width, tags=self._tag)

    def rectangle(self, x1, y1, x2, y2, fill='black', width=1.0):
        self._canvas.create_rectangle(x1, y1, x2, y2, fill=fill, width=width, tags=self._tag)

    def text(self, x, y, anchor='center', fill='black', text=''):
        self._canvas.create_text(x, y, anchor=anchor, fill=fill, text=text)
