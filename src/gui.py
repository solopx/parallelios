import tkinter as tk
from tkinter import ttk, scrolledtext

# ==============================================================================
# Color palette and fonts
# ==============================================================================

COLORS = {
    "bg":         "#C0C0C0",
    "bg_input":   "#FFFFFF",
    "fg":         "#000000",
    "fg_muted":   "#808080",
    "fg_accent":  "#000080",
    "fg_value":   "#000000",
    "console_bg": "#000000",
    "console_fg": "#00CC00",
    "btn_start":  "#008000",
    "btn_stop":   "#800000",
}

FONT =          ("Ubuntu", 10)
FONT_BOLD =     ("Consolas", 12, "bold")
FONT_SMALL =    ("Ubuntu", 10, "italic")
FONT_MONO =     ("Consolas", 10)
FONT_MONO_B =   ("Consolas", 10, "bold")
FONT_TITLE =    ("Consolas", 22, "bold")

APP_NAME = "Parallel.IOS"
APP_VERSION = "v2.0.1"

# ==============================================================================
# Global styles
# ==============================================================================

def configure_theme(root):

    root.option_add("*Background",                      COLORS["bg"])
    root.option_add("*Foreground",                      COLORS["fg"])
    root.option_add("*Entry.background",                COLORS["bg_input"])
    root.option_add("*Entry.foreground",                COLORS["fg_value"])
    root.option_add("*Entry.insertBackground",          COLORS["fg"])
    root.option_add("*Entry.relief",                    "sunken")
    root.option_add("*Entry.borderWidth",               2)
    root.option_add("*Entry.disabledBackground",        COLORS["bg"])
    root.option_add("*Entry.disabledForeground",        "#808080")
    root.option_add("*Text.background",                 COLORS["bg_input"])
    root.option_add("*Text.foreground",                 COLORS["fg_value"])
    root.option_add("*Text.insertBackground",           COLORS["fg_value"])
    root.option_add("*Text.relief",                     "sunken")
    root.option_add("*Text.borderWidth",                2)
    root.option_add("*Checkbutton.foreground",          COLORS["fg"])
    root.option_add("*Checkbutton.selectColor",         COLORS["bg_input"])
    root.option_add("*Checkbutton.activeBackground",    COLORS["bg"])
    root.option_add("*Checkbutton.disabledForeground",  COLORS["fg"])
    root.option_add("*Text.font",  FONT_MONO)
    root.option_add("*Entry.font",  FONT_MONO)
    root.configure(                                     bg=COLORS["bg"])

    style = ttk.Style()
    style.theme_use("classic")
    style.configure("TLabel",            background=COLORS["bg"], foreground=COLORS["fg"],        font=FONT)
    style.configure("Muted.TLabel",      background=COLORS["bg"], foreground=COLORS["fg"],        font=FONT)
    style.configure("Hint.TLabel",       background=COLORS["bg"], foreground=COLORS["fg_muted"],  font=FONT_SMALL)
    style.configure("TLabelframe",       background=COLORS["bg"], foreground=COLORS["fg"])
    style.configure("TLabelframe.Label", background=COLORS["bg"], foreground=COLORS["fg"],        font=FONT_BOLD)
    style.configure("TCombobox",
        fieldbackground=COLORS["bg_input"],
        background=COLORS["bg"],
        foreground=COLORS["fg_value"],
        arrowcolor=COLORS["fg"],
        selectbackground=COLORS["bg_input"],
        selectforeground=COLORS["fg_value"],
    )
    style.map("TCombobox",
        fieldbackground=[("readonly", COLORS["bg_input"]), ("disabled", COLORS["bg_input"])],
        foreground=[("readonly", COLORS["fg_value"]), ("disabled", COLORS["fg_value"])],
        selectbackground=[("readonly", COLORS["bg_input"]), ("disabled", COLORS["bg_input"])],
        selectforeground=[("readonly", COLORS["fg_value"]), ("disabled", COLORS["fg_value"])],
    )

