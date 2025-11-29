# maintenance_full.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
import sqlite3
import threading
import time
import csv
import os
from PIL import Image, ImageTk
import math

# Setup dasar untuk customtkinter 
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Daftar tema warna yang bisa dipilih user
THEMES = {
    "Premium Dark": {  # Tema gelap premium biru
        "bg": "#0f1720", "card": "#1e293b", "accent": "#0ea5e9",
        "good": "#10b981", "warn": "#f59e0b", "bad": "#ef4444",
        "text": "#f8fafc", "text_secondary": "#94a3b8"
    },
    "Gamer RGB": {  # Tema gaming dengan warna neon
        "bg": "#050505", "card": "#0f0f23", "accent": "#7c3aed",
        "good": "#00ff99", "warn": "#ffcc00", "bad": "#ff0033",
        "text": "#ffffff", "text_secondary": "#a0a0ff"
    },
    "Minimal Clean": {  # Tema terang minimalis
        "bg": "#f3f4f6", "card": "#ffffff", "accent": "#2563eb",
        "good": "#16a34a", "warn": "#f59e0b", "bad": "#dc2626",
        "text": "#1f2937", "text_secondary": "#6b7280"
    },
    "Sunset Orange": {  # Tema orange sunset
        "bg": "#1a1a2e", "card": "#16213e", "accent": "#ff7a45",
        "good": "#4ade80", "warn": "#fbbf24", "bad": "#f87171",
        "text": "#e2e8f0", "text_secondary": "#94a3b8"
    }
}

# Data preset motor dan jadwal servisnya
MOTOR_PRESET = {
    "Honda Beat": {
        "Oli Mesin": {"km": 2000, "bulan": 2},
        "Busi": {"km": 8000, "bulan": 6},
        "Kampas Rem": {"km": 6000, "bulan": 6},
        "CVT / Roller": {"km": 8000, "bulan": 8}
    },
    "Yamaha NMAX": {
        "Oli Mesin": {"km": 3000, "bulan": 2},
        "Radiator": {"km": 20000, "bulan": 12},
        "Gear Oil": {"km": 9000, "bulan": 8},
        "Busi": {"km": 10000, "bulan": 12}
    },
    "Honda Vario 150": {
        "Oli Mesin": {"km": 4000, "bulan": 3},
        "CVT / Roller": {"km": 12000, "bulan": 12},
        "Filter Udara": {"km": 16000, "bulan": 12},
        "Busi": {"km": 8000, "bulan": 6}
    }
}

# Nama file database SQLite
DB_FILE = "motor_maintenance.db"

