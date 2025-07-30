import argparse
import sys
from .macsanity import MacSanity, convert_macs_in_file

def main():
    help_dict = {
        "colon": "Colon-separated format. e.g., ab:12:cd:34:ef:56.",
        "dot": "Cisco-style dot notation. e.g., abcd.ef12.3456.",
        "dash": "Hyphen-separated format. Because it looks serious.",
        "ddash": "Double-dash separated. Very 'enterprise'.",
        "space": "Space-separated, for all the weird forms out there.",
        "blank": "Just the MAC. Naked. No delimiters.",
        "binary": "8-bit binary. For those who love pain.",
        "compact": "Base64. Not sure why. But here it is.",
        "eui64": "Cisco’s EUI-64 style. Because, Cisco.",
        "bpf": "Berkeley Packet Filter escape-hell. \\xab\\xcd style.",
        "reverse": "Reversed MAC. Just because.",
        "upsidedown": "Flips the MAC upside down. Your network... but spooky.",
    }

    available_formats = list(help_dict.keys())

    parser = argparse.ArgumentParser(
        description="macsanity — Format MAC addresses in any style you can imagine. Or fear."
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        'mac_address',
        type=str,
        nargs='?',
        help="The MAC address to format (e.g., AB:CD:EF:12:34:56)."
    )

    group.add_argument(
        '--file',
        type=str,
        help="Path to a file to convert all MAC addresses within."
    )

    parser.add_argument(
        '-f', '--format',
        type=str,
        choices=available_formats,
        help="Choose a format to output. Use --help to see available formats."
    )

    parser.add_argument(
        '-u', '--uppercase',
        action='store_true',
        help="SHOUT your MAC in uppercase."
    )

    parser.add_argument(
        '-l', '--lowercase',
        action='store_true',
        help="whisper your MAC in lowercase."
    )

    args = parser.parse_args()

    def style_output(text):
        return text.upper() if args.uppercase else text.lower() if args.lowercase else text

    if args.file:
        if not args.format:
            print("❌ You must specify a format when using --file.")
            sys.exit(1)
        convert_macs_in_file(args.file, target_format=args.format)
    else:
        formatter = MacSanity(args.mac_address)
        if args.format:
            result = getattr(formatter, args.format, None)
            if result is not None:
                print(style_output(result))
            else:
                print(f"Invalid format '{args.format}'. Run with --help to see what's possible.")
        else:
            print(f"\nHere’s how we can mess with your MAC today - remember to use '-f <format>':\n")
            for fmt in available_formats:
                result = getattr(formatter, fmt)
                print(f"{fmt:12}: {style_output(result)}  # {help_dict[fmt]}")
            print("\nNote: This was handcrafted by MAC artists in a certified bit-based facility.")

if __name__ == "__main__":
    main()