# ==============================================================================
# GUI assembly
# ==============================================================================

def build_gui():
    root = tk.Tk()
    root.title(f"{APP_NAME} - {APP_VERSION}")
    root.geometry("900x950")
    root.resizable(False, True)

    configure_theme(root)

    main_container = tk.Frame(root, padx=15, pady=10)
    main_container.pack(fill="both", expand=True)

    # ==================================================================
    # TITLE
    # ==================================================================

    header_frame = tk.Frame(
    main_container,
    bg=COLORS["bg"],
    width=900,
    height=80,
    relief="groove",
    borderwidth=2,
    )
    header_frame.pack_propagate(False)
    header_frame.pack(pady=(10, 20))

    lbl_title = tk.Label(
    header_frame,
    text=APP_NAME,
    bg=COLORS["bg"],
    fg=COLORS["fg"],
    font=(FONT_TITLE),
    justify="center",
    anchor="center"
    )
    lbl_title.pack(fill="x", pady=(6, 0))

    lbl_flow = tk.Label(
        header_frame,
        text="TFTP  >  [=================>file>---------------]  >  Devices",
        bg=COLORS["bg"],
        fg=COLORS["fg"],
        font=FONT_MONO_B,
        justify="center",
        anchor="center",
    )
    lbl_flow.pack(pady=(2, 0))

    FLOW_SEGMENT = ">file>"
    FLOW_BAR_WIDTH = 38
    FLOW_MAX_POS = FLOW_BAR_WIDTH - len(FLOW_SEGMENT)
    flow_state = {"pos": 0}

    def _animate_flow():
        if btn_stop.cget("state") == "normal":
            pos = flow_state["pos"]
            bar = ("=" * pos) + FLOW_SEGMENT + ("-" * (FLOW_MAX_POS - pos))
            lbl_flow.config(text=f"TFTP  >  [{bar}]  >  Devices")

            flow_state["pos"] = (pos + 1) % (FLOW_MAX_POS + 1)

        root.after(400, _animate_flow)

    root.after(400, _animate_flow)

    # ==================================================================
    # ROW 1 — TFTP Server + File
    # ==================================================================
    row_top = tk.Frame(main_container)
    row_top.pack(fill="x", pady=(0, 5))
    row_top.columnconfigure(0, weight=1, uniform="half")
    row_top.columnconfigure(1, weight=1, uniform="half")

    # TFTP Server (left)
    frm_tftp = ttk.LabelFrame(row_top, text="TFTP Server", padding=10)
    frm_tftp.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

    ttk.Label(frm_tftp, text="TFTP Server IP Adddress:", style="Muted.TLabel").pack(anchor="w")
    entry_tftp = tk.Entry(frm_tftp)
    entry_tftp.pack(fill="x", pady=(2, 0))

    # File to Transfer (right)
    frm_file = ttk.LabelFrame(row_top, text="File to transfer", padding=10)
    frm_file.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

    ttk.Label(frm_file, text="Filename:", style="Muted.TLabel").pack(anchor="w")
    entry_ios = tk.Entry(frm_file)
    entry_ios.pack(fill="x", pady=(2, 0))

    # MD5 + Size
    row_md5_size = tk.Frame(frm_file)
    row_md5_size.pack(fill="x", pady=(5, 0))
    row_md5_size.columnconfigure(0, weight=3)
    row_md5_size.columnconfigure(1, weight=1)

    col_md5 = tk.Frame(row_md5_size)
    col_md5.grid(row=0, column=0, sticky="ew", padx=(0, 5))
    ttk.Label(col_md5, text="Hash MD5:", style="Muted.TLabel").pack(anchor="w")
    entry_md5 = tk.Entry(col_md5)
    entry_md5.pack(fill="x", pady=(2, 0))

    col_size = tk.Frame(row_md5_size)
    col_size.grid(row=0, column=1, sticky="ew", padx=(5, 0))
    ttk.Label(col_size, text="Size (MB):", style="Muted.TLabel").pack(anchor="w")

    entry_file_size = tk.Entry(col_size)
    entry_file_size.pack(fill="x", pady=(2, 0))
    ttk.Label(frm_file, text="* File MD5 Hash                                  * Estimated File size (in MB)", style="Hint.TLabel").pack(anchor="w")

    # ==================================================================
    # ROW 2 — Authentication + Advanced Config
    # ==================================================================
    row_mid = tk.Frame(main_container)
    row_mid.pack(fill="x", pady=5)
    row_mid.columnconfigure(0, weight=1, uniform="half")
    row_mid.columnconfigure(1, weight=1, uniform="half")

    # Authentication
    frm_auth = ttk.LabelFrame(row_mid, text="Device Authentication", padding=10)
    frm_auth.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

    ttk.Label(frm_auth, text="User:", style="Muted.TLabel").pack(anchor="w")
    entry_user = tk.Entry(frm_auth)
    entry_user.pack(fill="x", pady=2)

    ttk.Label(frm_auth, text="Pass:", style="Muted.TLabel").pack(anchor="w")
    entry_pass = tk.Entry(frm_auth, show="*")
    entry_pass.pack(fill="x", pady=2)

    enable_var = tk.BooleanVar()
    entry_enable_pass = tk.Entry(frm_auth, show="*", state="disabled")

    def toggle_enable():
        if enable_var.get():
            entry_enable_pass.config(state="normal")
        else:
            entry_enable_pass.delete(0, tk.END)
            entry_enable_pass.config(state="disabled")

    chk_enable = tk.Checkbutton(
        frm_auth, text="Use Enable Password?",
        variable=enable_var, command=toggle_enable,
    )
    chk_enable.pack(anchor="w", pady=(5, 0))

    ttk.Label(frm_auth, text="Enable Pass:", style="Muted.TLabel").pack(anchor="w")
    entry_enable_pass.pack(fill="x", pady=2)

    # Advanced Settings
    frm_adv = ttk.LabelFrame(row_mid, text="Advanced Config", padding=10)
    frm_adv.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

    ttk.Label(frm_adv, text="Module:", style="Muted.TLabel").pack(anchor="w")
    module_var = tk.StringVar(value="Cisco IOS")
    module_combo = ttk.Combobox(frm_adv, textvariable=module_var, state="readonly",
                                values=["Cisco IOS", "Cisco NX-OS"], font=FONT_MONO)
    module_combo.pack(fill="x", pady=2)

    ttk.Label(frm_adv, text="Max Workers (Threads):", style="Muted.TLabel").pack(anchor="w", pady=(10, 0))
    entry_workers = tk.Entry(frm_adv)
    entry_workers.insert(0, "5")
    entry_workers.pack(fill="x", pady=2)
    ttk.Label(frm_adv, text="* Simultaneous Transfers", style="Hint.TLabel").pack(anchor="w")

    ttk.Label(frm_adv, text="Transfer Timeout (min):", style="Muted.TLabel").pack(anchor="w", pady=(10, 0))
    entry_timeout = tk.Entry(frm_adv)
    entry_timeout.insert(0, "30")
    entry_timeout.pack(fill="x", pady=2)
    ttk.Label(frm_adv, text="*Max transfer time per device", style="Hint.TLabel").pack(anchor="w")

    def on_module_change(*_):
        if module_var.get() == "Cisco NX-OS":
            enable_var.set(False)
            chk_enable.config(state="disabled")
            entry_enable_pass.delete(0, tk.END)
            entry_enable_pass.config(state="disabled")
        else:
            chk_enable.config(state="normal")

    module_var.trace_add("write", on_module_change)

    # ==================================================================
    # ROW 3 — Target Devices
    # ==================================================================
    frm_dev = ttk.LabelFrame(main_container, text="Devices", padding=10)
    frm_dev.pack(fill="x", pady=5)

    ttk.Label(frm_dev, text="IP addresses (comma separated):", style="Muted.TLabel").pack(anchor="w")
    entry_ips = tk.Text(frm_dev, height=3)
    entry_ips.pack(fill="x", pady=(2, 0))
    ttk.Label(frm_dev, text="* e.g.: 192.168.1.1, 10.0.0.1, 172.16.0.1", style="Hint.TLabel").pack(anchor="w")

    # ==================================================================
    # ROW 4 - Start / Stop Buttons
    # ==================================================================
    btn_frame = tk.Frame(main_container)
    btn_frame.pack(pady=8)

    btn_start = tk.Button(
        btn_frame, text="▶ Start Transfer",
        bg=COLORS["btn_start"], fg="white", font=FONT_BOLD,
        width=22, relief="raised", borderwidth=2, cursor="hand2",
    )
    btn_start.pack(side="left", padx=5)

    btn_stop = tk.Button(
        btn_frame, text="⏹ Stop / Abort",
        bg=COLORS["btn_stop"], fg="white", font=FONT_BOLD,
        width=22, state="disabled", relief="raised", borderwidth=2, cursor="hand2",
    )
    btn_stop.pack(side="left", padx=5)

    # ==================================================================
    # ROW 5 — Output Log
    # ==================================================================
    frm_log = ttk.LabelFrame(main_container, text="Output Log", padding=5)
    frm_log.pack(fill="both", expand=True, pady=(5, 0))

    output_box = scrolledtext.ScrolledText(
        frm_log, bg=COLORS["console_bg"], fg=COLORS["console_fg"],
        font=FONT_MONO, relief="sunken", borderwidth=2,
    )
    output_box.tag_config("info",    foreground=COLORS["console_fg"],   font=FONT_MONO_B)
    output_box.tag_config("error",   foreground="#ff5555",            font=FONT_MONO_B)
    output_box.tag_config("success", foreground=COLORS["console_fg"],   font=FONT_MONO_B)
    output_box.tag_config("warning", foreground="#f1fa8c",            font=FONT_MONO_B)
    output_box.tag_config("device",  foreground="#2196f3",            font=FONT_MONO_B)
    output_box.pack(fill="both", expand=True)
    # Read-only but selectable/copyable: blocks typed edits without disabling
    # the widget (a disabled Text widget can't be selected with the mouse).
    output_box.bind("<Key>", lambda e: "break")
    output_box.configure(insertwidth=0)

    # ==================================================================
    # Field locking during transfer
    # ==================================================================
    def _set_inputs_state(locked):
        state = "disabled" if locked else "normal"
        entry_tftp.config(state=state)
        entry_ios.config(state=state)
        entry_md5.config(state=state)
        entry_file_size.config(state=state)
        entry_user.config(state=state)
        entry_pass.config(state=state)
        entry_workers.config(state=state)
        entry_timeout.config(state=state)
        entry_ips.config(state=state)
        chk_enable.config(state="disabled" if locked else "normal")
        module_combo.config(state="disabled" if locked else "readonly")
        entry_enable_pass.config(
            state="disabled" if locked else ("normal" if enable_var.get() else "disabled")
        )

    def lock_inputs():
        _set_inputs_state(True)

    def unlock_inputs():
        _set_inputs_state(False)

    # ==================================================================
    # Widget return
    # ==================================================================
    return {
        "root":                 root,
        "entry_tftp":           entry_tftp,
        "entry_ios":            entry_ios,
        "entry_md5":            entry_md5,
        "entry_file_size":      entry_file_size,
        "entry_user":           entry_user,
        "entry_pass":           entry_pass,
        "enable_var":           enable_var,
        "entry_enable_pass":    entry_enable_pass,
        "entry_workers":        entry_workers,
        "entry_timeout":        entry_timeout,
        "module_var":           module_var,
        "entry_ips":            entry_ips,
        "btn_start":            btn_start,
        "btn_stop":             btn_stop,
        "output_box":           output_box,
        "lock_inputs":          lock_inputs,
        "unlock_inputs":        unlock_inputs,
    }