from re import fullmatch

def get_timings(line):
    # Extract data for ss and to
    pattern = r"\s*(\d+:[0-5][0-9]:[0-5][0-9],\d+)\s*-->\s*(\d+:[0-5][0-9]:[0-5][0-9],\d+)\s*$"
    match = fullmatch(pattern, line)
    # Move forward if valid timings line
    if not match:
        return ([],[])
    # Create ss and to data
    ss_data = match.group(1).replace(",",":").split(":")
    to_data = match.group(2).replace(",",":").split(":")
    # Trim milliseconds to be less than 1000
    ss_data[-1] = ss_data[-1][:3]
    to_data[-1] = to_data[-1][:3]
    # Define ss and to
    ss = list(map(int, ss_data))
    to = list(map(int, to_data))
    # Return the values
    return (ss,to)

