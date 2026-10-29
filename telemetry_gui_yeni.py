import threading
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

import serial
from serial.tools import list_ports


class TelemetryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Telemetri Seri Arayüzü")
        self.root.geometry("940x700")
        self.root.minsize(760, 560)
        self.ports = {}
        self.controls = {}

        self._build_ui()
        self.refresh_ports()
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="Telemetri Seri Arayüzü",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            main,
            text=(
                "Ayarlar USB-UART seri bağlantı ayarlarıdır. Modemin RF ayarları "
                "cihaz modeline/protokolüne göre ayrıca yapılandırılır."
            ),
            wraplength=900,
        ).pack(anchor="w", pady=(4, 10))

        endpoints = ttk.Frame(main)
        endpoints.pack(fill="x")
        self._build_endpoint(endpoints, "A")
        self._build_endpoint(endpoints, "B")

        ttk.Button(main, text="COM portlarını yenile", command=self.refresh_ports).pack(
            anchor="e", pady=(8, 12)
        )

        send_frame = ttk.LabelFrame(main, text="Mesaj gönder", padding=8)
        send_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(send_frame, text="Gönderen telemetri:").grid(
            row=0, column=0, sticky="w"
        )
        self.send_target = tk.StringVar(value="A")
        ttk.Combobox(
            send_frame,
            textvariable=self.send_target,
            values=("A", "B"),
            state="readonly",
            width=8,
        ).grid(row=0, column=1, padx=(6, 12), sticky="w")

        self.newline = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            send_frame, text="Sonuna CR+LF ekle", variable=self.newline
        ).grid(row=0, column=2, sticky="w")

        self.message_text = tk.StringVar()
        entry = ttk.Entry(send_frame, textvariable=self.message_text)
        entry.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        entry.bind("<Return>", lambda _event: self.send_message())
        ttk.Button(send_frame, text="Gönder", command=self.send_message).grid(
            row=1, column=3, padx=(8, 0), pady=(8, 0)
        )
        send_frame.columnconfigure(2, weight=1)

        log_frame = ttk.LabelFrame(main, text="Alınan / gönderilen veri", padding=8)
        log_frame.pack(fill="both", expand=True)
        self.log = tk.Text(log_frame, height=16, wrap="word", state="disabled")
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=scrollbar.set)
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        ttk.Button(main, text="Kaydı temizle", command=self.clear_log).pack(
            anchor="e", pady=(6, 0)
        )

    def _build_endpoint(self, parent, endpoint):
        frame = ttk.LabelFrame(parent, text=f"Telemetri {endpoint}", padding=8)
        frame.pack(side="left", fill="both", expand=True, padx=(0, 6) if endpoint == "A" else (6, 0))

        port = tk.StringVar()
        baud = tk.StringVar(value="57600")
        data_bits = tk.StringVar(value="8")
        parity = tk.StringVar(value="None")
        stop_bits = tk.StringVar(value="1")
        flow = tk.StringVar(value="None")
        status = tk.StringVar(value="Bağlı değil")
        setting_widgets = []

        ttk.Label(frame, text="COM port").grid(row=0, column=0, sticky="w", pady=3)
        port_combo = ttk.Combobox(frame, textvariable=port, width=13)
        port_combo.grid(row=0, column=1, sticky="ew", pady=3)
        setting_widgets.append(port_combo)
        ttk.Label(frame, text="Baud hızı (yazılabilir)").grid(row=1, column=0, sticky="w", pady=3)
        baud_combo = ttk.Combobox(
            frame,
            textvariable=baud,
            values=("9600", "19200", "38400", "57600", "115200", "230400"),
            width=13,
        )
        baud_combo.grid(row=1, column=1, sticky="ew", pady=3)
        setting_widgets.append(baud_combo)
        ttk.Label(frame, text="Veri biti").grid(row=2, column=0, sticky="w", pady=3)
        data_bits_combo = ttk.Combobox(
            frame, textvariable=data_bits, values=("5", "6", "7", "8"), state="readonly", width=13
        )
        data_bits_combo.grid(row=2, column=1, sticky="ew", pady=3)
        setting_widgets.append(data_bits_combo)
        ttk.Label(frame, text="Parite").grid(row=3, column=0, sticky="w", pady=3)
        parity_combo = ttk.Combobox(
            frame,
            textvariable=parity,
            values=("None", "Even", "Odd", "Mark", "Space"),
            state="readonly",
            width=13,
        )
        parity_combo.grid(row=3, column=1, sticky="ew", pady=3)
        setting_widgets.append(parity_combo)
        ttk.Label(frame, text="Dur biti").grid(row=4, column=0, sticky="w", pady=3)
        stop_bits_combo = ttk.Combobox(
            frame,
            textvariable=stop_bits,
            values=("1", "1.5", "2"),
            state="readonly",
            width=13,
        )
        stop_bits_combo.grid(row=4, column=1, sticky="ew", pady=3)
        setting_widgets.append(stop_bits_combo)
        ttk.Label(frame, text="Akış kontrolü").grid(row=5, column=0, sticky="w", pady=3)
        flow_combo = ttk.Combobox(
            frame,
            textvariable=flow,
            values=("None", "RTS/CTS", "XON/XOFF"),
            state="readonly",
            width=13,
        )
        flow_combo.grid(row=5, column=1, sticky="ew", pady=3)
        setting_widgets.append(flow_combo)

        button = ttk.Button(
            frame,
            text="Bağlan",
            command=lambda name=endpoint: self.toggle_connection(name),
        )
        button.grid(row=6, column=0, sticky="w", pady=(8, 2))
        ttk.Label(frame, textvariable=status).grid(
            row=6, column=1, sticky="w", padx=(8, 0), pady=(8, 2)
        )
        frame.columnconfigure(1, weight=1)

        self.controls[endpoint] = {
            "port": port,
            "port_combo": port_combo,
            "setting_widgets": setting_widgets,
            "baud": baud,
            "data_bits": data_bits,
            "parity": parity,
            "stop_bits": stop_bits,
            "flow": flow,
            "status": status,
            "button": button,
            "setting_states": [widget.cget("state") for widget in setting_widgets],
        }

    def refresh_ports(self):
        available = sorted(
            list_ports.comports(),
            key=lambda item: (item.vid is None, item.device),
        )
        port_names = [item.device for item in available]
        for endpoint, controls in self.controls.items():
            combo = controls["port_combo"]
            combo["values"] = port_names
            if endpoint in self.ports:
                continue
            if controls["port"].get() not in port_names:
                free_ports = [
                    name
                    for name in port_names
                    if all(
                        name != other["port"].get()
                        for key, other in self.controls.items()
                        if key != endpoint
                    )
                ]
                controls["port"].set(free_ports[0] if free_ports else "")

    def toggle_connection(self, endpoint):
        if endpoint in self.ports:
            self.disconnect(endpoint)
        else:
            self.connect(endpoint)

    def connect(self, endpoint):
        controls = self.controls[endpoint]
        port_name = controls["port"].get().strip()
        if not port_name:
            messagebox.showerror(
                "Bağlantı hatası", f"Telemetri {endpoint} için COM portu seçin."
            )
            return

        flow = controls["flow"].get()
        try:
            baudrate = int(controls["baud"].get().strip())
            if baudrate <= 0:
                raise ValueError("Baud hızı sıfırdan büyük olmalı.")
            connection = serial.Serial(
                port=port_name,
                baudrate=baudrate,
                bytesize=int(controls["data_bits"].get()),
                parity={
                    "None": serial.PARITY_NONE,
                    "Even": serial.PARITY_EVEN,
                    "Odd": serial.PARITY_ODD,
                    "Mark": serial.PARITY_MARK,
                    "Space": serial.PARITY_SPACE,
                }[controls["parity"].get()],
                stopbits=float(controls["stop_bits"].get()),
                timeout=0.2,
                write_timeout=1,
                rtscts=flow == "RTS/CTS",
                xonxoff=flow == "XON/XOFF",
            )
        except (serial.SerialException, ValueError, KeyError) as error:
            messagebox.showerror("Bağlantı hatası", str(error))
            return

        stop_event = threading.Event()
        reader = threading.Thread(
            target=self._read_serial, args=(endpoint, connection, stop_event), daemon=True
        )
        self.ports[endpoint] = {
            "serial": connection,
            "stop": stop_event,
            "reader": reader,
            "port_name": port_name,
        }
        for widget in controls["setting_widgets"]:
            widget.configure(state="disabled")
        controls["status"].set(f"Bağlı: {port_name} / {baudrate}")
        controls["button"].configure(text="Bağlantıyı kes")
        self._append_log(f"[{port_name}] Bağlantı kuruldu. Baud hızı: {baudrate}.")
        reader.start()

    def _read_serial(self, endpoint, connection, stop_event):
        pending = bytearray()
        while not stop_event.is_set():
            try:
                waiting = connection.in_waiting
                data = connection.read(waiting if waiting else 1)
            except serial.SerialException as error:
                self.root.after(0, self._reader_failed, endpoint, str(error))
                return
            if data:
                pending.extend(data)
                while b"\n" in pending:
                    end = pending.index(b"\n") + 1
                    message = bytes(pending[:end])
                    del pending[:end]
                    self.root.after(0, self._show_received, endpoint, message)
            elif pending:
                # Flush packets without a newline after the serial read timeout.
                message = bytes(pending)
                pending.clear()
                self.root.after(0, self._show_received, endpoint, message)

    def _show_received(self, endpoint, data):
        port_name = self.ports.get(endpoint, {}).get("port_name", endpoint)
        printable = data.decode("utf-8", errors="replace").replace("\r", "\\r").replace("\n", "\\n")
        self._append_log(
            f"[{datetime.now():%H:%M:%S}] {port_name} RX ({len(data)} byte) "
            f"HEX: {data.hex(' ')} | Metin: {printable}"
        )

    def _reader_failed(self, endpoint, error):
        if endpoint in self.ports:
            port_name = self.ports[endpoint]["port_name"]
            self._append_log(f"[{port_name}] Okuma hatası: {error}")
            self.disconnect(endpoint)

    def send_message(self):
        endpoint = self.send_target.get()
        connection_info = self.ports.get(endpoint)
        if connection_info is None:
            messagebox.showerror(
                "Gönderim hatası", f"Telemetri {endpoint} bağlı değil."
            )
            return
        message = self.message_text.get()
        if not message:
            return
        if self.newline.get():
            message += "\r\n"
        data = message.encode("utf-8")
        try:
            connection_info["serial"].write(data)
        except (serial.SerialException, serial.SerialTimeoutException) as error:
            messagebox.showerror("Gönderim hatası", str(error))
            return

        port_name = connection_info["port_name"]
        printable = message.rstrip().replace("\r", "\\r").replace("\n", "\\n")
        self._append_log(
            f"[{datetime.now():%H:%M:%S}] {port_name} TX ({len(data)} byte) "
            f"HEX: {data.hex(' ')} | Metin: {printable}"
        )
        self.message_text.set("")

    def disconnect(self, endpoint):
        connection_info = self.ports.pop(endpoint, None)
        if connection_info is None:
            return
        connection_info["stop"].set()
        connection_info["serial"].close()
        connection_info["reader"].join(timeout=0.5)

        controls = self.controls[endpoint]
        for widget, state in zip(
            controls["setting_widgets"], controls["setting_states"]
        ):
            widget.configure(state=state)
        controls["status"].set("Bağlı değil")
        controls["button"].configure(text="Bağlan")
        self._append_log(f"[{connection_info['port_name']}] Bağlantı kesildi.")

    def _append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        line_count = int(self.log.index("end-1c").split(".")[0])
        if line_count > 3000:
            self.log.delete("1.0", f"{line_count - 3000}.0")
        self.log.see("end")
        self.log.configure(state="disabled")

    def clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def close_app(self):
        for endpoint in tuple(self.ports):
            self.disconnect(endpoint)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TelemetryApp(root)
    root.mainloop()
