# brasciichart

Console ASCII line charts with Braille characters, no dependencies. 

```console
 1.00 ┤⠉⠉⠳⡄⠀⠀⠀⠀⠀⠀⠀⠀⢠⠔⠉⠉⠢⡤⠚⠉⠑⠦⡀
 0.50 ┤⡀⠀⠀⠈⢣⠀⠀⠀⠀⠀⠀⡔⠁⠀⠀⢀⠎⠈⢢⠀⠀⠀⠑⢄⠀⠀⠀⠀⠀⢀
 0.00 ┤⠘⡄⠀⠀⠀⠱⡀⠀⠀⢀⠜⠀⠀⠀⡠⠎⠀⠀⠀⠣⡀⠀⠀⠈⢆⠀⠀⠀⢠⠃
-0.50 ┤⠀⠈⢣⠀⠀⠀⠑⢄⢠⠊⠀⠀⠀⡰⠁⠀⠀⠀⠀⠀⠑⡄⠀⠀⠀⢣⡀⡜⠁
-1.00 ┤⠀⠀⠀⠑⢤⣀⡠⠜⠳⢄⣀⡤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠈⠢⢄⣀⡤⠚⢦⣀⣀
```

## Install
```
$ pip install brasciichart
```

## Usage
```console
usage: brasciichart [-h] [-v] 
  [-s SERIES_ADD [SERIES_ADD ...]]
  [-c  [...]]
  [-f FORMAT] [-o OFFSET]
  [-H HEIGHT] [-W WIDTH]
  [-m MIN] [-M MAX]
  [--xfrom XFROM] [--xto XTO]
  [--xformat XFORMAT]
  [--xrows {0,1,2}]
  [--no-trim]
  [series ...]

Console ASCII line charts with Braille characters.

positional arguments:
  series                float number series, "NaN" for null-values

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -s SERIES_ADD [SERIES_ADD ...], --series SERIES_ADD [SERIES_ADD ...]
                        additional series
  -c  [ ...], --colors  [ ...]
                        available series colors: black, red, green, yellow,
                        blue, magenta, cyan, lightgray, default, darkgray,
                        lightred, lightgreen, lightyellow, lightblue,
                        lightmagenta, lightcyan, white
  -f FORMAT, --format FORMAT
                        format for tick numbers (default: "{:7.2f} ")
  -o OFFSET, --offset OFFSET
                        chart area offset
  -H HEIGHT, --height HEIGHT
                        rows in chart area
  -W WIDTH, --width WIDTH
                        columns in chart area
  -m MIN, --min MIN     min y value
  -M MAX, --max MAX     max y value
  --xfrom XFROM         the first x-axis value (default 0)
  --xto XTO             the last x-axis value
                        (default `xfrom + max_series_size - 1`)
  --xformat XFORMAT     format for x-axis numbers (default from `--format`)
  --xrows {0,1,2}       rows in x-axis labels.
                        0 - no x-axis (default),
                        1 - one line for labels,
                        2 - two lines for labels.
  --no-trim, --trim     no/trim trailing whitespaces (default trim)
```

```console
$ brasciichart --height 1 --offset 0 -s 1 2 3 4 3 2 1 2 3 4 3 2 1
⡠⠊⠢⡠⠊⠢⡀
```

```console
$ brasciichart --height 10 --min 0 --format '{:5.3f} ' \
  `rrdtool xport -s e-2month -e 20250518 --json \
    DEF:load1=system.rrd:system_load1:AVERAGE \
    XPORT:load1:"System Load 1 min average" \
  | jq -r '[.data[][]] | join(" ")'`
 0.024 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇
 0.021 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇
 0.019 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠀⠀⠀⠀⠀⠀⠀⠀⡇
 0.016 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⣇
 0.013 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⢸⢸
 0.011 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡄⠀⡎⡇⠀⠀⠀⠀⠀⠀⢸⢸
 0.008 ┤⠀⠀⠀⠀⠀⠀⠀⠀⢰⠀⠀⠀⠀⣇⢀⡇⡇⠀⠀⠀⠀⠀⠀⢸⢸
 0.005 ┤⠀⢠⣀⣠⠳⡀⡀⠀⡏⡆⡔⢆⣸⢸⡎⡇⡇⡀⡄⣀⠔⠤⠲⣸⠘⡄⣀⠦⡄⢀⣀
 0.003 ┤⠉⠃⠁⠀⠀⠉⠈⠉⠀⠉⠀⠈⠙⠈⠀⠀⠘⠉⠈⠀⠀⠀⠀⠁⠀⠈⠀⠀⠈⠁
 0.000 ┼
```

