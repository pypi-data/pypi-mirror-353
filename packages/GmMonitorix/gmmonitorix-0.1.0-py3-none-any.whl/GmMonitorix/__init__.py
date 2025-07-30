import fcntl
import math
import re
import urllib.parse
from dataclasses import dataclass
from datetime import timedelta, datetime
from pathlib import Path
from typing import Union

__version__ = '0.1.0'
OUTPUT_DIR = Path('.tmp')
ADMINS_FILE = Path('.admins')
MONITORIX_CONF = Path('/etc/monitorix/monitorix.conf')
MONITORIX_DB_DIR = Path('/var/lib/monitorix')
GRAPHS_REFRESH_PERIOD = timedelta(seconds=15)
IMG_FORMAT = 'png'
THEME_BLACK = [
    '--slope-mode',
    '--font=LEGEND:7:',
    '--font=TITLE:9:',
    '--font=UNIT:8:',
    '--font=DEFAULT:0:Mono',
    '--color=CANVAS#000000',
    '--color=BACK#101010',
    '--color=FONT#C0C0C0',
    '--color=MGRID#80C080',
    '--color=GRID#808020',
    '--color=FRAME#808080',
    '--color=ARROW#FFFFFF',
    '--color=SHADEA#404040',
    '--color=SHADEB#404040',
    '--color=AXIS#101010',
]


@dataclass(frozen=True)
class Params:
    picUrls: bool = False
    nwhen: str = '1'
    twhen: str = 'day'

    @property
    def when(self):
        return f'{self.nwhen}{self.twhen}'

    @staticmethod
    def from_str(query) -> 'Params':
        params = urllib.parse.parse_qs(query)

        pic_urls = params.get('urls', '0')
        pic_urls = (pic_urls[0] == '1' if isinstance(pic_urls, list)
                    else pic_urls == '1')

        when = params.get('when', '1day')
        when = when[0] if isinstance(when, list) else when
        nwhen = (re.search(r'^\d+', when) or [1])[0]
        twhen = (re.search(r'hour|day|week|month|year', when) or ['day'])[0]

        return Params(picUrls=pic_urls, nwhen=nwhen, twhen=twhen)

    def __str__(self):
        return f'when={self.when}&urls={"1" if self.picUrls else "0"}'


class GraphSize:
    # @formatter:off
    large         = ['--width=750', '--height=180']  # noqa
    large_ascii   = {'width': 75,   'height': 12  }  # noqa
    main          = ['--width=450', '--height=150']  # noqa
    main_ascii    = {'width': 45,   'height': 10  }  # noqa
    medium        = ['--width=325', '--height=150']  # noqa
    medium_ascii  = {'width': 32,   'height': 10  }  # noqa
    medium2       = ['--width=325', '--height=70' ]  # noqa
    medium2_ascii = {'width': 32,   'height': 4   }  # noqa
    small         = ['--width=200', '--height=66' ]  # noqa
    small_ascii   = {'width': 20,   'height': 4   }  # noqa
    mini          = ['--width=183', '--height=66' ]  # noqa
    mini_ascii    = {'width': 18,   'height': 4   }  # noqa
    tiny          = ['--width=110', '--height=40' ]  # noqa
    tiny_ascii    = {'width': 11,   'height': 2   }  # noqa
    zoom          = ['--width=800', '--height=300']  # noqa
    zoom_ascii    = {'width': 80,   'height': 20  }  # noqa
    remote        = ['--width=300', '--height=100']  # noqa
    remote_ascii  = {'width': 30,   'height': 6   }  # noqa
    # @formatter:on

    @staticmethod
    def apply(cfg: dict):
        sizes = cfg.get('graph_size', {})
        for name, size in sizes.items():  # type: str, str
            wh = size.split('x')
            setattr(GraphSize, name,
                    [f'--width={wh[0]}', f'--height={wh[1]}'])
            # setattr(GraphSize, f'{name}_ascii',
            #         {'width': int(wh[0]) // 10, 'height': int(wh[1]) // 15})


class Locker:
    filename: Path

    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        self.fp = open(self.filename, mode='w')
        fcntl.flock(self.fp.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, _type, value, tb):
        fcntl.flock(self.fp.fileno(), fcntl.LOCK_UN)
        self.fp.close()
        return False


UNITS = [' bytes', 'KiB', 'MiB', 'GiB']


def human_size(size, units=None):
    if units is None:
        units = UNITS
    return f'{size:.01f} {units[0]}' if size < 1024 \
        else human_size(size / 1024, units[1:])


LBL_UNITS = ['b', 'k', 'M', 'G']


def lbl_size(size, units=None):
    if units is None:
        units = LBL_UNITS
    return '0  ' if math.ceil(size) == 0 \
        else f'{math.ceil(size):.0f} {units[0]}' if size < 1024 \
        else lbl_size(size / 1024, units[1:])


def min_max_last_avg(fmt: str, ser: list):
    if values := list(filter(lambda x: x is not None, ser)):
        return (fmt.format(min(values)).strip(),
                fmt.format(max(values)).strip(),
                fmt.format(values[-1]).strip(),
                fmt.format(sum(values) / len(values)).strip())
    return '', '', '', ''


