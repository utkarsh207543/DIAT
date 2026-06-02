#!/usr/bin/env python3
"""
Modern Serial Port Reader with Beautiful UI using CustomTkinter
Features: Port detection, baud rate selection, real-time data display, auto-scroll, copy/save data
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import serial
import serial.tools.list_ports
import threading
import queue
from datetime import datetime
from urllib.request import urlopen
from io import BytesIO

# Configure dark theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SerialReaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Serial Port Reader")
        self.geometry("900x700")
        self.minsize(700, 500)

        self.serial_port = None
        self.is_reading = False
        self.data_queue = queue.Queue()
        self.reader_thread = None

        self._setup_ui()
        self._refresh_ports()
        self.after(100, self._process_queue)

    def _setup_ui(self):
        """Build the UI with modern styling"""

        # Main container with padding
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header section with logos
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        # Load and display logos
        try:
            # DIAT Logo (left)
            diat_img_data = urlopen(
                "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/DIAT-ho5tA8pz9vgkAHW9G7Mams3ArUhhRp.png").read()
            diat_img = Image.open(BytesIO(diat_img_data)).resize((80, 80), Image.Resampling.LANCZOS)
            self.diat_photo = ImageTk.PhotoImage(diat_img)
            diat_label = ctk.CTkLabel(header_frame, image=self.diat_photo, text="")
            diat_label.pack(side="left", padx=(0, 15))

            # DRDO Logo (right of DIAT)
            drdo_img_data = urlopen(
                "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/DRDO-XXhUpxPsXWtGGWxz3fjxTcBaCva8Gm.png").read()
            drdo_img = Image.open(BytesIO(drdo_img_data)).resize((80, 80), Image.Resampling.LANCZOS)
            self.drdo_photo = ImageTk.PhotoImage(drdo_img)
            drdo_label = ctk.CTkLabel(header_frame, image=self.drdo_photo, text="")
            drdo_label.pack(side="left", padx=(0, 20))
        except Exception as e:
            print(f"Warning: Could not load logos: {e}")

        # Title and description
        text_section = ctk.CTkFrame(header_frame, fg_color="transparent")
        text_section.pack(side="left", fill="both", expand=True)

        title_label = ctk.CTkLabel(
            text_section,
            text="Serial Port Monitor",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            text_section,
            text="DRDO-DIAT Advanced Serial Communication Interface",
            font=("Helvetica", 11),
            text_color="#888888"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Configuration section
        config_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        config_frame.pack(fill="x", pady=(0, 15))

        # Port selection
        port_section = ctk.CTkFrame(config_frame)
        port_section.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(port_section, text="COM Port:", font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.port_var = ctk.StringVar(value="Select Port")
        self.port_dropdown = ctk.CTkComboBox(
            port_section,
            variable=self.port_var,
            state="readonly",
            font=("Helvetica", 10)
        )
        self.port_dropdown.pack(fill="x", pady=(5, 0))

        # Baud rate selection
        baud_section = ctk.CTkFrame(config_frame)
        baud_section.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(baud_section, text="Baud Rate:", font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.baud_var = ctk.StringVar(value="9600")
        baud_dropdown = ctk.CTkComboBox(
            baud_section,
            variable=self.baud_var,
            values=["300", "600", "1200", "2400", "4800", "9600", "14400", "19200", "28800", "38400", "57600",
                    "115200"],
            state="readonly",
            font=("Helvetica", 10)
        )
        baud_dropdown.pack(fill="x", pady=(5, 0))

        # Data bits
        databits_section = ctk.CTkFrame(config_frame)
        databits_section.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(databits_section, text="Data Bits:", font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.databits_var = ctk.StringVar(value="8")
        databits_dropdown = ctk.CTkComboBox(
            databits_section,
            variable=self.databits_var,
            values=["5", "6", "7", "8"],
            state="readonly",
            font=("Helvetica", 10)
        )
        databits_dropdown.pack(fill="x", pady=(5, 0))

        # Control buttons
        button_frame = ctk.CTkFrame(config_frame)
        button_frame.pack(side="left", fill="x", padx=(0, 0))

        self.connect_btn = ctk.CTkButton(
            button_frame,
            text="Connect",
            command=self._toggle_connection,
            font=("Helvetica", 11, "bold"),
            height=35,
            width=100
        )
        self.connect_btn.pack(side="left", padx=(5, 0))

        refresh_btn = ctk.CTkButton(
            button_frame,
            text="Refresh",
            command=self._refresh_ports,
            font=("Helvetica", 11),
            height=35,
            width=80
        )
        refresh_btn.pack(side="left", padx=(5, 0))

        # Status indicator
        status_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 15))

        status_inner = ctk.CTkFrame(status_frame)
        status_inner.pack(fill="x")

        self.status_indicator = ctk.CTkLabel(
            status_inner,
            text="●",
            text_color="#FF6B6B",
            font=("Helvetica", 16)
        )
        self.status_indicator.pack(side="left", padx=(0, 8))

        self.status_label = ctk.CTkLabel(
            status_inner,
            text="Disconnected",
            font=("Helvetica", 11)
        )
        self.status_label.pack(side="left", fill="x")

        # Data display section
        display_header = ctk.CTkFrame(main_container, fg_color="transparent")
        display_header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            display_header,
            text="Data Stream",
            font=("Helvetica", 12, "bold")
        ).pack(anchor="w")

        # Text display with scrollbar
        text_frame = ctk.CTkFrame(main_container)
        text_frame.pack(fill="both", expand=True, pady=(0, 15))
        text_frame.configure(height=200)

        self.text_display = ctk.CTkTextbox(
            text_frame,
            font=("Monaco", 10),
            text_color="#E0E0E0",
            fg_color="#1A1A1A",
            border_color="#404040",
            border_width=1,
            height=150
        )
        self.text_display.pack(fill="both", expand=True)
        self.text_display.configure(state="disabled")

        # Bottom controls
        control_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        control_frame.pack(fill="x")

        # Left side - info
        info_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        self.info_label = ctk.CTkLabel(
            info_frame,
            text="Ready",
            font=("Helvetica", 9),
            text_color="#888888"
        )
        self.info_label.pack(anchor="w")

        # Right side - action buttons
        action_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        action_frame.pack(side="right", fill="x")

        clear_btn = ctk.CTkButton(
            action_frame,
            text="Clear",
            command=self._clear_display,
            font=("Helvetica", 10),
            width=80
        )
        clear_btn.pack(side="left", padx=(0, 5))

        save_btn = ctk.CTkButton(
            action_frame,
            text="Save to File",
            command=self._save_data,
            font=("Helvetica", 10),
            width=100
        )
        save_btn.pack(side="left")

    def _refresh_ports(self):
        """Refresh available COM ports"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        if ports:
            self.port_dropdown.configure(values=ports)
            if self.port_var.get() == "Select Port":
                self.port_var.set(ports[0])
        else:
            self.port_dropdown.configure(values=["No ports found"])
            self.port_var.set("No ports found")

    def _toggle_connection(self):
        """Connect or disconnect from serial port"""
        if self.is_reading:
            self._disconnect()
        else:
            self._connect()

    def _connect(self):
        """Connect to selected serial port"""
        port = self.port_var.get()
        baud = int(self.baud_var.get())
        databits = int(self.databits_var.get())

        if port == "No ports found":
            messagebox.showerror("Error", "No serial ports available")
            return

        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baud,
                bytesize=databits,
                timeout=1
            )
            self.is_reading = True
            self.connect_btn.configure(text="Disconnect", fg_color="#FF6B6B")
            self.status_indicator.configure(text_color="#51CF66")
            self.status_label.configure(text=f"Connected to {port} @ {baud} baud")

            # Start reading thread
            self.reader_thread = threading.Thread(target=self._read_serial, daemon=True)
            self.reader_thread.start()

            self._update_info(f"Connected to {port}")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")

    def _disconnect(self):
        """Disconnect from serial port"""
        self.is_reading = False
        if self.serial_port:
            self.serial_port.close()

        self.connect_btn.configure(text="Connect", fg_color=None)
        self.status_indicator.configure(text_color="#FF6B6B")
        self.status_label.configure(text="Disconnected")
        self._update_info("Disconnected")

    def _read_serial(self):
        """Read from serial port in separate thread"""
        while self.is_reading:
            try:
                if self.serial_port and self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode('utf-8', errors='replace').strip()
                    if data:
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        self.data_queue.put(f"[{timestamp}] {data}\n")
            except Exception as e:
                self.data_queue.put(f"[ERROR] {str(e)}\n")
                break

    def _process_queue(self):
        """Process data from queue and update display"""
        try:
            while True:
                data = self.data_queue.get_nowait()
                self.text_display.configure(state="normal")
                self.text_display.insert("end", data)
                self.text_display.see("end")
                self.text_display.configure(state="disabled")
        except queue.Empty:
            pass
        finally:
            self.after(50, self._process_queue)

    def _clear_display(self):
        """Clear the text display"""
        self.text_display.configure(state="normal")
        self.text_display.delete("1.0", "end")
        self.text_display.configure(state="disabled")
        self._update_info("Display cleared")

    def _save_data(self):
        """Save displayed data to file"""
        if not self.text_display.get("1.0", "end-1c"):
            messagebox.showwarning("Empty", "No data to save")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.text_display.get("1.0", "end"))
                self._update_info(f"Data saved to {file_path}")
                messagebox.showinfo("Success", "Data saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")

    def _update_info(self, message):
        """Update info label"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.info_label.configure(text=f"[{timestamp}] {message}")

    def on_closing(self):
        """Handle window closing"""
        if self.is_reading:
            self._disconnect()
        self.destroy()


if __name__ == "__main__":
    app = SerialReaderApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
