#!/usr/bin/env python3
"""
PYNQ-Z2 Timetagger Control Script
Communicates with the FPGA via UART to configure and read data
"""

import serial
import struct
import time
import argparse
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional
import threading
import queue
import csv
from datetime import datetime


class TimetagController:
    def __init__(self, port: str = 'COM7', baudrate: int = 115200):
        """Initialize connection to timetagger"""
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1.0)
            time.sleep(0.1)  # Allow connection to stabilize
            print(f"Connected to {port} at {baudrate} baud")
        except serial.SerialException as e:
            print(f"Failed to connect to {port}: {e}")
            raise

        self.data_queue = queue.Queue()
        self.stop_reading = False

    def __del__(self):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()

    def write_register(self, addr: int, value: int) -> int:
        """Write to a register and return the read-back value"""
        cmd = struct.pack('<BBHHBBBB',
                          0xAA,  # Magic
                          0x01,  # Write command
                          addr & 0xFF,  # Address low
                          (addr >> 8) & 0xFF,  # Address high
                          value & 0xFF,  # Value bytes
                          (value >> 8) & 0xFF,
                          (value >> 16) & 0xFF,
                          (value >> 24) & 0xFF)

        self.ser.write(cmd)
        response = self.ser.read(4)

        if len(response) != 4:
            raise RuntimeError(f"Invalid response length: {len(response)}")

        return struct.unpack('<I', response)[0]

    def read_register(self, addr: int) -> int:
        """Read from a register"""
        cmd = struct.pack('<BBHHBBBB',
                          0xAA,  # Magic
                          0x00,  # Read command
                          addr & 0xFF,  # Address low
                          (addr >> 8) & 0xFF,  # Address high
                          0, 0, 0, 0)  # Dummy data

        self.ser.write(cmd)
        response = self.ser.read(4)

        if len(response) != 4:
            raise RuntimeError(f"Invalid response length: {len(response)}")

        return struct.unpack('<I', response)[0]

    def get_version(self) -> int:
        """Get hardware version"""
        return self.read_register(0x0001)

    def get_clockrate(self) -> int:
        """Get clock rate in Hz"""
        return self.read_register(0x0002)

    def reset_system(self):
        """Reset the timetagger system"""
        print("Resetting system...")
        # Disable all channels
        self.write_register(0x0004, 0x0000)  # Strobe channels
        self.write_register(0x0005, 0x0000)  # Delta channels

        # Reset counter and capture
        self.write_register(0x0003, 0x0004)  # Reset counter
        time.sleep(0.01)
        self.write_register(0x0003, 0x0000)  # Clear reset

        # Clear FIFO
        self.write_register(0x0008, 0x0001)  # Clear FIFO
        time.sleep(0.01)
        self.write_register(0x0008, 0x0000)  # Clear FIFO reset
        print("System reset complete")

    def start_capture(self, strobe_channels: int = 0x0F):
        """Start data capture"""
        print(f"Starting capture with channels: 0x{strobe_channels:02X}")
        self.write_register(0x0004, strobe_channels)  # Enable strobe channels
        self.write_register(0x0003, 0x0003)  # Start counter and capture

    def stop_capture(self):
        """Stop data capture"""
        print("Stopping capture...")
        self.write_register(0x0003, 0x0002)  # Stop capture, reset counter
        self.write_register(0x0003, 0x0000)  # Clear reset

    def get_record_count(self) -> int:
        """Get number of records captured"""
        return self.read_register(0x0006)

    def get_lost_count(self) -> int:
        """Get number of lost records"""
        return self.read_register(0x0007)

    def read_data_stream(self, num_records: int = 100, timeout: float = 1.0) -> List[Tuple[int, int, bool, bool, bool]]:
        """
        Read data stream from UART
        Returns list of tuples: (timestamp, channels, record_type, wraparound, sample_lost)
        """
        records = []
        start_time = time.time()

        for _ in range(num_records):
            if time.time() - start_time > timeout:
                break

            # Read 6 bytes per record
            data = self.ser.read(6)
            if len(data) != 6:
                break

            # Unpack 48-bit record
            record = struct.unpack('>BBBBBB', data)

            # Reconstruct 48-bit value
            value = 0
            for i, byte in enumerate(record):
                value |= (byte << (8 * (5 - i)))

            # Extract fields
            timestamp = value & 0xFFFFFFFFF  # 36 bits
            channels = (value >> 36) & 0xF  # 4 bits
            record_type = bool((value >> 45) & 1)  # 1 bit (0=strobe, 1=delta)
            wraparound = bool((value >> 46) & 1)  # 1 bit
            sample_lost = bool((value >> 47) & 1)  # 1 bit

            records.append((timestamp, channels, record_type, wraparound, sample_lost))

        return records

    def continuous_read_thread(self):
        """Thread function for continuous data reading"""
        while not self.stop_reading:
            try:
                records = self.read_data_stream(50, timeout=0.1)
                if records:
                    for record in records:
                        self.data_queue.put(record)
                time.sleep(0.001)  # Small delay to prevent CPU overload
            except Exception as e:
                print(f"Error in continuous read: {e}")
                break

    def start_continuous_read(self):
        """Start continuous data reading in background thread"""
        self.stop_reading = False
        self.read_thread = threading.Thread(target=self.continuous_read_thread)
        self.read_thread.daemon = True
        self.read_thread.start()
        print("Started continuous data reading")

    def stop_continuous_read(self):
        """Stop continuous data reading"""
        self.stop_reading = True
        if hasattr(self, 'read_thread'):
            self.read_thread.join(timeout=1.0)
        print("Stopped continuous data reading")

    def get_queued_data(self) -> List[Tuple[int, int, bool, bool, bool]]:
        """Get all data from the queue"""
        records = []
        while not self.data_queue.empty():
            try:
                records.append(self.data_queue.get_nowait())
            except queue.Empty:
                break
        return records

    def print_status(self):
        """Print system status"""
        print(f"Hardware Version: {self.get_version()}")
        print(f"Clock Rate: {self.get_clockrate():,} Hz")
        print(f"Records Captured: {self.get_record_count():,}")
        print(f"Records Lost: {self.get_lost_count():,}")