def lstrip_column(text):
    spaces = re.findall(r'^\s*', text, re.MULTILINE)
    min_spaces = min(map(len, spaces))
    if not min_spaces:
        return text  # nothing to strip
    return ''.join(map(lambda line: line[min_spaces:],
                       text.splitlines(keepends=True)))


def ceil_scaled(value: Union[int, float, str]) -> float:
    """
    Round a number up to its first significant digit.

    >>> print(ceil_scaled(123))
    200
    >>> print(ceil_scaled(23))
    30
    >>> print(ceil_scaled(4))
    5
    >>> print(ceil_scaled(3.21))
    4
    >>> print(ceil_scaled(0.075))
    0.08
    """
    if isinstance(value, str):
        value = float(value)
    n = 0
    if value > 1:
        while value > 10:
            value = value // 10
            n += 1
        return math.floor(value + 1) * (10 ** n)
    elif value > 0:
        while value < 1:
            value = value * 10
            n += 1
        return math.floor(value + 1) / (10 ** n)
    return value


def floor_scaled(value: Union[int, float, str]) -> float:
    """
    Round a number down to its first significant digit.

    >>> print(floor_scaled(123))
    100
    >>> print(floor_scaled(23))
    20
    >>> print(floor_scaled(4))
    3
    >>> print(floor_scaled(3.21))
    3
    >>> print(floor_scaled(0.075))
    0.07
    """
    if isinstance(value, str):
        value = float(value)
    n = 0
    if value > 1:
        while value > 10:
            value = value // 10
            n += 1
        if n == 0 and math.floor(value) == value:
            return value - 1
        return math.floor(value) * (10 ** n)
    elif value > 0:
        while value < 1:
            value = value * 10
            n += 1
        return math.ceil(value - 1) / (10 ** n)
    return value


# region x-axis funcs
def xround_func_hour(v):
    dt = datetime.fromtimestamp(v)
    minutes = dt.minute % 10
    dt = dt.replace(minute=(dt.minute // 10) * 10)
    if minutes >= 5:
        dt = dt + timedelta(minutes=10)

    return dt.timestamp()


def xround_func_day(v):
    dt = datetime.fromtimestamp(v)
    dt_start_of_hour = dt.replace(minute=0, second=0, microsecond=0)
    dt_half_hour = dt.replace(minute=30, second=0, microsecond=0)

    if dt > dt_half_hour:
        dt = dt_start_of_hour + timedelta(hours=1)
    else:
        dt = dt_start_of_hour

    return dt.timestamp()


def xround_func_week(v):
    dt = datetime.fromtimestamp(v)
    dt_start_of_day = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    dt_mid_day = dt.replace(hour=12, minute=0, second=0, microsecond=0)

    if dt > dt_mid_day:
        dt = dt_start_of_day + timedelta(days=1)
    else:
        dt = dt_start_of_day

    return dt.timestamp()


def xround_func_month(v):
    dt = datetime.fromtimestamp(v)
    dt_start_of_week = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    dt_start_of_week = dt_start_of_week - timedelta(days=dt.weekday())
    dt_half_week = dt.replace(hour=12, minute=0, second=0, microsecond=0)
    dt_half_week = dt_half_week - timedelta(days=dt.weekday())
    dt_half_week += timedelta(days=3)

    if dt > dt_half_week:
        dt = dt_start_of_week + timedelta(weeks=1)
    else:
        dt = dt_start_of_week

    return dt.timestamp()


def xformat_func_month(v: float):
    val = datetime.fromtimestamp(v)
    return val.strftime('Week %V')


def xround_func_year(v):
    dt = datetime.fromtimestamp(v)
    dt_start_of_month = dt.replace(day=1,
                                   hour=0, minute=0, second=0, microsecond=0)
    dt_half_month = dt.replace(day=16,
                               hour=0, minute=0, second=0, microsecond=0)

    if dt > dt_half_month:
        dt = (dt_start_of_month + timedelta(days=32)).replace(day=1)
    else:
        dt = dt_start_of_month

    return dt.timestamp()


XAXIS_CFG = {
    'hour': {
        'xrows': 2, 'xformat': '{}',
        'xformat_func': lambda x: datetime.fromtimestamp(x).strftime('%H:%M'),
        'xround_func': xround_func_hour
    },
    'day': {
        'xrows': 2, 'xformat': '{}',
        'xformat_func': lambda x: datetime.fromtimestamp(x).strftime('%H:%M'),
        'xround_func': xround_func_day
    },
    'week': {
        'xrows': 2, 'xformat': '{}',
        'xformat_func': lambda x: datetime.fromtimestamp(x).strftime('%d %b'),
        'xround_func': xround_func_week
    },
    'month': {
        'xrows': 2, 'xformat': '{}',
        'xformat_func': lambda x: datetime.fromtimestamp(x).strftime('Week %V'),
        'xround_func': xround_func_month
    },
    'year': {
        'xrows': 2, 'xformat': '{}',
        'xformat_func': lambda x: datetime.fromtimestamp(x).strftime('%b %Y'),
        'xround_func': xround_func_year
    },
}
# endregion x-axis funcs

# brasciichart color symbols width, 5 '\033[XXm' + 4 '\033[0m'
COLOR_RESET = 9
