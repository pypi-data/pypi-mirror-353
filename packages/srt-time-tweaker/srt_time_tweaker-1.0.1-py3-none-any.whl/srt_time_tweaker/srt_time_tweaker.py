from re import match
from datetime import timedelta


def srt_time_tweaker(srt_input, srt_output="output.srt", hours=0, minutes=0, seconds=0, milliseconds=0, duration = None, subtract_delay=False, ignore_negative_error=False):
    # Validate the input duration from duration arg if provided else from individual h,m,s,ms args
    if duration is not None:
        if not match(r"\d+:[0-5][0-9]:[0-5][0-9],\d+$", duration):
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
        # Defining pattern to match with an actual timings line
        pattern = r"\s*(\d+:[0-5][0-9]:[0-5][0-9],\d+)\s*-->\s*(\d+:[0-5][0-9]:[0-5][0-9],\d+)\s*$"
        line = lines[i].strip()
        matching = match(pattern, line)
        if not matching:
            continue
        # Move forward only if the pattern is matched
        ss_data = matching.group(1).replace(",",":").split(":")
        to_data = matching.group(2).replace(",",":").split(":")
        # Validate hours and milliseconds to be less than 1000
        ss_data[-1] = ss_data[-1][:6]
        to_data[-1] = to_data[-1][:6]
        ss = list(map(int, ss_data))
        to = list(map(int, to_data))
        if ss[0]>1000 or to[0]>1000:
            continue
        # Move forward only if the line is a perfect timing block
        ss_td = timedelta(hours=ss[0], minutes=ss[1], seconds=ss[2], milliseconds=ss[3])
        to_td = timedelta(hours=to[0], minutes=to[1], seconds=to[2], milliseconds=to[3])
        if subtract_delay:
            ss_new_td = ss_td - delay_td
            to_new_td = to_td - delay_td
        else:
            ss_new_td = ss_td + delay_td
            to_new_td = to_td + delay_td
        # Define ss and to delay as timedelta
        ss_h = ss_new_td.days*24 + ss_new_td.seconds//3600
        ss_h = f"0{ss_h}" if ss_h<10 else f"{ss_h}"
        ss_m = (ss_new_td.seconds%3600)//60
        ss_s = ss_new_td.seconds%60
        ss_ms = ss_new_td.microseconds//1000
        ss_new = f"{ss_h}:{ss_m:02}:{ss_s:02},{ss_ms:03}"
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

