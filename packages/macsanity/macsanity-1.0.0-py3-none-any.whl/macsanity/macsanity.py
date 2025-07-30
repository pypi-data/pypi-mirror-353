import re
import base64
import asyncio
from typing import Optional

class MacSanity:
    r"""
    A class to format MAC addresses into various notations.

    But really tho, it's more about keeping something stupid simple.
    Cleans the input MAC address and provides multiple formatting options —
    pretty much as many as there are vendors making network equipment.

    Async-compatible via optional `async_format_mac()` method.
    Because seriously... who has time to wait anymore?
    """

    def __init__(self, mac_address: str):
        r"""
        Initialize a MacFormatter object by cleaning and validating the MAC address.

        Args:
            mac_address (str): A MAC address in any common format -
            I seriously don't know what a common format is these days though. ¯\_(ツ)_/¯ 

        Raises:
            ValueError: If the MAC address does not contain exactly 12 hexadecimal characters.
            Also — please reach out if you've encountered a vendor using emojis in MAC addresses.
            I wouldn't even be surprised at this point...
        """
        self.original = mac_address
        self.mac = self._normalize_mac(mac_address)

    @staticmethod
    def _normalize_mac(mac: str) -> str:
        """
        Strip non-hex characters and validate the resulting MAC address.

        Args:
            mac (str): Raw MAC address string — could be from exports, logs, or 
            some random clipboard paste that looked like it might be a MAC.
    
        Returns:
            str: Normalized lowercase MAC address without delimiters.
    
        Raises:
            ValueError: If the cleaned MAC address does not contain exactly 12 hex digits.
            At that point, you're probably looking at a serial number. Or a curse.
        """
        mac_clean = ''.join(re.findall(r'[0-9a-fA-F]', mac))
        if not re.fullmatch(r'[0-9a-fA-F]{12}', mac_clean):
            raise ValueError("Invalid MAC address. Expected 12 hex digits.")
        return mac_clean.lower()

    def format_mac(self, delimiter: str, segment_length: int, length_mod: int = 0, step_size: Optional[int] = None) -> str:
        r"""
        Format the MAC address according to specified delimiter and segment settings.
    
        Args:
            delimiter (str): Delimiter between each segment (e.g., ':', '-', '.').
            segment_length (int): Number of characters in each segment.
            length_mod (int): Adjustment to exclude characters at the end (default: 0).
            step_size (int, optional): Step size for segment slicing (default: same as segment_length).
    
        Returns:
            str: Formatted MAC address.
    
        Example:
            Want to match Cisco’s dot-style? Use '.', 4, 3.  
            Aruba likes dashes? Fine. Use '-', 2.  
            Or invent your own format — it’s what everyone else seems to be doing. ¯\_(ツ)_/¯

            Feeling unhinged?
            format_mac('🦆', 1)  →  a🦆b🦆1🦆2🦆c🦆d🦆3🦆4🦆e🦆f🦆5🦆6
    
        Notes:
            This function assumes you've already normalized the MAC.
            We're not here to police your delimiters.
            But there clearly should be someone hired to do just that.
        """
        step_size = step_size or segment_length
        return delimiter.join(
            self.mac[i:i + segment_length] for i in range(0, len(self.mac) - length_mod, step_size)
        )

    @property
    def dot(self):
        """Cisco's dot format. Because... of course they wanted to be special. e.g., abcd.ef12.3456"""
        return self.format_mac('.', 4, 3)

    @property
    def colon(self):
        """Classic colon-separated style. This one's actually decent. e.g., ab:12:cd:34:ef:56"""
        return self.format_mac(':', 2)

    @property
    def dash(self):
        """Aruba probably uses this. Or maybe just your boss. e.g., ab-12-cd-34-ef-56"""
        return self.format_mac('-', 2)

    @property
    def ddash(self):
        """For those who think double-dash looks professional. e.g., ab12-cd34-ef56"""
        return self.format_mac('-', 4)

    @property
    def space(self):
        """The format you use when pasting into that one weird form on that one ancient web GUI. e.g., ab 12 cd 34 ef 56"""
        return self.format_mac(' ', 2)

    @property
    def blank(self):
        """No delimiter, just vibes. e.g., ab12cd34ef56"""
        return self.mac

    @property
    def binary(self):
        """Binary output. Because nothing says 'human-friendly' like 96 bits of eye pain."""
        return ' '.join(format(int(c, 16), '08b') for c in re.findall(r'.{2}', self.mac))

    @property
    def compact(self):
        """Base64-encoded MAC. Because maybe you wanted to confuse someone. Or a QR code."""
        return base64.b64encode(bytes.fromhex(self.mac)).decode('utf-8')

    @property
    def eui64(self):
        """Cisco's EUI-64 format. Just... insert 'fffe' in the middle. Apparently that's a thing."""
        eui64_mac = f"{self.mac[:6]}fffe{self.mac[6:]}"
        return '.'.join([eui64_mac[i:i + 4] for i in range(0, len(eui64_mac), 4)])

    @property
    def bpf(self):
        """Berkeley Packet Filter style — or as I call it: 'escape hell'. e.g., \\xab\\x12\\xcd..."""
        return '\\x' + '\\x'.join(self.mac[i:i + 2] for i in range(0, len(self.mac), 2))

    @property
    def reverse(self):
        """Reversed byte order. For those special cases where 'forward' is just too predictable."""
        return self.mac[::-1]

    @property
    def upsidedown(self):
        """I mean, I wouldn't be surprised if it lead to this – at some point..."""

        def flip_text(text: str) -> str:
            flip_map = str.maketrans(
                "abcdefghijklmnopqrstuvwxyz0123456789",
                "ɐqɔpǝɟƃɥᴉɾʞʅɯuodbɹsʇnʌʍxʎz0ƖᄅƐㄣϛ9ㄥ86"
            )
            return text.lower().translate(flip_map)  # <-- flip only, don't reverse

        if '.' in self.original:
            delimiter = '.'
            segments = self.original.split('.')
        elif ':' in self.original:
            delimiter = ':'
            segments = self.original.split(':')
        elif '-' in self.original:
            delimiter = '-'
            segments = self.original.split('-')
        elif ' ' in self.original:
            delimiter = ' '
            segments = self.original.split(' ')
        else:
            delimiter = ''
            segments = [self.mac[i:i+2] for i in range(0, len(self.mac), 2)]

        flipped_segments = [flip_text(seg) for seg in segments]
        return delimiter.join(flipped_segments)

    async def async_format_mac(self, delimiter: str, segment_length: int, length_mod: int = 0, step_size: Optional[int] = None) -> str:
        """
        Async wrapper for `format_mac`.
    
        Because your app is async, your network is slow, and your patience is finite.
        We offload the sync formatting so you can await your MACs like a civilized human.
    
        Returns:
            str: Formatted MAC address (same logic as sync, just... calmer).
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.format_mac, delimiter, segment_length, length_mod, step_size)

def convert_macs_in_file(input_path: str, target_format: str):
    """
    Finds all MAC addresses in a file and replaces them with a specified format.
    Overwrites the original file with the updated content.
    """
    mac_pattern = re.compile(r'(?<![\w])(?:[0-9a-fA-F]{2}[-:\.\s]?){5}[0-9a-fA-F]{2}(?![\w])|[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}')

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    def format_found_mac(mac_str):
        try:
            formatter = MacFormatter(mac_str)
            return getattr(formatter, target_format)
        except Exception:
            return mac_str

    updated_lines = []
    for line in lines:
        updated_line = line
        for match in re.finditer(mac_pattern, line):
            raw_mac = match.group()
            formatted_mac = format_found_mac(raw_mac)
            updated_line = updated_line.replace(raw_mac, formatted_mac)
        updated_lines.append(updated_line)

    with open(input_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

    print(f"✅ Converted all MACs in '{input_path}' to format: {target_format}")
