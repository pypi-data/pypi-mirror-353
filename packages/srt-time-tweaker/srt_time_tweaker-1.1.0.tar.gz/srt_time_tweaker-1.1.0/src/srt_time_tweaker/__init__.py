'''
srt_time_tweaker - A no-frills solution for fixing subtitle synchronization issues in SRT (SubRip Subtitle) files by precisely shifting all subtitle timestamps forward or backward using configurable time delays.
Author : भाग्य ज्योति (Bhagya Jyoti)
License : Apache License Version 2.0
Homepage: https://github.com/BhagyaJyoti22006/srt-time-tweaker
'''

from .srt_time_tweaker import srt_time_tweaker, valid_timings_line, get_timings
from .valid_timings_line import valid_timings_line
from .get_timings import get_timings

__all__ = ["srt_time_tweaker", "valid_timings_line", "get_timings"]
__version__ = "1.1.0"

