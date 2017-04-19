import math

from utils.calc.range import Range


class GraphPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return str({'x': self.x, 'y': self.y})


def graph_to_string(name: str, graph_points: list, size_x: int = None, size_y: int = None,
                    range_x: Range = None, range_y: Range = None):
    if len(graph_points) < 2:
        return 'Can\'t create string from graph %s. (graph is empty)' % name

    if range_x is None:
        graph_x = [point.x for point in graph_points]
        min_graph_x = min(graph_x)
        max_graph_x = max(graph_x)
        del graph_x
        graph_x_add = abs(max_graph_x - min_graph_x) * 0.2
        min_graph_x -= graph_x_add
        max_graph_x += graph_x_add
    else:
        min_graph_x = range_x.val_min
        max_graph_x = range_x.val_max

    if range_y is None:
        graph_y = [point.y for point in graph_points]
        min_graph_y = min(graph_y)
        max_graph_y = max(graph_y)
        del graph_y
        graph_y_add = abs(max_graph_y - min_graph_y) * 0.2
        min_graph_y -= graph_y_add
        max_graph_y += graph_y_add
    else:
        min_graph_y = range_y.val_min
        max_graph_y = range_y.val_max

    if min_graph_x == max_graph_x or min_graph_y == max_graph_y:
        return 'Can\'t create string from graph %s. (graph is too small - one point width or height)' % name

    if size_x is None:
        size_x = min(int(max_graph_x - min_graph_x) * 4, 150)
    if size_y is None:
        size_y = min(int(max_graph_y - min_graph_y), 100)
    size_x = max(size_x, 10)
    size_y = max(size_y, 10)
    len_x = size_x + 1
    len_y = size_y + 1

    max_graph_x_len = max(len(str(math.floor(min_graph_x))), len(str(math.floor(max_graph_x))))
    max_graph_y_len = max(len(str(math.floor(min_graph_y))), len(str(math.floor(max_graph_y))))

    left_offset = max_graph_y_len + 6

    # width = len_x + left_offset

    def x_to_graph_val(x):
        return x / size_x * (max_graph_x - min_graph_x) + min_graph_x

    def y_to_graph_val(y):
        return y / size_y * (max_graph_y - min_graph_y) + min_graph_y

    graph_map = [[' ' for x in range(len_x)] for y in range(len_y)]  # '*' if int(x_to_graph_val(x)) == 0 else

    def x_to_graph_label(x):
        val = x_to_graph_val(x)
        text = (' ' * (max_graph_x_len - len(str(int(val))))) + str(round(val, 5))
        if -1 < val < 0:
            text = text[1:]
        return text

    def y_to_graph_label(x):
        val = y_to_graph_val(x)
        text = (' ' * (max_graph_y_len - len(str(int(val))))) + str(round(val, 5))
        if -1 < val < 0:
            text = text[1:]
        text += ' ' * (max_graph_y_len + 6 - len(text))
        return text

    graph_x_labels = [x_to_graph_label(x) for x in range(len_x)]

    def point_to_graph_map_point(point: GraphPoint) -> GraphPoint:
        return GraphPoint(
            int((point.x - min_graph_x) / (max_graph_x - min_graph_x) * size_x),
            int((point.y - min_graph_y) / (max_graph_y - min_graph_y) * size_y)
        )

    for point in graph_points:
        graph_point = point_to_graph_map_point(point)
        if 0 < graph_point.x < len_x and 0 < graph_point.y < len_y:
            graph_map[graph_point.y][graph_point.x] = '■'

    graph_str = (' ' + ' ' * left_offset + '+' + '-' * len_x + '+') + '\n' + \
                (' ' + ' ' * left_offset + '|' + name + ' ' * (len_x - len(name)) + '|') + '\n' + \
                ('+' + '-' * left_offset + '+' + '=' * len_x + '+') + '\n' + \
                ('\n'.join(('|' + y_to_graph_label(len(graph_map) - y) + '|' + ''.join(graph_map[-y]) + '|'
                            for y in range(1, len(graph_map) + 1)))) + '\n' + \
                ('+' + '-' * left_offset + '+' + '-' * len_x + '+')

    run_labels = True
    label_char_pos = 0
    while run_labels:
        run_labels = False
        graph_str += '\n ' + ' ' * left_offset + '|'
        for label in graph_x_labels:
            if len(label) <= label_char_pos:
                graph_str += ' '
                continue
            graph_str += label[label_char_pos]
            run_labels = True
        graph_str += '|'
        label_char_pos += 1
    graph_str += '\n ' + ' ' * left_offset + '+' + '-' * len_x + '+'

    return graph_str
