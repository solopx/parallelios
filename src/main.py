import os
import threading
import tkinter as tk
from tkinter import messagebox

from gui import build_gui, COLORS
import ios_engine
import nxos_engine
from engine_core import (
    validate_ips,
    stop_event,
    active_connections,
)

def main():
    w = build_gui()

    root        = w["root"]
    output_box  = w["output_box"]
    btn_start   = w["btn_start"]
    btn_stop    = w["btn_stop"]

    def log_callback(display_id, msg, tag):
        def _insert():
            output_box.insert(tk.END, f"[{display_id}] {msg}\n", tag)
            if not output_box.tag_ranges("sel"):
                output_box.see(tk.END)
        root.after(0, _insert)

    def on_complete(success_count, total, details):
        def _update():
            summary_tag = "success" if success_count == total else "error"
            output_box.insert(tk.END, "\n--- Tasks Completed ---\n", "header")
            output_box.insert(
                tk.END,
                f"Sucess: {success_count} | Error: {total - success_count}\n",
                summary_tag,
            )

            copied = [d for d in details if d[1] == "copied"]
            skipped = [d for d in details if d[1] == "skipped"]
            failed = [d for d in details if d[1] == "failed"]

            if copied:
                output_box.insert(tk.END, "\nCopied & Verified:\n", "success")
                for display_id, _, _ in copied:
                    output_box.insert(tk.END, f"  [OK] {display_id}\n", "success")
            if skipped:
                output_box.insert(tk.END, "\nMD5 Match (Copy Skipped):\n", "success")
                for display_id, _, _ in skipped:
                    output_box.insert(tk.END, f"  [OK] {display_id}\n", "success")
            if failed:
                output_box.insert(tk.END, "\nFailed:\n", "error")
                for display_id, _, reason in failed:
                    output_box.insert(tk.END, f"  [X] {display_id} - {reason}\n", "error")

            if not output_box.tag_ranges("sel"):
                output_box.see(tk.END)
            btn_start.config(state="normal", bg=COLORS["btn_start"])
            btn_stop.config(state="disabled", bg=COLORS["btn_stop"])
            w["unlock_inputs"]()
        root.after(0, _update)

    def start_copy():
        tftp     = w["entry_tftp"].get().strip()
        file     = w["entry_ios"].get().strip()
        md5      = w["entry_md5"].get().strip()
        ips_raw  = w["entry_ips"].get("1.0", tk.END).strip()
        size_raw = w["entry_file_size"].get().strip()

        # Required field validation
        if not all([tftp, file, md5, ips_raw]):
            messagebox.showerror("Error", "Please fill all required fields!")
            return

        if not validate_ips(tftp, multiple=False):
            messagebox.showerror("IP Error", f"The TFTP Server IP '{tftp}' is invalid!")
            return

        raw_list, invalid_ips = validate_ips(ips_raw, multiple=True)

        if invalid_ips:
            error_msg = "The following device IPs are invalid:\n\n" + "\n".join(invalid_ips)
            messagebox.showerror("Invalid IPs", error_msg)
            return

        devices = list(dict.fromkeys(raw_list))

        if not devices:
            messagebox.showerror("Error", "No device IP addresses were provided!")
            return

        # File size: convert MB to bytes, or None if empty
        file_size = None
        if size_raw:
            try:
                mb = float(size_raw)
                if mb <= 0:
                    messagebox.showerror("Error", "File size must be greater than zero.")
                    return
                file_size = int(mb * 1024 * 1024)
            except ValueError:
                messagebox.showerror("Error", "Invalid file size. Please enter a value in MB.")
                return

        # Max Workers and Transfer Timeout: must be integers between 1 and 99
        try:
            max_workers = int(w["entry_workers"].get().strip())
            if not (1 <= max_workers <= 99):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Max Workers must be a whole number between 1 and 99.")
            return

        try:
            timeout_min = int(w["entry_timeout"].get().strip())
            if not (1 <= timeout_min <= 99):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Transfer Timeout must be a whole number between 1 and 99 minutes.")
            return

        btn_start.config(state="disabled", bg=COLORS["btn_start_disabled"])
        btn_stop.config(state="normal", bg=COLORS["btn_stop"])
        w["lock_inputs"]()
        output_box.delete("1.0", tk.END)
        module = w["module_var"].get()
        engine = nxos_engine if module == "Cisco NX-OS" else ios_engine

        threading.Thread(
            target=engine.transfer_and_verify_all,
            args=(
                tftp,
                file,
                md5,
                devices,
                w["entry_user"].get(),
                w["entry_pass"].get(),
                w["entry_enable_pass"].get() if w["enable_var"].get() else None,
                w["enable_var"].get(),
                file_size,
                log_callback,
                on_complete,
                max_workers,
                timeout_min * 60,
            ),
            daemon=True,
        ).start()

    def abort_transfer():
        stop_event.set()
        for ip in list(active_connections.keys()):
            try:
                active_connections[ip].remote_conn.close()
            except Exception:
                pass

    def stop_copy():
        if messagebox.askyesno("Confirm", "Abort the current operation?"):
            abort_transfer()
            btn_stop.config(state="disabled", bg=COLORS["btn_stop"])
            w["unlock_inputs"]()

    def on_closing():
        if btn_stop.cget("state") == "normal":
            if messagebox.askyesno(
                "Confirm Exit",
                "A transfer is currently in progress.\n"
                "Closing now will abort it. Are you sure you want to exit?",
            ):
                abort_transfer()
                os._exit(0)
        else:
            root.destroy()

    btn_start.config(command=start_copy)
    btn_stop.config(command=stop_copy)
    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()


if __name__ == "__main__":
    main()
