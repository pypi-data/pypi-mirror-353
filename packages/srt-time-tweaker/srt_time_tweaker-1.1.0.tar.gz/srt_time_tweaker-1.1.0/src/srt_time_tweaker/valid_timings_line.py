from re import fullmatch

def valid_timings_line(line):
    # Define pattern to match
    pattern = r"\s*(\d+:[0-5][0-9]:[0-5][0-9],\d+)\s*-->\s*(\d+:[0-5][0-9]:[0-5][0-9],\d+)\s*$"
    match = fullmatch(pattern, line)
    # return False if match unsuccessful
    if not match:
        return False
    # return True if match successful
    return True

