def argb_to_str(red: int, green: int, blue: int, alpha: int = None):
    return '#%02x%02x%02x' % (red, green, blue) if alpha is None else '#%02x%02x%02x%02x' % (alpha, red, green, blue)


class Color:
    def __init__(self, red: int, green: int, blue: int, alpha: int = 255):
        self.alpha = alpha
        self.red = red
        self.green = green
        self.blue = blue

    def to_str(self, include_alpha=True) -> str:
        return argb_to_str(self.red, self.green, self.blue, self.alpha if include_alpha else None)


def color_from_number(color_number: int) -> Color:
    return Color((color_number >> 16) & 0xff, (color_number >> 8) & 0xff,
                 color_number & 0xff, alpha=(color_number >> 24) & 0xff)


def color_from_str(color_str: str) -> Color:
    return color_from_number(int('0x' + color_str[1:], 16))


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
