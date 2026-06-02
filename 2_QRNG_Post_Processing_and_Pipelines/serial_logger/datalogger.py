import serial
import time


PORT = "COM5"
BAUDRATE = 460800

OUTPUT_FILE = "qrng.bin"
TARGET_MB = 10


target_bytes = TARGET_MB * 1024 * 1024
bytes_received = 0


def connect():

    while True:

        try:
            print("Opening serial...")
            s = serial.Serial(PORT, BAUDRATE, timeout=1)
            s.set_buffer_size(rx_size=65536)
            time.sleep(2)
            print("Connected.")
            return s

        except:
            print("Retrying...")
            time.sleep(2)


ser = connect()

start_time = time.time()


with open(OUTPUT_FILE, "ab") as f:

    print("Recording QRNG data...\n")

    while bytes_received < target_bytes:

        try:

            data = ser.read(4096)

            if data:

                f.write(data)

                bytes_received += len(data)

                elapsed = time.time() - start_time

                rate = bytes_received / elapsed / 1024

                print(
                    f"\rCollected: {bytes_received/1024/1024:.2f} MB | "
                    f"Rate: {rate:.2f} KB/s",
                    end=""
                )

        except serial.SerialException:

            print("\nUSB reconnect detected...")

            ser.close()

            ser = connect()


print("\n\nCapture complete.")