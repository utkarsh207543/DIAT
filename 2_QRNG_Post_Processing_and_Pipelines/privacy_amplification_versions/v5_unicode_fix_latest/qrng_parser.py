"""
QRNG Data Parser
Handles parsing of time-tagged photon detection data from QRNG files.
"""

class QRNGParser:
    def __init__(self):
        pass
        
    def parse_qrng_file(self, filename: str) -> str:
        """
        Parse QRNG time-tagged data file.
        
        Args:
            filename: Path to QRNG data file
            
        Returns:
            Binary string of chronologically ordered detection events
        """
        ch1_times = []
        ch2_times = []
        
        try:
            with open(filename, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('%'):
                        continue
                        
                    values = line.split()
                    while len(values) < 3:
                        values.append(None)
                        
                    try:
                        ch1 = int(values[0]) if values[0] is not None else None
                        ch2 = int(values[1]) if values[1] is not None else None
                    except (ValueError, TypeError):
                        print(f"Warning: Invalid data on line {line_num}: {line}")
                        continue
                        
                    if ch1 is not None:
                        ch1_times.append((ch1, '0'))
                    if ch2 is not None:
                        ch2_times.append((ch2, '1'))
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"QRNG data file not found: {filename}")
        except Exception as e:
            raise Exception(f"Error parsing QRNG file: {e}")
            
        # Sort all events chronologically
        all_events = sorted(ch1_times + ch2_times, key=lambda x: x[0])
        bitstring = ''.join(bit for _, bit in all_events)
        
        print(f"📊 Parsed {len(bitstring)} bits from {len(all_events)} detection events")
        print(f"   Channel 1 events: {len(ch1_times)}")
        print(f"   Channel 2 events: {len(ch2_times)}")
        
        return bitstring
