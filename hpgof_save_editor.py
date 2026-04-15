"""
╔══════════════════════════════════════════════════════════════╗
║  Harry Potter and the Goblet of Fire — Save Editor v1.0     ║
║  A visual save editor for the 2005 EA PC game               ║
║  Edit Triwizard Shields, mini-shields, and game flags        ║
╚══════════════════════════════════════════════════════════════╝

Copyright (c) 2026 tomigorn
Licensed under CC BY-NC-SA 4.0 — https://creativecommons.org/licenses/by-nc-sa/4.0/
"""

import struct
import shutil
import os
import sys
import ctypes
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Set AppUserModelID so Windows taskbar shows our icon, not Python's
if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("tomigorn.hpgof.saveeditor")

# ─────────────────────────────────────────────────────────
# Save file binary format constants
# ─────────────────────────────────────────────────────────

MAGIC = b'\x32\x30\x43\x4D'  # "20CM"

# Header offset for total big shields count
HEADER_TOTAL_OFF = 0x00C0

# Second total counter (GlobalData idx 1)
IDX1_TOTAL_OFF = 0x0806

# Level names (mapped from level codes & guide walkthrough)
LEVEL_NAMES = [
    "Defense Against the Dark Arts",
    "Hogwarts Exterior",
    "Moody's Challenges",
    "Forbidden Forest",
    "Triwizard Task 1",
    "Prefects' Bathroom",
    "Herbology",
    "Triwizard Task 2",
    "Triwizard Task 3",
    "Voldemort",
]

# Guide shield counts per level (from the official FAQ/Walkthrough)
GUIDE_SHIELDS = [1, 8, 0, 8, 3, 8, 8, 3, 0, 0]  # total = 39 (guide says 38, DATDA=1 is tutorial)

# ── Per-level group offsets ──
# Set 2 (idx 149-198): main shield tracking per level
# Structure per group: [seq_val_off, code_val_off, avail_val_off, collected_val_off, big_shields_val_off]
LEVEL_GROUPS = [
    # (avail_offset, collected_offset, big_shields_offset)
    (0x0512, 0x051E, 0x052A),   # Level 100 -> DATDA
    (0x054E, 0x055A, 0x0566),   # Level 101 -> Hogwarts Exterior
    (0x058A, 0x0596, 0x05A2),   # Level 102 -> Moody's Challenges
    (0x05C6, 0x05D2, 0x05DE),   # Level 103 -> Forbidden Forest
    (0x0602, 0x060E, 0x061A),   # Level 104 -> Triwizard Task 1
    (0x063E, 0x064A, 0x0656),   # Level 105 -> Prefects' Bathroom
    (0x067A, 0x0686, 0x0692),   # Level 106 -> Herbology
    (0x06B6, 0x06C2, 0x06CE),   # Level 107 -> Triwizard Task 2
    (0x06F2, 0x06FE, 0x070A),   # Level 108 -> Triwizard Task 3
    (0x072E, 0x073A, 0x0746),   # Level 109 -> Voldemort
]

# Set 1 (idx 99-148): secondary tracking (mini-shields / generators)
FIRST_SET_GROUPS = [
    (0x02BA, 0x02C6, 0x02D2),
    (0x02F6, 0x0302, 0x030E),
    (0x0332, 0x033E, 0x034A),
    (0x036E, 0x037A, 0x0386),
    (0x03AA, 0x03B6, 0x03C2),
    (0x03E6, 0x03F2, 0x03FE),
    (0x0422, 0x042E, 0x043A),
    (0x045E, 0x046A, 0x0476),
    (0x049A, 0x04A6, 0x04B2),
    (0x04D6, 0x04E2, 0x04EE),
]

# SaveFlags value offsets (8 x uint32 bitmasks)
SAVEFLAGS_OFFSETS = [
    0x0C42, 0x0C4E, 0x0C5A, 0x0C66,
    0x0C72, 0x0C7E, 0x0C8A, 0x0C96,
]