```console
$ brasciichart --height 5 \
  `for i in {-50..50..1}; do awk '{printf cos($1/10) " "}' <<< $i; done`
    1.00 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠔⠊⠉⠉⠉⠒⠤⡀
    0.50 ┤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠉⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀
    0.00 ┤⠈⠢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊
   -0.50 ┤⠀⠀⠈⠑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⠢⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠉
   -1.00 ┤⠀⠀⠀⠀⠀⠉⠢⠤⣀⣀⣀⠤⠔⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠒⠤⢄⣀⣀⡠⠤⠊⠁
```

```console
$ brasciichart -H 5 -W 30 -c red green \
  -s `for i in {-50..50..1}; do awk '{printf cos($1/10) " "}' <<< $i; done` \
  -s `for i in {-50..50..1}; do awk '{printf sin($1/10) " "}' <<< $i; done`
    1.00 ┤⠉⠉⠳⡄⠀⠀⠀⠀⠀⠀⠀⠀⢠⠔⠉⠉⠢⡤⠚⠉⠑⠦⡀
    0.50 ┤⡀⠀⠀⠈⢣⠀⠀⠀⠀⠀⠀⡔⠁⠀⠀⢀⠎⠈⢢⠀⠀⠀⠑⢄⠀⠀⠀⠀⠀⢀
    0.00 ┤⠘⡄⠀⠀⠀⠱⡀⠀⠀⢀⠜⠀⠀⠀⡠⠎⠀⠀⠀⠣⡀⠀⠀⠈⢆⠀⠀⠀⢠⠃
   -0.50 ┤⠀⠈⢣⠀⠀⠀⠑⢄⢠⠊⠀⠀⠀⡰⠁⠀⠀⠀⠀⠀⠑⡄⠀⠀⠀⢣⡀⡜⠁
   -1.00 ┤⠀⠀⠀⠑⢤⣀⡠⠜⠳⢄⣀⡤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠈⠢⢄⣀⡤⠚⢦⣀⣀
```

```console
$ brasciichart -W 50 --xrows 1 --xformat '{:.0f}' --xfrom 100 \
  -s 1 `for i in {1..49..1}; do awk '{printf "NaN" " "}' <<< $i; done`
    1.00 ┤⡀
         └┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬─
         100 104 108 112 116 120 124 128 132 136 140 144 148
```
Two-line X-axis labels with rounded values:
```python
from datetime import datetime, timedelta
from brasciichart import *

def xround_func_hour(v):
    dt = datetime.fromtimestamp(v)
    dt_begin_of_hour = dt.replace(minute=0, second=0, microsecond=0)
    dt_half_hour = dt.replace(minute=30, second=0, microsecond=0)

    if dt > dt_half_hour:
        dt = dt_begin_of_hour + timedelta(hours=1)
    else:
        dt = dt_begin_of_hour

    return dt.timestamp()


def xformat_func_hour(v: float):
    val = datetime.fromtimestamp(v)
    if val.hour % 2 == 0:
        return val.strftime('%H:%M')
    return ''

series = [1.0] + [float("nan")] * 49
now = datetime.now()
tomorrow = now + timedelta(days=1)
print(plot(series, {'width': 50, 'xrows': 2, 'xformat': '{}',
                    'xfrom': now.timestamp(), 'xto': tomorrow.timestamp(),
                    'xround_func': xround_func_hour,
                    'xformat_func': xformat_func_hour,}))
```
```console
    1.00 ┤⡀
         └───┬───┬───┬───┬───┬────┬───┬───┬───┬───┬───┬───┬─
           04:00 │ 08:00 │ 12:00  │ 16:00 │ 20:00 │ 00:00 │
               06:00   10:00    14:00   18:00   22:00  02:00
```

## Change log

### v0.2.0
* Add X-axis labels with round and format functions
* Add --no-trim flag to preserve trailing whitespaces
* Cleanup redundant repeated colors

### v0.1.0
Initial release
