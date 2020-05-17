from math import e, exp


class Colour:  # TODO should this subclass Vector? + and * would be useful
    COMMON_COLOURS = {
        'red':      (0xff, 0x00, 0x00),
        'green':    (0x00, 0xff, 0x00),
        'blue':     (0x00, 0x00, 0xff),
        'white':    (0xff, 0xff, 0xff),
        'black':    (0x00, 0x00, 0x00),
        'yellow':   (0xff, 0xff, 0x00),
        'magenta':  (0xff, 0x00, 0xff),
        'cyan':     (0x00, 0xff, 0xff),
        'orange':   (0xff, 0x7f, 0x00),  # TODO add other 127-based colours?
        'epic':     (0x66, 0x00, 0x33),  # TODO make these pre-existing objects?
        'lime':     (0x00, 0x00, 0x00),
        'grey':     (0x00, 0x00, 0x00),
        'pink':     (0x00, 0x00, 0x00),
        'purple':   (0x00, 0x00, 0x00),
    }

    def __init__(self, arg=' '):
        """Input can be hex string, colour name or rgb tuple. No arg = black."""
        self._rgb = (0, 0, 0)
        if arg[0] == '#':  # hx
            self._rgb = Colour.hx_to_rgb(arg)
        elif arg != ' ':  # arg is rgb tuple or colour name
            self._rgb = Colour.COMMON_COLOURS.get(arg, None)
            if self._rgb is None:
                self._rgb = tuple(int(x) for x in arg)

    def __str__(self):
        return Colour.rgb_to_hx(*self._rgb)

    def __repr__(self):
        return Colour.rgb_to_hx(*self._rgb)

    @property
    def hx(self):
        return Colour.rgb_to_hx(*self._rgb)

    @property
    def rgb(self):
        return self._rgb

    def __add__(self, other):
        return Colour(tuple(
            n+m for n, m in zip(self._rgb, other._rgb)
        ))  # basically vector addition?

    @staticmethod
    def rgb_to_hx(r, g, b):
        return f'#{r:02x}{g:02x}{b:02x}'

    @staticmethod
    def hx_to_rgb(hx):
        r = int(hx[1:3], 16)
        g = int(hx[3:5], 16)
        b = int(hx[5:7], 16)
        return (r, g, b)

    def adjust_value(self, ratio):
        """
        adjusts colour value by adj ratio
        (https://en.wikipedia.org/wiki/Colour_value)
        :param adj: float multiplier (1 for no change)
        :return: adjusted Colour object
        """
        return Colour(tuple(
            ratio*x if ratio*x<=255 else 255 for x in self._rgb
        ))  # multiplies twice per x... fix somehow? TODO


class Shader:
    """Provides different ways of mapping [-1,1] to shading ratios"""
    def __init__(self):
        self._formula = self._logistic

    def shade(self, rating):
        return self._formula(rating)

    @staticmethod
    def _half_to_one(x):
        return x/4 + 0.75

    @staticmethod
    def _zero_to_one(x):
        return x/2 + 0.5

    @staticmethod
    def _cubic(x):  # I had to think a bit for this one
        return 0.3*(x**3) + 0.1*x + 0.6

    @staticmethod
    def _signum(x):
        if x < 0:
            return 0.2
        if x > 0:
            return 1
        return 0.6

    @staticmethod
    def _logistic(x):
        return 0.5 + 0.5/(1+exp(-4*x))

