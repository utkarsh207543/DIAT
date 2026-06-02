import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import serial
import serial.tools.list_ports
import threading
import datetime
import os

# ==============================
# CONFIGURATION
# ==============================
BAUD_RATE = 2000000
DEFAULT_FOLDER = "qrng_logs"

if not os.path.exists(DEFAULT_FOLDER):
    os.makedirs(DEFAULT_FOLDER)


# ==============================
# SERIAL READER THREAD
# ==============================
class SerialReader:

    def __init__(self, port, textbox, save_folder):
        self.port = port
        self.textbox = textbox
        self.save_folder = save_folder
        self.running = False
        self.ser = None
        self.file = None

    def start(self):

        try:
            self.ser = serial.Serial(self.port, BAUD_RATE)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"random_{timestamp}.txt"

            filepath = os.path.join(self.save_folder, filename)

            self.file = open(filepath, "w")

            self.running = True

            threading.Thread(target=self.read_serial, daemon=True).start()

            messagebox.showinfo("Logging Started",
                                f"Saving data to:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Serial Error", str(e))

    def read_serial(self):

        while self.running:

            try:
                line = self.ser.readline().decode(errors="ignore").strip()

                if line:
                    self.textbox.insert(tk.END, line + "\n")
                    self.textbox.see(tk.END)

                    if self.file:
                        self.file.write(line + "\n")

            except:
                break

    def stop(self):

        self.running = False

        if self.ser:
            self.ser.close()

        if self.file:
            self.file.close()


# ==============================
# MAIN GUI
# ==============================
class QRNG_GUI:

    def __init__(self, root):

        self.root = root
        self.root.title("TURN-ON TRANSIENT QUANTUM RANDOM GENERATOR")
        self.root.geometry("820x520")
        self.root.configure(bg="#f4f6f7")

        self.reader = None

        self.save_folder = DEFAULT_FOLDER

        self.setup_ui()


    # ==============================
    # UI LAYOUT
    # ==============================

    def setup_ui(self):

        header = tk.Label(
            self.root,
            text="TURN-ON TRANSIENT QUANTUM RANDOM GENERATOR",
            font=("Segoe UI", 16, "bold"),
            bg="#f4f6f7"
        )
        header.pack(pady=(10, 0))

        subtitle = tk.Label(
            self.root,
            text="Developed at DRDO–DIAT Pune | Author: Utkarsh Kumar Singh",
            font=("Segoe UI", 10),
            bg="#f4f6f7"
        )
        subtitle.pack(pady=(0, 8))


        # ==============================
        # LOGO ROW
        # ==============================

        logo_frame = tk.Frame(self.root, bg="#f4f6f7")
        logo_frame.pack(pady=5)

        try:
            diat_img = Image.open("DIAT.png")
            diat_img = diat_img.resize((95, 95))
            self.diat_logo = ImageTk.PhotoImage(diat_img)

            drdo_img = Image.open("DRDO.png")
            drdo_img = drdo_img.resize((95, 95))
            self.drdo_logo = ImageTk.PhotoImage(drdo_img)

            tk.Label(logo_frame, image=self.diat_logo, bg="#f4f6f7").grid(row=0, column=0, padx=20)
            tk.Label(logo_frame, image=self.drdo_logo, bg="#f4f6f7").grid(row=0, column=1, padx=20)

        except Exception as e:
            print("Logo load error:", e)


        # ==============================
        # CONTROL PANEL
        # ==============================

        control_panel = tk.Frame(self.root, bg="#f4f6f7")
        control_panel.pack(pady=8)

        tk.Label(control_panel,
                 text="Select COM Port:",
                 font=("Segoe UI", 10),
                 bg="#f4f6f7").grid(row=0, column=0, padx=5)

        self.port_var = tk.StringVar()

        self.port_menu = tk.OptionMenu(control_panel,
                                      self.port_var,
                                      *self.get_ports())

        self.port_menu.config(width=10)
        self.port_menu.grid(row=0, column=1)

        tk.Button(control_panel,
                  text="Refresh",
                  command=self.refresh_ports,
                  width=8).grid(row=0, column=2, padx=6)


        tk.Button(control_panel,
                  text="Browse Save Folder",
                  command=self.choose_folder,
                  width=18).grid(row=0, column=3, padx=8)


        tk.Button(control_panel,
                  text="Start Logging",
                  command=self.start_logging,
                  width=14,
                  bg="#27ae60",
                  fg="white").grid(row=1, column=1, pady=6)


        tk.Button(control_panel,
                  text="Stop Logging",
                  command=self.stop_logging,
                  width=14,
                  bg="#c0392b",
                  fg="white").grid(row=1, column=2, pady=6)


        # ==============================
        # TEXT OUTPUT WINDOW
        # ==============================

        output_frame = tk.Frame(self.root)
        output_frame.pack(fill="both", expand=True, padx=12, pady=10)

        self.textbox = tk.Text(
            output_frame,
            font=("Consolas", 10),
            relief="solid",
            bd=1
        )

        scrollbar = tk.Scrollbar(output_frame,
                                 command=self.textbox.yview)

        self.textbox.configure(yscrollcommand=scrollbar.set)

        self.textbox.pack(side="left",
                          fill="both",
                          expand=True)

        scrollbar.pack(side="right",
                       fill="y")


    # ==============================
    # PORT FUNCTIONS
    # ==============================

    def get_ports(self):

        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]


    def refresh_ports(self):

        menu = self.port_menu["menu"]
        menu.delete(0, "end")

        ports = self.get_ports()

        for port in ports:
            menu.add_command(label=port,
                             command=lambda p=port:
                             self.port_var.set(p))

        if ports:
            self.port_var.set(ports[0])


    # ==============================
    # FOLDER SELECTION
    # ==============================

    def choose_folder(self):

        folder = filedialog.askdirectory()

        if folder:
            self.save_folder = folder

            messagebox.showinfo(
                "Save Location Selected",
                f"Data will be saved in:\n{folder}"
            )


    # ==============================
    # LOGGING CONTROL
    # ==============================

    def start_logging(self):

        port = self.port_var.get()

        if not port:
            messagebox.showwarning("Warning",
                                   "Select COM port first")
            return

        self.reader = SerialReader(
            port,
            self.textbox,
            self.save_folder
        )

        self.reader.start()


    def stop_logging(self):

        if self.reader:
            self.reader.stop()

            messagebox.showinfo(
                "Stopped",
                "Logging stopped successfully"
            )


# ==============================
# RUN APP
# ==============================

if __name__ == "__main__":

    root = tk.Tk()

    app = QRNG_GUI(root)

    root.mainloop()
