#!/bin/env python3
# -*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2025 cthulhu
"""Module to generate ascii charts.

This module provides a single function `plot` that can be used to generate an
ascii chart from a series of numbers with using braille font.
The chart can be configured via several options to tune the output.
"""
from __future__ import division

from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter
from collections import defaultdict, Counter
from math import ceil, floor, isnan, cos

black = '\033[30m'
red = '\033[31m'
green = '\033[32m'
yellow = '\033[33m'
blue = '\033[34m'
magenta = '\033[35m'
cyan = '\033[36m'
lightgray = '\033[37m'
default = '\033[39m'
darkgray = '\033[90m'
lightred = '\033[91m'
lightgreen = '\033[92m'
lightyellow = '\033[93m'
lightblue = '\033[94m'
lightmagenta = '\033[95m'
lightcyan = '\033[96m'
white = '\033[97m'
reset = '\033[0m'

__version__ = '0.1.0'
__all__ = [
    'plot', 'black', 'red',
    'green', 'yellow', 'blue',
    'magenta', 'cyan', 'lightgray',
    'default', 'darkgray', 'lightred',
    'lightgreen', 'lightyellow', 'lightblue',
    'lightmagenta', 'lightcyan', 'white', 'reset',
]

DEFAULT_FORMAT = '{:7.2f} '


def _isnum(n):
    return n is not None and not isnan(n)


def colored(char, color):
    if not color or color == reset:
        return char
    else:
        return color + char + reset


class Pixels(list):
    def __init__(self, width, height):
        super().__init__(
            [defaultdict(list) for _ in range(width)]
            for _ in range(height))

    @staticmethod
    def iterline(x1, y1, x2, y2):
        xdiff = abs(x2 - x1)
        ydiff = abs(y2 - y1)
        xdir = 1 if x1 <= x2 else -1
        ydir = 1 if y1 <= y2 else -1

        r = ceil(max(xdiff, ydiff))
        if r == 0:  # point, not line
            yield x1, y1
        else:
            x, y = floor(x1), floor(y1)
            i = 0
            while i < r:
                x += xdir * xdiff / r  # with floating point can be > x2
                y += ydir * ydiff / r  #

                yield x, y
                i += 1

    def getAttr(self, x, y) -> str:
        r = self[y][x]
        if not r:
            return ''
        c = [(len(vals), vals, attr)
             for attr, vals in r.items() if attr]
        if not c:
            return ''
        _, _, attr = max(c)
        return attr

    def plotpixel(self, x, y, attr, val=None):
        self[y][x][attr].append(val)

    def plotline(self, x1, y1, x2, y2, attr, val=None):
        prev_x, prev_y = None, None
        for x, y in self.iterline(x1, y1, x2, y2):
            if x != prev_x or y != prev_y:
                self.plotpixel(round(x), round(y), attr, val)


