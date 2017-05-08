class Color:
    def __init__(self, red: int, green: int, blue: int, alpha: int = 255):
        self.alpha = alpha
        self.red = red
        self.green = green
        self.blue = blue

    def to_str(self, include_alpha=True) -> str:
        if not include_alpha:
            color = (self.red & 0xff) << 16 | (self.green & 0xff) << 8 | (self.blue & 0xff)
            color_str = hex(color)[2:]
            for i in range(len(color_str), 6):
                color_str = '0' + color_str
        else:
            color = (self.alpha & 0xff) << 24 | (self.red & 0xff) << 16 | (self.green & 0xff) << 8 | (self.blue & 0xff)
            color_str = hex(color)[2:]
            for i in range(len(color_str), 8):
                color_str = '0' + color_str
        return '#' + color_str


def color_from_number(color_number: int) -> Color:
    return Color((color_number >> 16) & 0xff, (color_number >> 8) & 0xff,
                 color_number & 0xff, alpha=(color_number >> 24) & 0xff)


def color_from_str(color_str: str) -> Color:
    return color_from_number(int('0x' + color_str[1:], 16))


def argb_to_str(red: int, green: int, blue: int, alpha: int = None):
    if alpha is None:
        color = (red & 0xff) << 16 | (green & 0xff) << 8 | (blue & 0xff)
        color_str = hex(color)[2:]
        for i in range(len(color_str), 6):
            color_str = '0' + color_str
    else:
        color = (alpha & 0xff) << 24 | (red & 0xff) << 16 | (green & 0xff) << 8 | (blue & 0xff)
        color_str = hex(color)[2:]
        for i in range(len(color_str), 8):
            color_str = '0' + color_str
    return '#' + color_str


COL_BLACK = color_from_str('#ff000000')
COL_BLUE = color_from_str('#ff0000ff')
COL_CYAN = color_from_str('#ff00ffff')
COL_DARK_GRAY = color_from_str('#ff444444')
COL_GRAY = color_from_str('#ff888888')
COL_GREEN = color_from_str('#ff00ff00')
COL_LIGHT_GRAY = color_from_str('#ffcccccc')
COL_MAGENTA = color_from_str('#ffff00ff')
COL_RED = color_from_str('#ffff0000')
COL_TRANSPARENT = color_from_str('#00000000')
COL_WHITE = color_from_str('#ffffffff')
COL_YELLOW = color_from_str('#ffffff00')