# --------------------------
# FUNGSI DATABASE (sqlite3)
# --------------------------
def init_db():
    """Buat database dan tabel jika belum ada"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Tabel untuk menyimpan data motor
    c.execute('''
        CREATE TABLE IF NOT EXISTS motors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            created_at TEXT
        )
    ''')
    # Tabel untuk jadwal servis
    c.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            motor_name TEXT,
            service_name TEXT,
            interval_km INTEGER,
            interval_bulan INTEGER,
            next_due_km INTEGER,
            next_due_date TEXT,
            last_serviced_at TEXT
        )
    ''')
    # Tabel riwayat servis
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            motor_name TEXT,
            service_name TEXT,
            when_served TEXT,
            km_at_service INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def add_motor_to_db(motor_name, services_dict, km_now=0):
    """Simpan motor baru ke database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO motors (name, created_at) VALUES (?, ?)", (motor_name, datetime.now().isoformat()))
    except:
        pass  # Kalau motor sudah ada, skip
    # Simpan setiap servis ke database
    for sname, val in services_dict.items():
        interval_km = int(val.get("km", 0))
        interval_bulan = int(val.get("bulan", 0))
        next_due_km = km_now + interval_km
        next_due_date = (datetime.now() + timedelta(days=interval_bulan*30)).isoformat()
        # Hapus dulu yang lama, lalu insert yang baru
        c.execute("DELETE FROM services WHERE motor_name=? AND service_name=?", (motor_name, sname))
        c.execute('''INSERT INTO services (motor_name, service_name, interval_km, interval_bulan,
                     next_due_km, next_due_date, last_serviced_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (motor_name, sname, interval_km, interval_bulan, next_due_km, next_due_date, None))
    conn.commit()
    conn.close()

def load_services_from_db(motor_name):
    """Ambil data servis untuk motor tertentu dari database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT service_name, interval_km, interval_bulan, next_due_km, next_due_date, last_serviced_at FROM services WHERE motor_name=?", (motor_name,))
    rows = c.fetchall()
    conn.close()
    out = {}
    for r in rows:
        out[r[0]] = {
            "km": r[1], "bulan": r[2], "next_due_km": r[3],
            "next_due_date": datetime.fromisoformat(r[4]) if r[4] else datetime.now(),
            "last_serviced_at": datetime.fromisoformat(r[5]) if r[5] else None
        }
    return out

def update_service_in_db(motor_name, service_name, next_due_km=None, next_due_date=None, last_serviced_at=None):
    """Update data servis di database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if next_due_km is not None:
        c.execute("UPDATE services SET next_due_km=? WHERE motor_name=? AND service_name=?", (next_due_km, motor_name, service_name))
    if next_due_date is not None:
        c.execute("UPDATE services SET next_due_date=? WHERE motor_name=? AND service_name=?", (next_due_date.isoformat(), motor_name, service_name))
    if last_serviced_at is not None:
        c.execute("UPDATE services SET last_serviced_at=? WHERE motor_name=? AND service_name=?", (last_serviced_at.isoformat(), motor_name, service_name))
    conn.commit()
    conn.close()

def log_history(motor_name, service_name, km_at_service):
    """Catat servis ke riwayat"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO history (motor_name, service_name, when_served, km_at_service) VALUES (?, ?, ?, ?)",
              (motor_name, service_name, datetime.now().isoformat(), km_at_service))
    conn.commit()
    conn.close()

def export_history_csv(path):
    """Export riwayat servis ke file CSV"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT motor_name, service_name, when_served, km_at_service FROM history ORDER BY when_served DESC")
    rows = c.fetchall()
    conn.close()
    with open(path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["motor_name","service_name","when_served","km_at_service"])
        writer.writerows(rows)

# Inisialisasi database saat aplikasi mulai
init_db()

# --------------------------
# WIDGET KUSTOM (Komponen UI tambahan)
# --------------------------
class AnimatedCard(ctk.CTkFrame):
    """Kartu animasi yang bisa berkedip ketika di-highlight"""
    def __init__(self, master, theme, **kwargs):
        super().__init__(master, **kwargs)
        self.theme = theme
        self.configure(fg_color=theme["card"], corner_radius=12)
        
    def animate_highlight(self):
        """Animasi kedip ketika kartu di-highlight"""
        original_color = self.cget("fg_color")
        highlight_color = self.theme["accent"]
        
        def fade_back(count=0):
            if count <= 10:
                ratio = count / 10
                # Hitung warna gradasi antara highlight dan original
                r = int((1-ratio) * int(highlight_color[1:3], 16) + ratio * int(original_color[1:3], 16))
                g = int((1-ratio) * int(highlight_color[3:5], 16) + ratio * int(original_color[3:5], 16))
                b = int((1-ratio) * int(highlight_color[5:7], 16) + ratio * int(original_color[5:7], 16))
                color = f"#{r:02x}{g:02x}{b:02x}"
                self.configure(fg_color=color)
                self.after(30, lambda: fade_back(count+1))
        
        self.configure(fg_color=highlight_color)
        self.after(300, fade_back)

class CircularProgressBar(ctk.CTkFrame):
    """Progress bar berbentuk lingkaran yang keren"""
    def __init__(self, master, size=80, theme=None, **kwargs):
        super().__init__(master, **kwargs)
        self.theme = theme
        self.size = size
        self.canvas = tk.Canvas(self, width=size, height=size, bg=theme["card"], highlightthickness=0)
        self.canvas.pack()
        self.value = 0
        
    def set_value(self, value):
        """Set nilai progress (0-1)"""
        self.value = max(0, min(1, value))
        self.draw()
        
    def draw(self):
        """Gambar progress bar di canvas"""
        self.canvas.delete("all")
        center = self.size / 2
        radius = self.size / 2 - 5
        
        # Lingkaran background
        self.canvas.create_oval(center - radius, center - radius, 
                               center + radius, center + radius, 
                               outline=self.theme["bg"], width=3)
        
        # Busur progress
        if self.value > 0:
            start_angle = 90
            extent_angle = -360 * self.value
            
            # Tentukan warna berdasarkan nilai progress
            if self.value >= 0.8:
                color = self.theme["bad"]  # Merah kalau hampir habis
            elif self.value >= 0.6:
                color = self.theme["warn"]  # Kuning kalau menengah
            else:
                color = self.theme["good"]  # Hijau kalau masih banyak
                
            self.canvas.create_arc(center - radius, center - radius, 
                                  center + radius, center + radius,
                                  start=start_angle, extent=extent_angle,
                                  outline=color, width=4, style=tk.ARC)
        
        # Teks persentase di tengah
        self.canvas.create_text(center, center, text=f"{int(self.value * 100)}%", 
                               fill=self.theme["text"], font=("Arial", 12, "bold"))

# --------------------------
# APLIKASI UTAMA
# --------------------------
class MotorMaintenanceApp(ctk.CTk):
    """Kelas utama aplikasi Maintenance Motor"""
    
    def __init__(self):
        super().__init__()
        # Setup window utama
        self.title("🏍️ Motor Maintenance kel 2")
        self.geometry("1200x750")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # State aplikasi
        self.theme_name = "Premium Dark"  # Tema default
        self.apply_theme(self.theme_name)
        self.km_simulate = False  # Flag untuk simulasi KM
        self.sim_thread = None    # Thread untuk simulasi

        # Data yang sedang dipilih
        self.current_motor = None  # Motor yang sedang aktif
        self.services = {}         # Daftar servis untuk motor aktif

        # Bangun UI dan jalankan animasi
        self.build_ui()
        self.anim_slide_in()

        # Mulai pengecekan periodic
        self.after(1200, self.periodic_check)

    # --------- MEMBANGUN UI ---------
    def build_ui(self):
        """Bangun semua komponen antarmuka pengguna"""
        # Setup layout grid
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Main content
        self.grid_rowconfigure(0, weight=1)

        # ---- SIDEBAR ----
        self.sidebar = ctk.CTkFrame(self, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Area logo/title
        logo_frame = ctk.CTkFrame(self.sidebar, corner_radius=0, fg_color=self._theme_colors["accent"])
        logo_frame.pack(fill="x", padx=0, pady=0)
        
        ctk.CTkLabel(logo_frame, text="🏍️ MOTOR CARE", 
                    font=("Arial", 20, "bold"), text_color="white").pack(pady=15)
        
        # Area navigasi
        nav_frame = ctk.CTkFrame(self.sidebar, corner_radius=0)
        nav_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Pilihan motor
        ctk.CTkLabel(nav_frame, text="PILIH MOTOR", font=("Arial", 14, "bold"), 
                    text_color=self._theme_colors["text_secondary"]).pack(pady=(20, 5))
        
        self.motor_combo = ctk.CTkComboBox(nav_frame, 
                                         values=list(MOTOR_PRESET.keys()) + self._load_custom_motor_names(),
                                         command=self.on_motor_select,
                                         width=200, height=35,
                                         dropdown_font=("Arial", 12))
        self.motor_combo.pack(pady=10)
        
        # Tombol tambah motor custom
        ctk.CTkButton(nav_frame, text="➕ Tambah Motor", 
                     command=self.open_custom_motor_window,
                     fg_color="transparent", border_width=2,
                     text_color=self._theme_colors["text"],
                     border_color=self._theme_colors["accent"]).pack(pady=5)

        # Input KM
        ctk.CTkLabel(nav_frame, text="KILOMETER SAAT INI", 
                    font=("Arial", 14, "bold"), 
                    text_color=self._theme_colors["text_secondary"]).pack(pady=(20, 5))
        
        self.km_now_var = tk.IntVar(value=0)
        self.km_now_entry = ctk.CTkEntry(nav_frame, width=180, height=40,
                                       textvariable=self.km_now_var,
                                       font=("Arial", 16, "bold"),
                                       justify="center")
        self.km_now_entry.pack(pady=10)
        
        # Aksi cepat
        ctk.CTkLabel(nav_frame, text="AKSI CEPAT", 
                    font=("Arial", 14, "bold"), 
                    text_color=self._theme_colors["text_secondary"]).pack(pady=(20, 5))
        
        action_buttons = [
            ("💾 Simpan Data", self.save_motor_db),
            ("📊 Export CSV", self.export_history_dialog),
            ("🔄 Reset Due", self.reset_next_due_manual),
            ("📋 Riwayat", self.show_recent_history)
        ]
        
        for text, command in action_buttons:
            btn = ctk.CTkButton(nav_frame, text=text, command=command,
                              fg_color="transparent", border_width=1,
                              border_color=self._theme_colors["text_secondary"],
                              text_color=self._theme_colors["text"])
            btn.pack(fill="x", padx=10, pady=5)

        # Pilihan tema
        ctk.CTkLabel(nav_frame, text="TEMA", 
                    font=("Arial", 14, "bold"), 
                    text_color=self._theme_colors["text_secondary"]).pack(pady=(20, 5))
        
        self.theme_combo = ctk.CTkComboBox(nav_frame, 
                                         values=list(THEMES.keys()), 
                                         command=self.on_theme_change,
                                         width=180)
        self.theme_combo.set(self.theme_name)
        self.theme_combo.pack(pady=10)

        # ---- AREA KONTEN UTAMA ----
        self.main_content = ctk.CTkFrame(self, corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)

        # Header dengan statistik
        self.header_frame = ctk.CTkFrame(self.main_content, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        self.stats_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20, pady=15)
        
        # Statistik akan diupdate ketika motor dipilih
        self.stats_labels = {}
        
        # Area servis
        services_container = ctk.CTkFrame(self.main_content)
        services_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        services_container.grid_columnconfigure(0, weight=1)
        services_container.grid_rowconfigure(0, weight=1)
        
        # Frame servis yang bisa di-scroll
        self.services_scroll = ctk.CTkScrollableFrame(services_container, 
                                                    fg_color="transparent")
        self.services_scroll.grid(row=0, column=0, sticky="nsew")
        self.services_scroll.grid_columnconfigure(0, weight=1)

        # Kontrol simulasi di bagian bawah
        sim_frame = ctk.CTkFrame(self.main_content, height=80)
        sim_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        sim_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(sim_frame, text="🚀 Simulasi KM:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.sim_speed = ctk.CTkSlider(sim_frame, from_=1, to=200, number_of_steps=199, width=200)
        self.sim_speed.set(10)
        self.sim_speed.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkButton(sim_frame, text="▶️ Start", command=self.start_simulation, 
                     fg_color=self._theme_colors["good"]).grid(row=0, column=2, padx=5, pady=10)
        ctk.CTkButton(sim_frame, text="⏹️ Stop", command=self.stop_simulation,
                     fg_color=self._theme_colors["bad"]).grid(row=0, column=3, padx=5, pady=10)

    def update_stats_header(self):
        """Update header dengan statistik terkini"""
        # Hapus widget lama
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
            
        if not self.current_motor:
            ctk.CTkLabel(self.stats_frame, text="Pilih motor untuk memulai", 
                        font=("Arial", 16), text_color=self._theme_colors["text_secondary"]).pack(pady=20)
            return
            
        # Hitung statistik
        km_now = int(self.km_now_var.get() or 0)
        total_services = len(self.services)
        overdue_count = 0    # Servis yang telat
        warning_count = 0    # Servis yang hampir telat
        
        for service in self.services.values():
            if service.get("next_due_km", 0) <= km_now:
                overdue_count += 1
            elif service.get("next_due_km", 0) - km_now <= max(50, int(service["km"] * 0.15)):
                warning_count += 1
        
        # Data untuk ditampilkan
        stats_data = [
            (f"📊 {total_services}", "Total Servis", self._theme_colors["text"]),
            (f"✅ {total_services - overdue_count - warning_count}", "Aman", self._theme_colors["good"]),
            (f"⚠️ {warning_count}", "Peringatan", self._theme_colors["warn"]),
            (f"🚨 {overdue_count}", "Terlambat", self._theme_colors["bad"])
        ]
        
        # Tampilkan setiap statistik
        for i, (value, label, color) in enumerate(stats_data):
            stat_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
            stat_frame.pack(side="left", expand=True, padx=10)
            
            ctk.CTkLabel(stat_frame, text=value, font=("Arial", 24, "bold"), 
                        text_color=color).pack()
            ctk.CTkLabel(stat_frame, text=label, font=("Arial", 12),
                        text_color=self._theme_colors["text_secondary"]).pack()

    # ----------------------
    # MANAJEMEN TEMA
    # ----------------------
    def apply_theme(self, name):
        """Terapkan tema yang dipilih"""
        self.theme_name = name
        theme = THEMES[name]
        # Set mode terang/gelap
        if name == "Minimal Clean":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")
        self._theme_colors = theme

    def on_theme_change(self, name):
        """Callback ketika user ganti tema"""
        self.apply_theme(name)
        self.refresh_ui_colors()

    def refresh_ui_colors(self):
        """Refresh warna UI sesuai tema"""
        # Update sidebar
        self.sidebar.configure(fg_color=self._theme_colors["card"])
        
        # Update header
        self.header_frame.configure(fg_color=self._theme_colors["card"])
        
        # Render ulang servis dan statistik
        if self.current_motor:
            self.update_stats_header()
            self.render_services()

    # ----------------------
    # ANIMASI
    # ----------------------
    def anim_slide_in(self):
        """Animasi fade-in ketika aplikasi dibuka"""
        self.attributes('-alpha', 0)
        for i in range(0, 101, 5):
            self.attributes('-alpha', i/100)
            self.update()
            time.sleep(0.02)

    # ----------------------
    # MANAJEMEN MOTOR
    # ----------------------
    def _load_custom_motor_names(self):
        """Ambil daftar nama motor custom dari database"""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT name FROM motors")
        rows = [r[0] for r in c.fetchall()]
        conn.close()
        return rows

    def on_motor_select(self, name):
        """Callback ketika user pilih motor dari dropdown"""
        if not name:
            return
        self.current_motor = name
        # Coba load dari database dulu
        services_db = load_services_from_db(name)
        if services_db:
            # Jika ada di database, pakai data dari database
            mem = {}
            for sname, vals in services_db.items():
                mem[sname] = {
                    "km": vals["km"],
                    "bulan": vals["bulan"],
                    "next_due_km": vals["next_due_km"],
                    "next_due_date": vals["next_due_date"],
                    "last_serviced_at": vals["last_serviced_at"]
                }
            self.services = mem
        else:
            # Jika tidak ada, pakai preset
            preset = MOTOR_PRESET.get(name, {})
            mem = {}
            for sname, v in preset.items():
                mem[sname] = {"km": v["km"], "bulan": v["bulan"], "next_due_km": 0, "next_due_date": datetime.now() + timedelta(days=v["bulan"]*30), "last_serviced_at": None}
            self.services = mem
        
        # Update UI
        self.update_stats_header()
        self.render_services()

    def open_custom_motor_window(self):
        """Buka window untuk tambah motor custom"""
        win = ctk.CTkToplevel(self)
        win.title("➕ Tambah Motor Custom")
        win.geometry("500x600")
        win.transient(self)  # Biar window selalu di atas main window
        win.grab_set()       # Biar user harus nutup window ini dulu

        main_frame = ctk.CTkFrame(win)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Tambah Motor Baru", font=("Arial", 18, "bold")).pack(pady=10)

        # Input nama motor
        ctk.CTkLabel(main_frame, text="Nama Motor:").pack(pady=5)
        name_entry = ctk.CTkEntry(main_frame, width=300, placeholder_text="Contoh: Honda Scoopy")
        name_entry.pack(pady=5)

        # Daftar servis
        ctk.CTkLabel(main_frame, text="Daftar Servis:").pack(pady=10)
        
        list_frame = ctk.CTkScrollableFrame(main_frame, height=200)
        list_frame.pack(fill="both", expand=True, pady=5)

        # Temporary storage untuk servis yang ditambahkan
        services_temp = {}

        def add_service_to_temp():
            """Tambah servis ke list temporary"""
            sname = s_entry.get().strip()
            try:
                s_km = int(km_entry.get())
                s_bl = int(bl_entry.get())
            except:
                messagebox.showerror("Error", "KM dan Bulan harus angka")
                return
            if sname == "":
                messagebox.showwarning("Peringatan", "Nama servis kosong")
                return
            services_temp[sname] = {"km": s_km, "bulan": s_bl}
            refresh_temp_list()
            # Kosongkan input fields
            s_entry.delete(0, tk.END)
            km_entry.delete(0, tk.END)
            bl_entry.delete(0, tk.END)

        def refresh_temp_list():
            """Refresh tampilan list servis"""
            for w in list_frame.winfo_children():
                w.destroy()
            for s, v in services_temp.items():
                item_frame = ctk.CTkFrame(list_frame)
                item_frame.pack(fill="x", pady=2)
                ctk.CTkLabel(item_frame, text=f"• {s} - {v['km']} km / {v['bulan']} bln").pack(side="left", padx=5)
                ctk.CTkButton(item_frame, text="✕", width=30, height=30,
                            command=lambda sn=s: remove_service(sn)).pack(side="right", padx=5)

        def remove_service(service_name):
            """Hapus servis dari list"""
            services_temp.pop(service_name, None)
            refresh_temp_list()

        # Input fields untuk servis
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", pady=10)

        s_entry = ctk.CTkEntry(input_frame, placeholder_text="Nama Servis")
        s_entry.pack(pady=2)
        km_entry = ctk.CTkEntry(input_frame, placeholder_text="Interval KM")
        km_entry.pack(pady=2)
        bl_entry = ctk.CTkEntry(input_frame, placeholder_text="Interval Bulan")
        bl_entry.pack(pady=2)
        
        ctk.CTkButton(input_frame, text="➕ Tambah Servis", command=add_service_to_temp).pack(pady=5)

        def save_custom():
            """Simpan motor custom ke database"""
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Peringatan", "Nama motor kosong")
                return
            if not services_temp:
                messagebox.showwarning("Peringatan", "Tambahkan minimal 1 servis")
                return
            add_motor_to_db(name, services_temp, km_now=int(self.km_now_var.get() or 0))
            # Update dropdown motor
            values = list(MOTOR_PRESET.keys()) + self._load_custom_motor_names()
            self.motor_combo.configure(values=values)
            self.motor_combo.set(name)
            messagebox.showinfo("Sukses", f"Motor {name} berhasil ditambahkan!")
            win.destroy()

        ctk.CTkButton(main_frame, text="💾 Simpan Motor", command=save_custom, 
                     fg_color=self._theme_colors["good"]).pack(pady=10)

    # ----------------------
    # RENDER PANEL SERVIS
    # ----------------------
    def render_services(self):
        """Render semua kartu servis di panel utama"""
        # Hapus servis yang lama
        for w in self.services_scroll.winfo_children():
            w.destroy()

        if not self.services:
            ctk.CTkLabel(self.services_scroll, text="Tidak ada servis tersedia",
                        font=("Arial", 16), text_color=self._theme_colors["text_secondary"]).pack(pady=50)
            return

        km_now = int(self.km_now_var.get() or 0)
        theme = self._theme_colors

        # Buat kartu untuk setiap servis
        for sname, val in self.services.items():
            # Buat kartu animasi
            card = AnimatedCard(self.services_scroll, theme, height=120)
            card.pack(fill="x", padx=5, pady=8)
            card.grid_columnconfigure(1, weight=1)

            # Indicator status servis
            status_frame = ctk.CTkFrame(card, fg_color="transparent", width=100)
            status_frame.grid(row=0, column=0, rowspan=2, sticky="ns", padx=10, pady=10)

            # Progress bar lingkaran
            if val.get("next_due_km", 0) == 0:
                val["next_due_km"] = km_now + val["km"]
            
            next_km = val["next_due_km"]
            interval_km = max(1, val["km"])
            # Hitung rasio progress (0-1)
            progress_ratio = min(1.0, max(0.0, (interval_km - (next_km - km_now)) / interval_km))
            
            progress = CircularProgressBar(status_frame, size=60, theme=theme)
            progress.set_value(progress_ratio)
            progress.pack()

            # Info servis
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=(10, 0))
            info_frame.grid_columnconfigure(0, weight=1)

            # Nama dan status servis
            name_label = ctk.CTkLabel(info_frame, text=sname, font=("Arial", 16, "bold"), 
                                    anchor="w", text_color=theme["text"])
            name_label.grid(row=0, column=0, sticky="w")

            # Detail progress
            sisa_km = max(0, next_km - km_now)
            days_left = max(-9999, (val["next_due_date"] - datetime.now()).days)
            
            status_text = f"Sisa: {sisa_km} km | {days_left} hari"
            status_label = ctk.CTkLabel(info_frame, text=status_text, font=("Arial", 12),
                                      text_color=theme["text_secondary"], anchor="w")
            status_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

            # Tombol aksi
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.grid(row=0, column=2, rowspan=2, sticky="ns", padx=10, pady=10)

            ctk.CTkButton(btn_frame, text="✅ Selesai", width=100,
                         command=lambda sn=sname: self.mark_serviced(sn),
                         fg_color=theme["good"]).pack(pady=5)

            # Kode warna berdasarkan status
            if sisa_km <= 0 or days_left <= 0:
                status_color = theme["bad"]    # Merah - telat
                status_icon = "🔴"
            elif sisa_km <= max(50, int(interval_km*0.15)) or days_left <= 7:
                status_color = theme["warn"]   # Kuning - peringatan
                status_icon = "🟡"
            else:
                status_color = theme["good"]   # Hijau - aman
                status_icon = "🟢"

            # Update tampilan dengan warna dan icon
            name_label.configure(text=f"{status_icon} {sname}", text_color=status_color)
            status_label.configure(text_color=status_color)

            # Simpan reference widget untuk update nanti
            val["_widgets"] = {
                "card": card, "name_label": name_label, 
                "status_label": status_label, "progress": progress
            }

    # ----------------------
    # CEK PERIODIC & NOTIFIKASI
    # ----------------------
    def periodic_check(self):
        """Cek status servis secara periodic (setiap detik)"""
        if not self.current_motor:
            self.after(1000, self.periodic_check)
            return
        
        try:
            km_now = int(self.km_now_var.get() or 0)
        except:
            self.after(1000, self.periodic_check)
            return

        overdue_found = False
        for sname, val in self.services.items():
            if val.get("next_due_km", 0) == 0:
                val["next_due_km"] = km_now + val["km"]
            
            # Cek apakah servis sudah telat
            overdue_km = (km_now >= val["next_due_km"])
            overdue_date = (datetime.now() >= val["next_due_date"])
            
            # Update progress bar
            widgets = val.get("_widgets", {})
            if widgets.get("progress"):
                interval_km = max(1, val["km"])
                remaining_km = max(0, val["next_due_km"] - km_now)
                progress_ratio = min(1.0, max(0.0, (interval_km - remaining_km) / interval_km))
                widgets["progress"].set_value(progress_ratio)

            # Jika telat, tampilkan peringatan
            if overdue_km or overdue_date:
                overdue_found = True
                if not val.get("_alerted"):  # Hanya alert sekali
                    # Animasi kartu
                    if widgets.get("card"):
                        widgets["card"].animate_highlight()
                    # Tampilkan messagebox
                    messagebox.showwarning("⏰ Waktu Servis", 
                                         f"{self.current_motor} → {sname} sudah waktunya servis!\n\n"
                                         f"KM sekarang: {km_now}\n"
                                         f"KM due: {val['next_due_km']}")
                    val["_alerted"] = True  # Tandai sudah di-alert

        # Update statistik header
        self.update_stats_header()
        self.after(1000, self.periodic_check)  # Jadwalkan cek lagi

    # ----------------------
    # MARK SERVIS SELESAI
    # ----------------------
    def mark_serviced(self, service_name):
        """Tandai servis sebagai sudah dikerjakan"""
        if not self.current_motor:
            messagebox.showwarning("Peringatan", "Pilih motor terlebih dahulu")
            return
        
        try:
            km_now = int(self.km_now_var.get() or 0)
        except:
            messagebox.showerror("Error", "Masukkan KM sekarang yang valid")
            return
        
        val = self.services.get(service_name)
        if not val:
            return
        
        # Hitung jadwal servis berikutnya
        interval_km = int(val["km"])
        interval_bulan = int(val["bulan"])
        next_due_km = km_now + interval_km
        next_due_date = datetime.now() + timedelta(days=interval_bulan*30)
        
        # Update data di memory
        val["next_due_km"] = next_due_km
        val["next_due_date"] = next_due_date
        val["last_serviced_at"] = datetime.now()
        val["_alerted"] = False  # Reset status alert
        
        # Update database
        update_service_in_db(self.current_motor, service_name, 
                           next_due_km=next_due_km, 
                           next_due_date=next_due_date, 
                           last_serviced_at=datetime.now())
        
        # Catat di riwayat
        log_history(self.current_motor, service_name, km_now)
        
        # Animasi konfirmasi
        widgets = val.get("_widgets", {})
        if widgets.get("card"):
            widgets["card"].animate_highlight()
        
        messagebox.showinfo("✅ Berhasil", 
                          f"{service_name} telah ditandai selesai servis\npada KM {km_now}")
        
        # Refresh tampilan
        self.render_services()
        self.update_stats_header()

    # ----------------------
    # SIMPAN MOTOR KE DB
    # ----------------------
    def save_motor_db(self):
        """Simpan data motor saat ini ke database"""
        name = self.current_motor
        if not name:
            messagebox.showwarning("Peringatan", "Pilih atau buat motor terlebih dahulu")
            return
        
        add_motor_to_db(name, {k: {"km": v["km"], "bulan": v["bulan"]} for k, v in self.services.items()}, 
                       km_now=int(self.km_now_var.get() or 0))
        messagebox.showinfo("💾 Tersimpan", f"Data motor {name} berhasil disimpan!")

    # ----------------------
    # EKSPOR, RIWAYAT, HAPUS DB
    # ----------------------
    def export_history_dialog(self):
        """Export riwayat servis ke file CSV"""
        path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                          filetypes=[("CSV files","*.csv")],
                                          initialfile=f"motor_history_{datetime.now().strftime('%Y%m%d')}.csv")
        if not path:
            return
        export_history_csv(path)
        messagebox.showinfo("📤 Export Selesai", f"Riwayat berhasil diexport ke:\n{path}")

    def show_recent_history(self):
        """Tampilkan riwayat servis terbaru"""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT motor_name, service_name, when_served, km_at_service FROM history ORDER BY when_served DESC LIMIT 20")
        rows = c.fetchall()
        conn.close()
        
        # Buat window untuk menampilkan riwayat
        win = ctk.CTkToplevel(self)
        win.title("📋 Riwayat Servis Terbaru")
        win.geometry("700x500")
        win.transient(self)
        
        ctk.CTkLabel(win, text="Riwayat Servis 20 Terbaru", font=("Arial", 18, "bold")).pack(pady=10)
        
        text_frame = ctk.CTkFrame(win)
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        text_widget = ctk.CTkTextbox(text_frame, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        if not rows:
            text_widget.insert("1.0", "Belum ada riwayat servis")
        else:
            # Format riwayat dengan emoji
            history_text = "\n\n".join([
                f"📅 {r[2][:16]}\n"
                f"   🏍️ {r[0]} | 🔧 {r[1]} | 🛣️ KM {r[3]}"
                for r in rows
            ])
            text_widget.insert("1.0", history_text)
        
        text_widget.configure(state="disabled")  # Biar tidak bisa diedit

    def clear_all_db(self):
        """Hapus semua data dari database"""
        if not messagebox.askyesno("⚠️ Konfirmasi", 
                                 "Hapus SEMUA data dari database?\n\n"
                                 "Tindakan ini tidak dapat dibatalkan!"):
            return
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM motors")
        c.execute("DELETE FROM services")
        c.execute("DELETE FROM history")
        conn.commit()
        conn.close()
        
        messagebox.showinfo("🧹 Berhasil", "Semua data berhasil dihapus")
        # Reset UI
        self.motor_combo.set("")
        self.current_motor = None
        self.services = {}
        self.update_stats_header()
        self.render_services()

    # ----------------------
    # RESET JADWAL SERVIS
    # ----------------------
    def reset_next_due_manual(self):
        """Reset jadwal servis berdasarkan KM terakhir"""
        if not self.current_motor:
            messagebox.showwarning("Peringatan", "Pilih motor terlebih dahulu")
            return
        
        # Dialog input KM
        dialog = ctk.CTkInputDialog(text="Masukkan KM terakhir servis:", title="Reset Jadwal Servis")
        km_last = dialog.get_input()
        
        if km_last is None:
            return
            
        try:
            km_last = int(km_last)
        except:
            messagebox.showerror("Error", "Masukkan angka yang valid untuk KM")
            return
        
        # Update setiap servis
        for sname, val in self.services.items():
            new_next = km_last + val["km"]
            val["next_due_km"] = new_next
            update_service_in_db(self.current_motor, sname, next_due_km=new_next)
        
        messagebox.showinfo("🔄 Berhasil", "Jadwal servis berhasil direset!")
        self.render_services()

    # ----------------------
    # SIMULASI KM
    # ----------------------
    def _sim_thread_fn(self):
        """Thread untuk simulasi peningkatan KM"""
        while self.km_simulate:
            try:
                step = int(self.sim_speed.get())  # Ambil kecepatan dari slider
            except:
                step = 10
            
            # Tingkatkan KM
            current = int(self.km_now_var.get() or 0)
            current += step
            self.km_now_var.set(current)
            
            # Update UI di main thread
            self.after(0, self.render_services)
            self.after(0, self.update_stats_header)
            
            time.sleep(1)  # Tunggu 1 detik

    def start_simulation(self):
        """Mulai simulasi peningkatan KM"""
        if self.km_simulate:
            return
        
        self.km_simulate = True
        self.sim_thread = threading.Thread(target=self._sim_thread_fn, daemon=True)
        self.sim_thread.start()
        
        messagebox.showinfo("🚀 Simulasi", "Simulasi KM sedang berjalan...")

    def stop_simulation(self):
        """Hentikan simulasi"""
        self.km_simulate = False
        if hasattr(self, 'sim_thread') and self.sim_thread:
            self.sim_thread = None

    # ----------------------
    # TUTUP APLIKASI
    # ----------------------
    def on_close(self):
        """Handle ketika aplikasi ditutup"""
        self.km_simulate = False  # Hentikan simulasi
        self.quit()

# --------------------------
# JALANKAN APLIKASI
# --------------------------
if __name__ == "__main__":
    # Pastikan motor preset ada di database
    for pname, pservices in MOTOR_PRESET.items():
        add_motor_to_db(pname, pservices, km_now=0)
    
    # Jalankan aplikasi
    app = MotorMaintenanceApp()
    app.mainloop()
