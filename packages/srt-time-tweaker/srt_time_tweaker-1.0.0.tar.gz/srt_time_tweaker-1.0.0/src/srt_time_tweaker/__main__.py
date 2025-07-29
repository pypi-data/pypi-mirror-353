import argparse
from .srt_time_tweaker import srt_time_tweaker as srtt

def main():
    # Main argparse
    parser = argparse.ArgumentParser(
        prog="srt-time-tweaker",
        description="A no-frills solution for fixing subtitle synchronization issues in .srt files by precisely shifting all subtitle timestamps forward or backward using configurable time delays."
    )
    # Adding arguments
    parser.add_argument(
        "input", 
        help="Path to input .srt subtitle file"
    )
    parser.add_argument(
        "-o", 
        "--output", 
        default="output.srt", 
        help="Path to output .srt file"
    )
    parser.add_argument(
        "-H", 
        "--hours", 
        type=int, 
        default=0, 
        help="Hours to shift"
    )
    parser.add_argument(
        "-M", 
        "--minutes", 
        type=int, 
        default=0, 
        help="Minutes to shift"
    )
    parser.add_argument(
        "-S", 
        "--seconds", 
        type=int, 
        default=0, 
        help="Seconds to shift"
    )
    parser.add_argument(
        "-ms", 
        "--milliseconds", 
        type=int, 
        default=0, 
        help="Milliseconds to shift"
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=str,
        help="Time delay in \"HH:MM:SS,ms\" format (overrides hours, minutes, seconds, milliseconds)",
    )
    parser.add_argument(
        "--subtract",
        action="store_true",
        help="Subtract the delay from timestamps instead of adding",
    )
    parser.add_argument(
        "--ignore-negative",
        action="store_true",
        help="Ignore negative timing errors instead of raising exceptions (while subtract)",
    )
    # Finalising argparse
    args = parser.parse_args()
    # Calling srt_time_tweaker
    srtt(
        srt_input=args.input,
        srt_output=args.output,
        hours=args.hours,
        minutes=args.minutes,
        seconds=args.seconds,
        milliseconds=args.milliseconds,
        duration=args.duration,
        subtract_delay=args.subtract,
        ignore_negative_error=args.ignore_negative,
    )
    # Success message
    print(f"Success: Output file saved to \"{args.output or "output.srt"}\"")

# CLI entry point
if __name__ == "__main__":
    main()