def save_data_to_csv(records: List[Tuple], filename: str):
    """Save records to CSV file"""
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Timestamp', 'Channels', 'RecordType', 'Wraparound', 'SampleLost', 'TimeNS'])

        for ts, ch, rtype, wrap, lost in records:
            # Convert timestamp to nanoseconds (assuming 125MHz clock = 8ns resolution)
            time_ns = ts * 8
            type_str = 'Delta' if rtype else 'Strobe'
            writer.writerow([ts, f'0x{ch:02X}', type_str, wrap, lost, time_ns])

    print(f"Saved {len(records)} records to {filename}")


def analyze_data(records: List[Tuple]):
    """Analyze captured data and print statistics"""
    if not records:
        print("No data to analyze")
        return

    print(f"\n=== Data Analysis ===")
    print(f"Total records: {len(records)}")

    # Separate by type
    strobe_records = [r for r in records if not r[2]]
    delta_records = [r for r in records if r[2]]

    print(f"Strobe events: {len(strobe_records)}")
    print(f"Delta events: {len(delta_records)}")

    # Count lost samples
    lost_count = sum(1 for r in records if r[4])
    print(f"Lost samples: {lost_count}")

    # Channel distribution
    channel_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for _, ch, _, _, _ in records:
        for bit in range(4):
            if ch & (1 << bit):
                channel_counts[bit] += 1

    print(f"\nChannel distribution:")
    for ch in range(4):
        print(f"  Channel {ch}: {channel_counts[ch]} events")

    # Time analysis
    if len(records) > 1:
        timestamps = [r[0] for r in records]
        time_diffs = np.diff(timestamps)
        time_diffs_ns = time_diffs * 8  # Convert to nanoseconds

        print(f"\nTiming analysis:")
        print(f"  Min interval: {np.min(time_diffs_ns):.1f} ns")
        print(f"  Max interval: {np.max(time_diffs_ns):.1f} ns")
        print(f"  Mean interval: {np.mean(time_diffs_ns):.1f} ns")
        print(f"  Std interval: {np.std(time_diffs_ns):.1f} ns")


