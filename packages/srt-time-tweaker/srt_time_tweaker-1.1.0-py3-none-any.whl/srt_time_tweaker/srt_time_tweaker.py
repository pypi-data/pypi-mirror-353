from re import fullmatch
from datetime import timedelta
from .valid_timings_line import valid_timings_line
from .get_timings import get_timings

def srt_time_tweaker(srt_input, srt_output="output.srt", hours=0, minutes=0, seconds=0, milliseconds=0, duration = None, subtract_delay=False, ignore_negative_error=False):
    # Validate the input duration from duration arg if provided else from individual h,m,s,ms args
    if duration is not None:
        if not fullmatch(r"\d+:[0-5][0-9]:[0-5][0-9],\d+$", duration):
            raise ValueError(f"Wrong format for duration={duration}; duration must follow \"HH:MM:SS,ms\" format.")
        d = list(map(int, duration.replace(",",":").split(":")))
        h,m,s,ms = d[0], d[1], d[2], d[3]
    else:
        h,m,s,ms = hours, minutes, seconds, milliseconds
    if h>=1000:
        raise ValueError(f"Wrong hour input; hour must be less than 1000; hours={h}")
    if ms>=1000:
        raise ValueError(f"Wrong millisecond input; millisecond must be less than 1000; milliseconds={ms}")
    delay_td = timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms)
    # Read and load input srt file
    lines = []
    with open(srt_input, "r", encoding="utf-8") as file:
        for line in file:
            lines.append(line)
    # Process timings in input and convert to new timings based on delay
    for i in range(len(lines)):
        line = lines[i].strip()
        # Move forward only if the line is a valid timings line
        if not valid_timings_line(line):
            continue
        # Extract ss and to from timings line
        ss,to = get_timings(line)
        # Move forward only if hours are less than 1000
        if ss[0]>1000 or to[0]>1000:
            continue
        # Create timedelta objects for ss and to
        ss_td = timedelta(hours=ss[0], minutes=ss[1], seconds=ss[2], milliseconds=ss[3])
        to_td = timedelta(hours=to[0], minutes=to[1], seconds=to[2], milliseconds=to[3])
        if subtract_delay:
            ss_new_td = ss_td - delay_td
            to_new_td = to_td - delay_td
        else:
            ss_new_td = ss_td + delay_td
            to_new_td = to_td + delay_td
        # Define ss delay as timedelta
        ss_h = ss_new_td.days*24 + ss_new_td.seconds//3600
        ss_h = f"0{ss_h}" if ss_h<10 else f"{ss_h}"
        ss_m = (ss_new_td.seconds%3600)//60
        ss_s = ss_new_td.seconds%60
        ss_ms = ss_new_td.microseconds//1000
        ss_new = f"{ss_h}:{ss_m:02}:{ss_s:02},{ss_ms:03}"
        # Define to delay as timedelta
        to_h = to_new_td.days*24 + to_new_td.seconds//3600
        to_h = f"0{to_h}" if to_h<10 else f"{to_h}"
        to_m = (to_new_td.seconds%3600)//60
        to_s = to_new_td.seconds%60
        to_ms = to_new_td.microseconds//1000
        to_new = f"{to_h}:{to_m:02}:{to_s:02},{to_ms:03}"
        # Form the final line to write to output
        lines[i] = f"{ss_new} --> {to_new}\n"
        # Validate negative error if any
        if "-" in str(ss_new) or "-" in str(to_new):
            if not ignore_negative_error:
                raise ValueError(f"Negative time applied due to delay duration more than input duration; output line forming as:- \n{lines[i]}")
        continue
    # Write to output srt file
    with open(srt_output, "w", encoding="utf-8") as file:
        for i in lines:
            file.write(i)
    # Return and exit code
    return

