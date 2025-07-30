from datetime import timedelta

from ..types.color import Color
from ..core.module_property import module_property
from ..utils.export import export

from .. import lib
from .timeframe import in_seconds

_visible_bars = 20

bg_color = Color('#000000')
fg_color = Color('#FFFFFF')

is_heikinashi = False
is_kagi = False
is_linebreak = False
is_pnf = False
is_range = False
is_renko = False
is_standard = True


# noinspection PyProtectedMember
@export
@module_property
def left_visible_bar_time() -> int:
    return int((lib._datetime - timedelta(seconds=in_seconds(lib.syminfo.period) * _visible_bars)).timestamp() * 1000)


# noinspection PyProtectedMember
@export
@module_property
def right_visible_bar_time() -> int:
    return int(lib._datetime.timestamp() * 1000)