def plot_data(records: List[Tuple], save_plot: bool = False):
    """Plot captured data"""
    if not records:
        print("No data to plot")
        return

    try:
        import matplotlib.pyplot as plt

        # Extract data
        timestamps = np.array([r[0] for r in records]) * 8  # Convert to nanoseconds
        channels = [r[1] for r in records]

        # Create subplot for each channel
        fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
        fig.suptitle('Timetagger Data - Channel Activity')

        colors = ['red', 'blue', 'green', 'orange']

        for ch in range(4):
            # Find events for this channel
            ch_events = []
            ch_times = []
            for i, (ts_ns, ch_mask, _, _, _) in enumerate(zip(timestamps, channels, *zip(*records)[2:])):
                if ch_mask & (1 << ch):
                    ch_events.append(1)
                    ch_times.append(ts_ns)
                else:
                    ch_events.append(0)

            if ch_times:
                axes[ch].scatter(ch_times, [1] * len(ch_times),
                                 c=colors[ch], alpha=0.7, s=10)

            axes[ch].set_ylabel(f'Ch {ch}')
            axes[ch].set_ylim(0, 1.5)
            axes[ch].grid(True, alpha=0.3)

        axes[-1].set_xlabel('Time (ns)')
        plt.tight_layout()

        if save_plot:
            filename = f"timetag_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Plot saved as {filename}")

        plt.show()

    except ImportError:
        print("Matplotlib not available for plotting")


def main():
    parser = argparse.ArgumentParser(description='PYNQ-Z2 Timetagger Control')
    parser.add_argument('--port', default='COM7', help='Serial port')
    parser.add_argument('--baudrate', type=int, default=115200, help='Baud rate')
    parser.add_argument('--duration', type=float, default=1.0, help='Capture duration (seconds)')
    parser.add_argument('--channels', type=int, default=0x0F, help='Channel mask (hex)')
    parser.add_argument('--continuous', action='store_true', help='Continuous capture mode')
    parser.add_argument('--save-csv', action='store_true', help='Save data to CSV file')
    parser.add_argument('--plot', action='store_true', help='Plot captured data')
    parser.add_argument('--save-plot', action='store_true', help='Save plot to file')

    args = parser.parse_args()

    try:
        # Connect to timetagger
        # On Windows, you may need to determine the correct COM port in Device Manager
        tagger = TimetagController(args.port, args.baudrate)

        # Print initial status
        print("=== PYNQ-Z2 Timetagger ===")
        tagger.print_status()
        print()

        # Reset and configure
        tagger.reset_system()

        if args.continuous:
            print("Starting continuous capture mode...")
            print("Press Ctrl+C to stop")

            tagger.start_capture(args.channels)
            tagger.start_continuous_read()

            try:
                while True:
                    time.sleep(1)
                    records = tagger.get_queued_data()
                    if records:
                        print(f"Received {len(records)} records")
                        # Print last few records
                        for record in records[-5:]:
                            ts, ch, rtype, wrap, lost = record
                            type_str = "Delta" if rtype else "Strobe"
                            print(f"  {ts:10d}  0x{ch:02X}  {type_str:6s}  {wrap}  {lost}")

            except KeyboardInterrupt:
                print("\nStopping continuous capture...")
                tagger.stop_continuous_read()
                tagger.stop_capture()

                # Get any remaining data
                final_records = tagger.get_queued_data()
                if final_records:
                    print(f"Final batch: {len(final_records)} records")

        else:
            print(f"Starting capture for {args.duration} seconds...")
            print(f"Enabled channels: 0x{args.channels:02X}")

            # Start capture
            tagger.start_capture(args.channels)

            # Collect data
            start_time = time.time()
            all_records = []

            while time.time() - start_time < args.duration:
                records = tagger.read_data_stream(100)
                all_records.extend(records)
                if records:
                    print(f"Read {len(records)} records...")
                time.sleep(0.01)

            # Stop capture
            tagger.stop_capture()

            # Print results
            print(f"\nCaptured {len(all_records)} records")

            if all_records:
                print("\nFirst 10 records:")
                print("Timestamp    Ch  Type    Wrap  Lost")
                print("-" * 37)

                for i, (ts, ch, rtype, wrap, lost) in enumerate(all_records[:10]):
                    type_str = "Delta" if rtype else "Strobe"
                    print(f"{ts:10d}  {ch:02X}  {type_str:6s}  {wrap:1d}     {lost:1d}")

                # Analyze data
                analyze_data(all_records)

                # Save to CSV if requested
                if args.save_csv:
                    filename = f"timetag_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    save_data_to_csv(all_records, filename)

                # Plot data if requested
                if args.plot or args.save_plot:
                    plot_data(all_records, args.save_plot)

        # Final status
        print("\nFinal status:")
        tagger.print_status()

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