# ── Default save file path ──
DEFAULT_SAVE_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA", ""),
    "Electronic Arts",
    "Harry Potter and the Goblet of Fire",
    "HPGOF",
)
DEFAULT_SAVE_FILE = os.path.join(DEFAULT_SAVE_DIR, "HPGOF")


# ─────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────

def read_u32(data, off):
    return struct.unpack_from('<I', data, off)[0]

def write_u32(data, off, val):
    struct.pack_into('<I', data, off, val & 0xFFFFFFFF)

def validate_save(data):
    """Check if data looks like a valid HPGOF save."""
    if len(data) < 0x0D00:
        return False
    if data[0:4] != MAGIC:
        return False
    return True

def make_backup(filepath):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = filepath + f".backup_{ts}"
    shutil.copy2(filepath, dst)
    return dst

def find_backups(filepath):
    """Return list of backup files sorted oldest first."""
    directory = os.path.dirname(filepath)
    basename = os.path.basename(filepath)
    backups = []
    if os.path.isdir(directory):
        for f in sorted(os.listdir(directory)):
            if f.startswith(basename + ".backup_"):
                backups.append(os.path.join(directory, f))
    return backups


# ─────────────────────────────────────────────────────────
# Color palette (Hogwarts-inspired)
# ─────────────────────────────────────────────────────────

COLORS = {
    "bg_dark":      "#1a1a2e",
    "bg_mid":       "#16213e",
    "bg_card":      "#0f3460",
    "accent_gold":  "#e6b422",
    "accent_light": "#f5d061",
    "text":         "#e8e8e8",
    "text_dim":     "#8899aa",
    "text_dark":    "#1a1a2e",
    "success":      "#4ecca3",
    "danger":       "#e74c3c",
    "shield_full":  "#f5d061",
    "shield_empty": "#2c3e50",
    "btn_primary":  "#2980b9",
    "btn_success":  "#27ae60",
    "btn_danger":   "#c0392b",
    "btn_text":     "#ffffff",
    "entry_bg":     "#1e3a5f",
    "border":       "#3a506b",
}


# ─────────────────────────────────────────────────────────
# Main Application
# ─────────────────────────────────────────────────────────

class SaveEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Harry Potter: Goblet of Fire — Save Editor")
        self.root.configure(bg=COLORS["bg_dark"])
        self.root.resizable(True, True)

        # State
        self.filepath = None
        self.data = None
        self.level_vars = []       # (avail_var, collected_var, big_var) per level
        self.set1_vars = []        # (avail_var, collected_var, big_var) per set1 group
        self.flag_vars = []        # StringVar per flag
        self.total_var = tk.StringVar(value="—")
        self.file_label_var = tk.StringVar(value="No file loaded")

        # Try to set icon — silently skip if not available
        try:
            base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base, "app_icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(default=icon_path)
        except Exception:
            pass

        self._build_styles()
        self._build_ui()

        # Auto-load if default save exists
        if os.path.isfile(DEFAULT_SAVE_FILE):
            self._load_file(DEFAULT_SAVE_FILE)

    # ── Styles ──

    def _build_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Dark.TFrame", background=COLORS["bg_dark"])
        style.configure("Card.TFrame", background=COLORS["bg_card"], relief="flat")
        style.configure("Mid.TFrame", background=COLORS["bg_mid"])

        style.configure("Title.TLabel",
                        background=COLORS["bg_dark"],
                        foreground=COLORS["accent_gold"],
                        font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel",
                        background=COLORS["bg_dark"],
                        foreground=COLORS["text_dim"],
                        font=("Segoe UI", 10))
        style.configure("Dark.TLabel",
                        background=COLORS["bg_dark"],
                        foreground=COLORS["text"],
                        font=("Segoe UI", 10))
        style.configure("Card.TLabel",
                        background=COLORS["bg_card"],
                        foreground=COLORS["text"],
                        font=("Segoe UI", 10))
        style.configure("CardBold.TLabel",
                        background=COLORS["bg_card"],
                        foreground=COLORS["accent_light"],
                        font=("Segoe UI", 10, "bold"))
        style.configure("CardDim.TLabel",
                        background=COLORS["bg_card"],
                        foreground=COLORS["text_dim"],
                        font=("Segoe UI", 9))
        style.configure("Total.TLabel",
                        background=COLORS["bg_dark"],
                        foreground=COLORS["accent_gold"],
                        font=("Segoe UI", 14, "bold"))
        style.configure("Mid.TLabel",
                        background=COLORS["bg_mid"],
                        foreground=COLORS["text"],
                        font=("Segoe UI", 10))
        style.configure("MidBold.TLabel",
                        background=COLORS["bg_mid"],
                        foreground=COLORS["accent_light"],
                        font=("Segoe UI", 10, "bold"))
        style.configure("MidDim.TLabel",
                        background=COLORS["bg_mid"],
                        foreground=COLORS["text_dim"],
                        font=("Segoe UI", 9))
        style.configure("Section.TLabel",
                        background=COLORS["bg_dark"],
                        foreground=COLORS["accent_gold"],
                        font=("Segoe UI", 12, "bold"))
        style.configure("File.TLabel",
                        background=COLORS["bg_dark"],
                        foreground=COLORS["text_dim"],
                        font=("Segoe UI", 9))
        style.configure("StatusOk.TLabel",
                        background=COLORS["bg_dark"],
                        foreground=COLORS["success"],
                        font=("Segoe UI", 9))
        style.configure("StatusBad.TLabel",
                        background=COLORS["bg_dark"],
                        foreground=COLORS["danger"],
                        font=("Segoe UI", 9))

        # Buttons
        style.configure("Primary.TButton",
                        background=COLORS["btn_primary"],
                        foreground=COLORS["btn_text"],
                        font=("Segoe UI", 10, "bold"),
                        padding=(12, 6))
        style.map("Primary.TButton",
                  background=[("active", "#3498db"), ("disabled", "#555555")])

        style.configure("Success.TButton",
                        background=COLORS["btn_success"],
                        foreground=COLORS["btn_text"],
                        font=("Segoe UI", 10, "bold"),
                        padding=(12, 6))
        style.map("Success.TButton",
                  background=[("active", "#2ecc71"), ("disabled", "#555555")])

        style.configure("Danger.TButton",
                        background=COLORS["btn_danger"],
                        foreground=COLORS["btn_text"],
                        font=("Segoe UI", 10, "bold"),
                        padding=(12, 6))
        style.map("Danger.TButton",
                  background=[("active", "#e74c3c"), ("disabled", "#555555")])

        style.configure("Small.TButton",
                        background=COLORS["bg_card"],
                        foreground=COLORS["accent_light"],
                        font=("Segoe UI", 9),
                        padding=(6, 2))
        style.map("Small.TButton",
                  background=[("active", "#1a5276")])

    # ── UI Construction ──

    def _build_ui(self):
        # Main container with scrollbar
        outer = tk.Frame(self.root, bg=COLORS["bg_dark"])
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=COLORS["bg_dark"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=COLORS["bg_dark"])

        self.scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self._build_header()
        self._build_file_bar()
        self._build_level_section()
        self._build_set1_section()
        self._build_flags_section()
        self._build_action_bar()
        self._build_footer()

        # Set minimum window size
        self.root.update_idletasks()
        self.root.minsize(720, 500)
        self.root.geometry("780x820")

    def _build_header(self):
        frame = tk.Frame(self.scroll_frame, bg=COLORS["bg_dark"], pady=12)
        frame.pack(fill="x", padx=20)

        ttk.Label(frame, text="⚡ Harry Potter: Goblet of Fire", style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text="Save File Editor  •  Triwizard Shield Manager", style="Subtitle.TLabel").pack(anchor="w")

    def _build_file_bar(self):
        frame = tk.Frame(self.scroll_frame, bg=COLORS["bg_dark"], pady=4)
        frame.pack(fill="x", padx=20)

        row = tk.Frame(frame, bg=COLORS["bg_dark"])
        row.pack(fill="x")

        ttk.Label(row, textvariable=self.file_label_var, style="File.TLabel").pack(side="left")

        btn_frame = tk.Frame(row, bg=COLORS["bg_dark"])
        btn_frame.pack(side="right")

        ttk.Button(btn_frame, text="📁 Open File", style="Primary.TButton",
                   command=self._browse_file).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="🔄 Reload", style="Small.TButton",
                   command=self._reload_file).pack(side="left")

        # Separator
        sep = tk.Frame(self.scroll_frame, bg=COLORS["border"], height=1)
        sep.pack(fill="x", padx=20, pady=(8, 4))

    def _build_level_section(self):
        container = tk.Frame(self.scroll_frame, bg=COLORS["bg_dark"], pady=6)
        container.pack(fill="x", padx=20)

        # Section header with total
        header = tk.Frame(container, bg=COLORS["bg_dark"])
        header.pack(fill="x", pady=(0, 8))

        ttk.Label(header, text="🛡️  Triwizard Shields", style="Section.TLabel").pack(side="left")
        total_frame = tk.Frame(header, bg=COLORS["bg_dark"])
        total_frame.pack(side="right")
        ttk.Label(total_frame, text="Total: ", style="Dark.TLabel").pack(side="left")
        ttk.Label(total_frame, textvariable=self.total_var, style="Total.TLabel").pack(side="left")

        # Column headers
        col_header = tk.Frame(container, bg=COLORS["bg_dark"])
        col_header.pack(fill="x", pady=(0, 4))
        labels = [("Level", 200), ("Available", 75), ("Collected", 75), ("Big Shields", 80), ("", 60)]
        for text, width in labels:
            lbl = ttk.Label(col_header, text=text, style="Subtitle.TLabel", width=width // 8)
            lbl.pack(side="left", padx=4)

        # Level rows
        self.level_vars = []
        self.level_widgets = []  # (avail_entry, coll_entry, big_entry, max_btn)
        for i, name in enumerate(LEVEL_NAMES):
            row_frame = tk.Frame(container, bg=COLORS["bg_card"], pady=5, padx=10)
            row_frame.pack(fill="x", pady=1)

            guide_count = GUIDE_SHIELDS[i]
            no_shields = guide_count == 0
            name_text = f"{name}"
            if guide_count > 0:
                name_text += f"  ({guide_count} in game)"
            else:
                name_text += "  (no shields)"

            lbl = ttk.Label(row_frame, text=name_text, style="CardBold.TLabel", width=28)
            lbl.pack(side="left")

            avail_var = tk.StringVar(value="—")
            coll_var = tk.StringVar(value="—")
            big_var = tk.StringVar(value="—")

            disabled_fg = "#555555"
            entry_fg = disabled_fg if no_shields else COLORS["text"]
            gold_fg = disabled_fg if no_shields else COLORS["accent_gold"]

            avail_entry = tk.Entry(row_frame, textvariable=avail_var, width=7, justify="center",
                                   bg=COLORS["entry_bg"], fg=entry_fg, font=("Consolas", 10),
                                   insertbackground=COLORS["text"], relief="flat", bd=2)
            avail_entry.pack(side="left", padx=4)

            coll_entry = tk.Entry(row_frame, textvariable=coll_var, width=7, justify="center",
                                  bg=COLORS["entry_bg"], fg=entry_fg, font=("Consolas", 10),
                                  insertbackground=COLORS["text"], relief="flat", bd=2)
            coll_entry.pack(side="left", padx=4)

            big_entry = tk.Entry(row_frame, textvariable=big_var, width=7, justify="center",
                                 bg=COLORS["entry_bg"], fg=gold_fg, font=("Consolas", 10, "bold"),
                                 insertbackground=COLORS["text"], relief="flat", bd=2)
            big_entry.pack(side="left", padx=4)

            # Max button per row
            max_btn = ttk.Button(row_frame, text="MAX", style="Small.TButton",
                                 command=lambda idx=i: self._max_level(idx))
            max_btn.pack(side="left", padx=8)

            if no_shields:
                for entry in (avail_entry, coll_entry, big_entry):
                    entry.configure(state="disabled", disabledbackground=COLORS["entry_bg"],
                                    disabledforeground=disabled_fg)
                max_btn.configure(state="disabled")

            self.level_vars.append((avail_var, coll_var, big_var))
            self.level_widgets.append((avail_entry, coll_entry, big_entry, max_btn))

    def _build_set1_section(self):
        container = tk.Frame(self.scroll_frame, bg=COLORS["bg_dark"], pady=6)
        container.pack(fill="x", padx=20)

        # Collapsible section
        self.set1_visible = tk.BooleanVar(value=False)
        toggle_frame = tk.Frame(container, bg=COLORS["bg_dark"])
        toggle_frame.pack(fill="x", pady=(8, 4))

        self.set1_toggle_btn = ttk.Button(toggle_frame, text="▶  Mini-Shield Generators (Advanced)",
                                           style="Small.TButton", command=self._toggle_set1)
        self.set1_toggle_btn.pack(anchor="w")

        self.set1_frame = tk.Frame(container, bg=COLORS["bg_dark"])
        # Don't pack yet — hidden by default

        set1_labels = [
            "Generator Set A", "Generator Set B", "Generator Set C",
            "Generator Set D", "Generator Set E", "Generator Set F",
            "Generator Set G", "Generator Set H", "Generator Set I",
            "Generator Set J",
        ]

        # Column headers
        col_header = tk.Frame(self.set1_frame, bg=COLORS["bg_dark"])
        col_header.pack(fill="x", pady=(0, 4))
        for text, width in [("Group", 180), ("Available", 75), ("Collected", 75), ("Shields", 80), ("", 60)]:
            lbl = ttk.Label(col_header, text=text, style="Subtitle.TLabel", width=width // 8)
            lbl.pack(side="left", padx=4)

        self.set1_vars = []
        for i, name in enumerate(set1_labels):
            row_frame = tk.Frame(self.set1_frame, bg=COLORS["bg_mid"], pady=4, padx=10)
            row_frame.pack(fill="x", pady=1)

            no_shields = GUIDE_SHIELDS[i] == 0
            label_text = name if not no_shields else f"{name}  (no shields)"
            ttk.Label(row_frame, text=label_text, style="MidBold.TLabel", width=24).pack(side="left")

            avail_var = tk.StringVar(value="—")
            coll_var = tk.StringVar(value="—")
            big_var = tk.StringVar(value="—")

            disabled_fg = "#555555"
            entries = []
            for var in [avail_var, coll_var, big_var]:
                fg = disabled_fg if no_shields else COLORS["text"]
                e = tk.Entry(row_frame, textvariable=var, width=7, justify="center",
                             bg=COLORS["entry_bg"], fg=fg, font=("Consolas", 10),
                             insertbackground=COLORS["text"], relief="flat", bd=2)
                e.pack(side="left", padx=4)
                entries.append(e)

            max_btn = ttk.Button(row_frame, text="MAX", style="Small.TButton",
                                 command=lambda idx=i: self._max_set1(idx))
            max_btn.pack(side="left", padx=8)

            if no_shields:
                for e in entries:
                    e.configure(state="disabled", disabledbackground=COLORS["entry_bg"],
                                disabledforeground=disabled_fg)
                max_btn.configure(state="disabled")

            self.set1_vars.append((avail_var, coll_var, big_var))

    def _build_flags_section(self):
        container = tk.Frame(self.scroll_frame, bg=COLORS["bg_dark"], pady=6)
        container.pack(fill="x", padx=20)

        # Collapsible
        self.flags_visible = tk.BooleanVar(value=False)
        toggle_frame = tk.Frame(container, bg=COLORS["bg_dark"])
        toggle_frame.pack(fill="x", pady=(8, 4))

        self.flags_toggle_btn = ttk.Button(toggle_frame, text="▶  SaveFlags — Game Progression Flags (Advanced)",
                                            style="Small.TButton", command=self._toggle_flags)
        self.flags_toggle_btn.pack(anchor="w")

        self.flags_frame = tk.Frame(container, bg=COLORS["bg_dark"])
        # Hidden by default

        info_label = ttk.Label(self.flags_frame,
                               text="These bitmask flags track game progression (quests, pickups, cutscenes).\n"
                                    "Setting all bits to 1 (0xFFFFFFFF) marks everything as complete.",
                               style="Subtitle.TLabel", wraplength=700, justify="left")
        info_label.pack(anchor="w", pady=(0, 6))

        self.flag_vars = []
        for i in range(8):
            row = tk.Frame(self.flags_frame, bg=COLORS["bg_mid"], pady=3, padx=10)
            row.pack(fill="x", pady=1)

            ttk.Label(row, text=f"Flag[{i}]", style="MidBold.TLabel", width=8).pack(side="left")

            var = tk.StringVar(value="00000000")
            entry = tk.Entry(row, textvariable=var, width=12, justify="center",
                             bg=COLORS["entry_bg"], fg=COLORS["accent_light"], font=("Consolas", 10),
                             insertbackground=COLORS["text"], relief="flat", bd=2)
            entry.pack(side="left", padx=8)

            self.bits_label = ttk.Label(row, text="(0 bits)", style="MidDim.TLabel")
            self.bits_label.pack(side="left")

            self.flag_vars.append((var, self.bits_label))

    def _build_action_bar(self):
        sep = tk.Frame(self.scroll_frame, bg=COLORS["border"], height=1)
        sep.pack(fill="x", padx=20, pady=(12, 8))

        frame = tk.Frame(self.scroll_frame, bg=COLORS["bg_dark"], pady=8)
        frame.pack(fill="x", padx=20)

        left = tk.Frame(frame, bg=COLORS["bg_dark"])
        left.pack(side="left")

        ttk.Button(left, text="⚡ MAX ALL SHIELDS", style="Success.TButton",
                   command=self._max_all).pack(side="left", padx=(0, 8))
        ttk.Button(left, text="🗑️ Reset to Original", style="Danger.TButton",
                   command=self._restore_backup).pack(side="left", padx=(0, 8))

        right = tk.Frame(frame, bg=COLORS["bg_dark"])
        right.pack(side="right")

        ttk.Button(right, text="💾 SAVE", style="Success.TButton",
                   command=self._save_file).pack(side="right", padx=(8, 0))

        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(self.scroll_frame, textvariable=self.status_var, style="StatusOk.TLabel")
        self.status_label.pack(anchor="w", padx=24, pady=(0, 4))

    def _build_footer(self):
        sep = tk.Frame(self.scroll_frame, bg=COLORS["border"], height=1)
        sep.pack(fill="x", padx=20, pady=(8, 4))

        footer = tk.Frame(self.scroll_frame, bg=COLORS["bg_dark"], pady=8)
        footer.pack(fill="x", padx=20)

        ttk.Label(footer,
                  text="HP Goblet of Fire Save Editor v1.0  •  A backup is created each time you save.",
                  style="Subtitle.TLabel").pack(side="left")

    # ── File operations ──

    def _browse_file(self):
        initial_dir = DEFAULT_SAVE_DIR if os.path.isdir(DEFAULT_SAVE_DIR) else os.path.expanduser("~")
        path = filedialog.askopenfilename(
            title="Open HPGOF Save File",
            initialdir=initial_dir,
            filetypes=[("HPGOF Save", "HPGOF"), ("All Files", "*.*")],
        )
        if path:
            self._load_file(path)

    def _load_file(self, path):
        try:
            with open(path, 'rb') as f:
                data = bytearray(f.read())
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{e}")
            return

        if not validate_save(data):
            messagebox.showerror("Invalid File",
                                 "This does not appear to be a valid HPGOF save file.\n"
                                 "Expected '20CM' magic header.")
            return

        self.filepath = path
        self.data = data
        self.file_label_var.set(f"📄 {path}")
        self._refresh_ui()
        self._set_status(f"Loaded successfully ({len(data):,} bytes)", ok=True)

    def _reload_file(self):
        if self.filepath:
            self._load_file(self.filepath)
        else:
            messagebox.showinfo("No File", "No file is currently loaded.")

    def _refresh_ui(self):
        """Read data and update all UI fields."""
        if self.data is None:
            return

        data = self.data

        # Levels (set 2)
        total = 0
        for i, (avail_off, coll_off, big_off) in enumerate(LEVEL_GROUPS):
            avail = GUIDE_SHIELDS[i]
            coll = read_u32(data, coll_off)
            big = read_u32(data, big_off)
            total += big

            av, cv, bv = self.level_vars[i]
            if avail == 0:
                av.set("N/A")
                cv.set("N/A")
                bv.set("N/A")
            else:
                av.set(str(avail))
                cv.set(str(coll))
                bv.set(str(big))

        self.total_var.set(str(total))

        # Set 1
        for i, (avail_off, coll_off, big_off) in enumerate(FIRST_SET_GROUPS):
            avail = GUIDE_SHIELDS[i]
            coll = read_u32(data, coll_off)
            big = read_u32(data, big_off)

            av, cv, bv = self.set1_vars[i]
            if avail == 0:
                av.set("N/A")
                cv.set("N/A")
                bv.set("N/A")
            else:
                av.set(str(avail))
                cv.set(str(coll))
                bv.set(str(big))

        # Flags
        for i, off in enumerate(SAVEFLAGS_OFFSETS):
            val = read_u32(data, off)
            var, bits_label = self.flag_vars[i]
            var.set(f"{val:08X}")
            bits = bin(val).count('1')
            bits_label.configure(text=f"({bits} bits set)")

    def _apply_ui_to_data(self):
        """Write UI field values back into self.data."""
        if self.data is None:
            return False

        data = self.data
        new_total = 0
        errors = []

        # Levels (set 2)
        for i, (avail_off, coll_off, big_off) in enumerate(LEVEL_GROUPS):
            if GUIDE_SHIELDS[i] == 0:
                write_u32(data, avail_off, 0)
                write_u32(data, coll_off, 0)
                write_u32(data, big_off, 0)
                continue
            try:
                avail = int(self.level_vars[i][0].get())
                coll = int(self.level_vars[i][1].get())
                big = int(self.level_vars[i][2].get())
            except ValueError:
                errors.append(f"Invalid number in {LEVEL_NAMES[i]}")
                continue

            write_u32(data, avail_off, avail)
            write_u32(data, coll_off, coll)
            write_u32(data, big_off, big)
            new_total += big

        # Set 1
        for i, (avail_off, coll_off, big_off) in enumerate(FIRST_SET_GROUPS):
            if GUIDE_SHIELDS[i] == 0:
                write_u32(data, avail_off, 0)
                write_u32(data, coll_off, 0)
                write_u32(data, big_off, 0)
                continue
            try:
                avail = int(self.set1_vars[i][0].get())
                coll = int(self.set1_vars[i][1].get())
                big = int(self.set1_vars[i][2].get())
            except ValueError:
                errors.append(f"Invalid number in Generator Set {chr(65+i)}")
                continue

            write_u32(data, avail_off, avail)
            write_u32(data, coll_off, coll)
            write_u32(data, big_off, big)

        # Totals
        write_u32(data, HEADER_TOTAL_OFF, new_total)
        write_u32(data, IDX1_TOTAL_OFF, new_total)

        # Flags
        for i, off in enumerate(SAVEFLAGS_OFFSETS):
            try:
                val = int(self.flag_vars[i][0].get(), 16)
                write_u32(data, off, val)
            except ValueError:
                errors.append(f"Invalid hex in Flag[{i}]")

        if errors:
            messagebox.showwarning("Warnings", "Some fields had issues:\n" + "\n".join(errors))

        self.total_var.set(str(new_total))
        return True

    def _save_file(self):
        if self.data is None or self.filepath is None:
            messagebox.showinfo("No File", "No save file is loaded.")
            return

        if not self._apply_ui_to_data():
            return

        # Backup
        try:
            backup_path = make_backup(self.filepath)
        except Exception as e:
            messagebox.showerror("Backup Failed", f"Could not create backup:\n{e}")
            return

        # Save
        try:
            with open(self.filepath, 'wb') as f:
                f.write(self.data)
        except Exception as e:
            messagebox.showerror("Save Failed", f"Could not write save file:\n{e}")
            return

        self._set_status(f"Saved! Backup: {os.path.basename(backup_path)}", ok=True)

    # ── Quick actions ──

    def _max_level(self, idx):
        """Set a single level row to max using known correct shield counts."""
        avail_var, coll_var, big_var = self.level_vars[idx]
        correct = GUIDE_SHIELDS[idx]
        avail_var.set(str(correct))
        coll_var.set(str(correct))
        big_var.set(str(correct))
        self._update_total_display()

    def _max_set1(self, idx):
        avail_var, coll_var, big_var = self.set1_vars[idx]
        correct = GUIDE_SHIELDS[idx]
        avail_var.set(str(correct))
        coll_var.set(str(correct))

    def _max_all(self):
        """Maximize everything."""
        if self.data is None:
            messagebox.showinfo("No File", "Load a save file first.")
            return

        # Max all levels
        for i in range(len(LEVEL_GROUPS)):
            self._max_level(i)

        # Max all set1
        for i in range(len(FIRST_SET_GROUPS)):
            self._max_set1(i)

        # Max all flags
        for i in range(8):
            self.flag_vars[i][0].set("FFFFFFFF")
            self.flag_vars[i][1].configure(text="(32 bits set)")

        self._update_total_display()
        self._set_status("All shields and flags maximized! Click SAVE to write.", ok=True)

    def _restore_backup(self):
        if self.filepath is None:
            messagebox.showinfo("No File", "No save file is loaded.")
            return

        backups = find_backups(self.filepath)
        if not backups:
            messagebox.showinfo("No Backups", "No backup files found.")
            return

        # Show backup selection
        result = messagebox.askyesno(
            "Restore Backup",
            f"Restore from the oldest backup?\n\n"
            f"{os.path.basename(backups[0])}\n\n"
            f"({len(backups)} backup(s) available)\n\n"
            f"This will overwrite the current save file."
        )

        if result:
            try:
                shutil.copy2(backups[0], self.filepath)
                self._load_file(self.filepath)
                self._set_status("Restored from original backup!", ok=True)
            except Exception as e:
                messagebox.showerror("Restore Failed", f"Could not restore:\n{e}")

    def _update_total_display(self):
        total = 0
        for avail_var, coll_var, big_var in self.level_vars:
            try:
                total += int(big_var.get())
            except ValueError:
                pass
        self.total_var.set(str(total))

    # ── Toggle sections ──

    def _toggle_set1(self):
        if self.set1_visible.get():
            self.set1_frame.pack_forget()
            self.set1_toggle_btn.configure(text="▶  Mini-Shield Generators (Advanced)")
            self.set1_visible.set(False)
        else:
            self.set1_frame.pack(fill="x")
            self.set1_toggle_btn.configure(text="▼  Mini-Shield Generators (Advanced)")
            self.set1_visible.set(True)

    def _toggle_flags(self):
        if self.flags_visible.get():
            self.flags_frame.pack_forget()
            self.flags_toggle_btn.configure(text="▶  SaveFlags — Game Progression Flags (Advanced)")
            self.flags_visible.set(False)
        else:
            self.flags_frame.pack(fill="x")
            self.flags_toggle_btn.configure(text="▼  SaveFlags — Game Progression Flags (Advanced)")
            self.flags_visible.set(True)

    # ── Status ──

    def _set_status(self, text, ok=True):
        self.status_var.set(text)
        self.status_label.configure(style="StatusOk.TLabel" if ok else "StatusBad.TLabel")


# ─────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    app = SaveEditorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