def plot(series, cfg=None):
    """Generate an ascii chart for a series of numbers.

    `series` should be a list of ints or floats. Missing data values in the
    series can be specified as a NaN. In Python versions less than 3.5, use
    float("nan") to specify an NaN. With 3.5 onwards, use math.nan to specify a
    NaN.

    >>> print(plot([cos(n / 10) for n in range(-50, 50, 1)], \
                   {'height': 5}))
        1.00 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠔⠊⠉⠉⠉⠒⠤⡀
        0.50 ┤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠉⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⢄
        0.00 ┤⠈⠢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊
       -0.50 ┤⠀⠀⠈⠑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⠢⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠉
       -1.00 ┤⠀⠀⠀⠀⠀⠉⠢⠤⣀⣀⣀⠤⠔⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠒⠤⢄⣀⣀⡠⠤⠊⠁

    >>> print(plot([1, 2, 3, 4, float("nan"), 4, 3, 2, 1]))
        4.00 ┤⠀⡸⠸⡀
        3.00 ┤⠀⡇⠀⡇
        2.00 ┤⢸⠀⠀⢸
        1.00 ┤⡎⠀⠀⠈⡆

    `series` can also be a list of lists to support multiple data series.

    >>> print(plot([[10, 20, 30, 40, 30, 20, 10], \
                    [40, 30, 20, 10, 20, 30, 40]], \
                   {'height': 3}))
       40.00 ┤⢇⡜⣄⠇
       25.00 ┤⢸⡇⣿
       10.00 ┤⡎⢣⠋⡆

    `cfg` is an optional dictionary of various parameters to tune the appearance
    of the chart. `min` and `max` will clamp the y-axis and all values:

    >>> series = [1, 2, 3, 4, float("nan"), 4, 3, 2, 1]
    >>> print(plot(series, {'min': 0}))
        4.00 ┤⠀⡸⠸⡀
        3.00 ┤⠀⡇⠀⡇
        2.00 ┤⢸⠀⠀⢸
        1.00 ┤⠇⠀⠀⠀⠇
        0.00 ┼

    >>> print(plot(series, {'min': 2}))
        4.00 ┤⠀⡸⠸⡀
        3.00 ┤⠀⡇⠀⡇
        2.00 ┤⣰⠁⠀⢸⡀

    >>> print(plot(series, {'min': 2, 'max': 3}))
        3.00 ┤⠀⡏⠈⡇
        2.00 ┤⣸⠀⠀⢸⡀

    `height` specifies the number of rows the graph should occupy. It can be
    used to scale down a graph with large data values:

    >>> print(plot([10, 20, 30, 40, 50, 40, 30, 20, 10], \
                   {'height': 5}))
       50.00 ┤⠀⢀⢇
       40.00 ┤⠀⡸⠸⡀
       30.00 ┤⠀⡇⠀⡇
       20.00 ┤⢸⠀⠀⢸
       10.00 ┤⡎⠀⠀⠈⡆

    `width` specifies the number of columns the graph should occupy. It can be
    used to scale down a graph with large data values:

    >>> print(plot([cos(n / 10) for n in range(-50, 50, 1)], \
                   {'height': 5, 'width': 10}))
        1.00 ┤⠀⠀⠀⠀⡜⢳
        0.50 ┤⡀⠀⠀⢰⠁⠈⡇
        0.00 ┤⢣⠀⠀⡸⠀⠀⢣⠀⠀⡸
       -0.50 ┤⠘⡄⢀⠇⠀⠀⠘⡄⢀⠇
       -1.00 ┤⠀⢧⡼⠀⠀⠀⠀⢣⡼

    >>> print(plot([[10, 20, 30, 40, 30, 20, 10], \
                    [40, 30, 20, 10, 20, 30, 40]], \
                   {'height': 3, 'width': 30}))
       40.00 ┤⠉⠒⠤⢄⡀⠀⠀⠀⠀⠀⠀⣀⠤⠔⠊⠉⠒⠤⣀⠀⠀⠀⠀⠀⠀⢀⡠⠤⠒⠉
       25.00 ┤⠀⠀⠀⠀⢈⣉⠶⠶⠶⢎⣉⠀⠀⠀⠀⠀⠀⠀⠀⣉⡱⠶⠶⠶⣉⡁
       10.00 ┤⣀⠤⠒⠊⠁⠀⠀⠀⠀⠀⠀⠉⠒⠢⢄⣀⠤⠒⠉⠀⠀⠀⠀⠀⠀⠈⠑⠒⠤⣀

    `format` specifies a Python format string used to format the labels on the
    y-axis. The default value is "{:7.2f} ". This can be used to remove the
    decimal point:

    >>> print(plot([-10, 20, 30, 40, 50, 40, 30, 20, -10], \
                   {'height': 5, 'format':'{:8.0f} '}))
           50 ┤⠀⢠⢣
           35 ┤⠀⡎⠈⡆
           20 ┤⢸⠀⠀⢸
            5 ┤⡜⠀⠀⠸⡀
          -10 ┤⡇⠀⠀⠀⡇

    `xrows` specifes rows for x-axis labels.
      0 - no x-axis (default),
      1 - one line for labels,
      2 - two lines for labels.

    `xformat` specifes a Python format string used to format the labels on the
    x-axis. By default the `format` value is used.

    `xfrom` specifies the first x-axis value, (default 0).

    `xto` the last x-axis value, (default `xfrom + max_series_size - 1`).

    >>> series = [1.0] + [float("nan")] * 49
    >>> print(plot(series, {'width': 50, 'xrows': 2, 'xformat': '{:.0f}'}))
        1.00 ┤⡀
             └┬┬┬┬┬┬┬┬┬┬┬─┬┬─┬┬─┬┬─┬┬─┬┬─┬┬─┬┬─┬┬─┬┬─┬┬─┬┬─┬┬─┬─
              0│2│4│6│8│10│13│16│19│22│25│28│31│34│37│40│43│46│
               1 3 5 7 9  12 15 18 21 24 27 30 33 36 39 42 45 48

    >>> print(plot(series, {'width': 50, 'xrows': 1, 'xfrom': 1, \
                            'xformat': '{:.0f}'}))
        1.00 ┤⡀
             └┬─┬─┬─┬─┬─┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬───
              1 3 5 7 9 11 14 17 20 23 26 29 32 35 38 41 44 47

    `xformat_func` optional function to pre-process x value before `xformat`.

    >>> print(plot(series, { \
            'width': 50, 'xrows': 2, 'xfrom': 1, 'xformat': '{}', \
            'xformat_func': lambda x: '---' if x == 1 \
                                      else f'{x:013.0f}' if x % 10 == 0 \
                                      else ''}))
        1.00 ┤⡀
             └┬────────┬─────────┬─────────┬─────────┬─────────┬
             ---       │   0000000000020   │   0000000000040   │
                 0000000000010       0000000000030 0000000000050

    `xround_func` optional function to round x-values. X label be printed
    if rounded value is in (`x` <= round < `x+1`) range.

    >>> print(plot(series, {'width': 50, 'xrows': 1, 'xformat': '{:.0f}', \
                            'xround_func': lambda x: ceil(x / 7) * 7}))
        1.00 ┤⡀
             └┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬
              0      7      14     21     28     35     42    49

    `trim` trailing spaces. Default `True`. 'False' useful to concat several
    charts horizontally.

    >>> cfg = {'width': 5, 'trim': False, 'xrows': 2, \
               'format': '{}', 'format_func': lambda x: '', \
               'xformat': '{:.0f}', 'xround_func': lambda x: ceil(x / 2) * 2}
    >>> print(plot([1, 1, float('NaN'), float('NaN'), float('NaN')], cfg) \
              .replace("\\n", "$\\n") + "$")
      ┤⣀⡀⠀⠀⠀$
      └┬─┬─┬$
       0 │ 4$
         2  $

    >>> cfg.update({'trim': True})
    >>> print(plot([1, 1, float('NaN'), float('NaN'), float('NaN')], cfg) \
              .replace("\\n", "$\\n") + "$")
      ┤⣀⡀$
      └┬─┬─┬$
       0 │ 4$
         2$
    """
    if len(series) == 0:
        return ''

    if not isinstance(series[0], list):
        if all(not _isnum(n) for n in series):
            return ''
        else:
            series = [series]

    cfg = cfg or {}
    minimum = cfg.get('min', min(filter(_isnum, [y for s in series for y in s])))
    maximum = cfg.get('max', max(filter(_isnum, [y for s in series for y in s])))
    if minimum > maximum:
        raise ValueError('The min value cannot exceed the max value.')

    interval = maximum - minimum
    offset = cfg.get('offset', 3)
    height = cfg.get('height', ceil(interval) + 1)
    height = int((height or 1) * 4)
    ratio = ((height - 1) or 1) / (interval or 1)

    colors = cfg.get('colors', [reset])
    symbols = cfg.get('symbols', ['┼', '┤', '└', '─', '┼', '┬', '│'])

    def scaled_y(y):
        y = min(max(y, minimum), maximum)
        return int(round((y - minimum) * ratio))

    series_width = 0
    for s in series:
        series_width = max(series_width, len(s))
    width = cfg.get('width')
    width = width * 2 if width else series_width
    xratio = (width - 1) / (series_width - 1 or 1)
    width += width % 2

    def scaled_x(x):
        return int(round(x * xratio))

    pixels = Pixels(width, height)

    polylines = []
    for s, ser in enumerate(series):
        prev_y = None
        for x, y in enumerate(ser):
            attr = colors[s] if len(colors) > s else reset
            if _isnum(y):
                if not _isnum(prev_y):
                    polylines.append(([(x, y)], attr, y))
                else:
                    polylines.append(([(x - 1, prev_y), (x, y)], attr, y))
            prev_y = y

    for vertexes, attr, row in polylines:
        if len(vertexes) == 1:  # single point
            x, y = vertexes[0]
            pixels.plotpixel(scaled_x(x),
                             height - scaled_y(y) - 1, attr, row)
            continue

        prev_x, prev_y = vertexes[0]
        for x, y in vertexes[1:]:
            x1 = scaled_x(prev_x)
            y1 = height - scaled_y(prev_y) - 1
            x2 = scaled_x(x)
            y2 = height - scaled_y(y) - 1
            pixels.plotline(x1, y1, x2, y2, attr, row)
            prev_x, prev_y = x, y
    axis_shift = max(min(2, offset), 0)  # [0]='lbl'  [1]='|'
    result = [[' '] * axis_shift + [chr(0x2800)] * (width // 2)
              for _ in range(height // 4)]

    # axis and labels
    label = ''
    if offset > 0:
        fmt = cfg.get('format', DEFAULT_FORMAT)
        fmt_func = cfg.get('format_func', None)
        for y in range(height // 4):
            mark = maximum - y * (interval / (((height - 1) // 4) or 1))
            label = fmt.format(fmt_func(mark) if fmt_func else mark)
            result[y][max(axis_shift - 2, 0)] = label or ' '
            result[y][max(axis_shift - 1, 0)] = symbols[1] if mark else symbols[0]

    for y in range(height // 4):
        for x in range(width // 2):
            # @formatter:off
            block_attrs = [
                pixels.getAttr(x * 2,     y * 4),
                pixels.getAttr(x * 2,     y * 4 + 1),
                pixels.getAttr(x * 2,     y * 4 + 2),
                pixels.getAttr(x * 2 + 1, y * 4),
                pixels.getAttr(x * 2 + 1, y * 4 + 1),
                pixels.getAttr(x * 2 + 1, y * 4 + 2),
                pixels.getAttr(x * 2,     y * 4 + 3),
                pixels.getAttr(x * 2 + 1, y * 4 + 3),
            ]
            # @formatter:on
            braille_num = sum(int(bool(attr)) * (1 << i)
                              for i, attr in enumerate(block_attrs))
            if braille_num:
                ch = chr(0x2800 + braille_num)
                c = Counter(c for c in block_attrs if c).most_common(1)[0][0]
                result[y][x + axis_shift] = colored(ch, c)

    trim = cfg.get('trim', True)
    xfrom = cfg.get('xfrom', 0)
    xto = cfg.get('xto', xfrom + series_width - 1)
    xrows = cfg.get('xrows', 0)

    if colors and colors[0] != reset:
        reset_len = len(reset)
        color_len = len(default)
        for row in result:
            for i in range(len(row) - 2, 0, -1):
                if (row[i].startswith('\033')
                        and row[i][0:color_len] == row[i + 1][0:color_len]):
                    # cleanup redundant repeated colors to reduce size
                    row[i] = row[i][0:-reset_len]
                    row[i + 1] = row[i + 1][color_len:]

    if not xrows:
        return '\n'.join([
            (' ' * max(offset - axis_shift, 0)
             + (''.join(r).rstrip(chr(0x2800)) if trim else ''.join(r)))
            for r in result])

    # X-Axis labels
    # TODO: Refactor this [censored]
    xstep = abs(xto - xfrom) / (((width // 2) - 1) or 1)
    if xto < xfrom:
        xstep = -xstep
    xfmt = cfg.get('xformat', cfg.get('format', DEFAULT_FORMAT))
    result.append([' '] * axis_shift + [chr(0x2800)] * (width // 2))
    result[-1][max(axis_shift - 2, 0)] = ' ' * (len(label) or 1)
    result[-1][max(axis_shift - 1, 0)] = symbols[2]  # '└'
    #
    xval = xfrom
    row1 = ''
    row2 = ''
    str_shift = 0
    if axis_shift == 1:
        str_shift = 1  # Y-axis only '|'
    elif axis_shift == 2:
        str_shift = (len(label) or 1) + 1 + (offset - 2)  # Lbl + Y-axis + offset
    is_row1_selected = True
    fmt_func = cfg.get('xformat_func', None)
    rnd_func = cfg.get('xround_func', None)
    ch_width = width // 2
    for i in range(0, ch_width):
        result[-1][i + axis_shift] = symbols[3]  # '─'
        lbl = None
        if rnd_func:
            rounded = rnd_func(xval)
            if xval <= rounded < (xval + xstep):
                lbl = xfmt.format(fmt_func(rounded) if fmt_func else rounded)
        else:
            lbl = xfmt.format(fmt_func(xval) if fmt_func else xval)
        if not lbl:
            xval += xstep
            continue  #

        xlbl_pos = i + str_shift
        if (i == 0 and str_shift > 0) or len(lbl) > 2:
            xlbl_pos -= len(lbl) // 2
        len1, len2 = len(row1), len(row2)
        if len1 <= (i + str_shift):
            if (is_row1_selected
                    and len1 <= xlbl_pos
                    and len1 - str_shift + len(lbl) <= ch_width):
                result[-1][i + axis_shift] = symbols[5]  # '┬'
                pad = xlbl_pos - len1
                if pad > 0:
                    if (len1 + pad - str_shift + len(lbl)) >= ch_width:
                        # shift to the left to don't exceed the width
                        pad -= (len1 + pad - str_shift + len(lbl)) - ch_width
                    row1 += ' ' * pad
                row1 += lbl
                if xrows > 1:
                    is_row1_selected = not is_row1_selected
                else:
                    row1 += ' '
            elif (not is_row1_selected
                  and len2 <= xlbl_pos
                  and len2 - str_shift + len(lbl) <= ch_width):
                #
                result[-1][i + axis_shift] = symbols[5]  # '┬'
                # row 1
                pad = (i + str_shift) - len1
                if pad > 0:
                    row1 += ' ' * pad
                row1 += symbols[6]  # '│'
                # row 2
                pad = xlbl_pos - len2
                if pad:
                    if (len2 + pad - str_shift + len(lbl)) >= ch_width:
                        # shift to the left to don't exceed the width
                        pad -= (len2 + pad - str_shift + len(lbl)) - ch_width
                    row2 += ' ' * pad
                row2 += lbl + ' '
                is_row1_selected = not is_row1_selected

        xval += xstep

    row1 = row1.rstrip()
    row2 = row2.rstrip()
    if not trim:
        row1 = row1.ljust(ch_width + str_shift)
        if xrows > 1:
            row2 = row2.ljust(ch_width + str_shift)

    text = '\n'.join([
        (' ' * max(offset - axis_shift, 0)
         + (''.join(r).rstrip(chr(0x2800)) if trim else ''.join(r)))
        for r in result])
    text += f'\n{row1}'
    if xrows > 1:
        text += f'\n{row2}'
    return text


COLORS = {
    'black': black,
    'red': red,
    'green': green,
    'yellow': yellow,
    'blue': blue,
    'magenta': magenta,
    'cyan': cyan,
    'lightgray': lightgray,
    'default': default,
    'darkgray': darkgray,
    'lightred': lightred,
    'lightgreen': lightgreen,
    'lightyellow': lightyellow,
    'lightblue': lightblue,
    'lightmagenta': lightmagenta,
    'lightcyan': lightcyan,
    'white': white,
}


class SeriesAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not getattr(namespace, 'series_add', None):
            setattr(namespace, 'series_add', [])
        namespace.series_add.append(list(map(float, values)))


class ColorsAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not getattr(namespace, 'colors', None):
            setattr(namespace, 'colors', [])
        namespace.colors += list(map(lambda c: COLORS[c], values))


class BooleanAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, not option_string.startswith('--no'))


def argparse():
    parser = ArgumentParser(
        prog='brasciichart',
        formatter_class=RawDescriptionHelpFormatter,
        description='Console ASCII line charts with Braille characters.')

    parser.add_argument(
        '-v', '--version', action='version',
        version=f'brasciichart {__version__}')
    parser.add_argument(
        'series', type=float, nargs='*',
        help='float number series, "NaN" for null-values')
    parser.add_argument(
        '-s', '--series', action=SeriesAction, type=float, nargs='+',
        dest='series_add', help='additional series')
    parser.add_argument(
        '-c', '--colors', action=ColorsAction, nargs='+', metavar='',
        choices=COLORS.keys(),
        help='available series colors:'
             ' black, red, green, yellow, blue, magenta, cyan, lightgray,'
             ' default, darkgray, lightred, lightgreen, lightyellow, lightblue,'
             ' lightmagenta, lightcyan, white')
    parser.add_argument(
        '-f', '--format', default=DEFAULT_FORMAT,
        help='format for tick numbers (default: "{:7.2f} ")')
    parser.add_argument('-o', '--offset', type=int, help='chart area offset')
    parser.add_argument('-H', '--height', type=int, help='rows in chart area')
    parser.add_argument('-W', '--width', type=int, help='columns in chart area')
    parser.add_argument('-m', '--min', type=float, help='min y value')
    parser.add_argument('-M', '--max', type=float, help='max y value')
    parser.add_argument(
        '--xfrom', type=float,
        help='the first x-axis value (default 0)')
    parser.add_argument(
        '--xto', type=float,
        help='the last x-axis value (default `xfrom + max_series_size - 1`)')
    parser.add_argument(
        '--xformat', type=str,
        help='format for x-axis numbers (default from `--format`)')
    parser.add_argument(
        '--xrows', type=int, choices=[0, 1, 2],
        help='rows in x-axis labels.'
             ' 0 - no x-axis (default),'
             ' 1 - one line for labels,'
             ' 2 - two lines for labels.')
    parser.add_argument(
        '--no-trim', '--trim', dest='trim', nargs=0, action=BooleanAction,
        help='no/trim trailing whitespaces (default trim)')

    parser.epilog = """
Example:
./brasciichart.py --height 2 --offset 0 \\
  `for i in {-50..50..1}; do awk '{printf cos($1/10) " "}' <<< $i; done`
Output:
⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠤⠔⠒⠊⠉⠉⠉⠉⠉⠒⠒⠤⢄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀
⠀⠈⠉⠒⠢⠤⠤⣀⣀⣀⣀⣀⡠⠤⠔⠒⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠑⠒⠤⠤⣀⣀⣀⣀⣀⡠⠤⠤⠒⠊⠉
"""
    return parser


def main():
    parser = argparse()
    args = vars(parser.parse_args())
    series = args.pop('series')
    series_add = args.pop('series_add')
    if not series and not series_add:
        parser.print_help()
        exit(1)
    series = ([series] if series else []) + (series_add or [])
    cfg = {k: v for k, v in args.items() if v is not None}
    print(plot(series, cfg))


if __name__ == '__main__':
    main()
