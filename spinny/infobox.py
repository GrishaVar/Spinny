from collections import OrderedDict


class InfoBox:
    """
    Draws box with runtime for debug information.

    add(self, item, default='', rounding=None) adds item to box.
    draw(self, *args) re-draws box with updated information.

    canvas: Given tk Canvas object.
    x, y: ints, top-left position of box.
    width: int, with of box in pixels.
    items: OrderedDict of given info lines.
    """
    def __init__(self, canvas, pos, width, fill='white', border='black'):
        self.canvas = canvas
        self.x, self.y = pos
        self.width = width

        self.items = OrderedDict()
        self.counter = 0

        self.text_box = self.canvas.create_polygon(
            0, 0,
            fill=fill,
            outline=border,
            width=2,
            tag='infobox',
        )

    def add(self, item, default='', rounding=None):
        """
        Add item to InfoBox.
        :param item: str, identifier
        :param default: str, text to display
        :param rounding: int, rounding
        """
        if item in self.items:
            return  # TODO: what should I do here?
        obj = self.canvas.create_text(
            self.x+2,
            self.y+2 + 17*self.counter,
            anchor='nw',
            font='Arial 13',
            tag='infobox',
        )
        self.items[item] = (default, obj, rounding)
        self.counter += 1
        self.resize_box()

    def draw(self, *args):
        """
        Draws/Updates InfoBox with given args.
        :param args: iterable of arguments for each item, in order
        """
        if len(args) != len(self.items):
            raise TypeError('Too many/few arguments')
        self.canvas.tag_raise(self.text_box)
        for item, value in zip(self.items, args):
            default, obj, rounding = self.items[item]
            if rounding is not None:
                value = round(value, rounding)
            self.canvas.itemconfig(obj, text=default.format(value))
            self.canvas.tag_raise(obj)

    def resize_box(self):
        self.canvas.coords(
            self.text_box,
            self.x, self.y,
            self.x, self.y + 17*self.counter + 4,  # TODO: fix magic numbers
            self.x+self.width, self.y + 17*self.counter + 4,
            self.x+self.width, self.y
        )