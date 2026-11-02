"""Accessible Tk desktop interface; generation runs off the UI thread."""

from __future__ import annotations

import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from . import __version__
from .settings import default_settings_path, load_folder, save_folder
from .core import Cancelled, FORMATS, MAX_COUNT, custom_space, export_numbers, format_number, nanp_space, prefix_space


class App(tk.Tk):
    def __init__(self, settings_path: Path | None = None) -> None:
        super().__init__()
        self.title("Phone Number Generator")
        width = min(840, self.winfo_screenwidth() - 60)
        height = min(880, self.winfo_screenheight() - 100)
        self.geometry(f"{width}x{height}")
        self.minsize(min(720, width), min(560, height))
        self.configure(bg="#f2f5fa")
        self.events: queue.Queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.busy = False
        self.last_file: Path | None = None
        self.settings_path = settings_path if settings_path is not None else default_settings_path()
        self.destination = tk.StringVar(value=load_folder(self.settings_path))
        self.mode = tk.StringVar(value="nanp")
        self.country = tk.StringVar(value="44")
        self.remaining = tk.StringVar(value="6")
        self.prefix_remaining = tk.StringVar(value="3")
        self.count = tk.StringVar(value="1000")
        self.output_format = tk.StringVar(value=FORMATS[0])
        self.status = tk.StringVar(value="Ready. Add your area codes to get started.")
        self.capacity = tk.StringVar(value="")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f2f5fa")
        style.configure("TLabel", background="#f2f5fa", foreground="#24334b", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 23, "bold"), foreground="#132640")
        style.configure("Step.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 7))
        style.configure("Primary.TButton", background="#245bdd", foreground="white")
        style.map("Primary.TButton", background=[("active", "#1744b3"), ("disabled", "#8b99ad")])
        style.configure("TRadiobutton", background="#f2f5fa", font=("Segoe UI", 10))
        style.configure("TEntry", padding=6)
        self._build()
        self.protocol("WM_DELETE_WINDOW", self.close)
        self._poll_after = self.after(100, self.poll)

    def _build(self) -> None:
        # A scrollable form keeps Save and status reachable on small/high-DPI screens.
        canvas = tk.Canvas(self, bg="#f2f5fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        body = ttk.Frame(canvas, padding=24)
        body_id = canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(body_id, width=e.width))
        def wheel(event):
            if not isinstance(event.widget, tk.Text):
                canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
        self.bind("<MouseWheel>", wheel)
        def reveal_focus(event):
            widget = event.widget
            if widget is self or not widget.winfo_ismapped():
                return
            self.update_idletasks()
            top = widget.winfo_rooty() - body.winfo_rooty()
            bottom = top + widget.winfo_height()
            visible_top = canvas.canvasy(0)
            visible_bottom = canvas.canvasy(canvas.winfo_height())
            total = max(body.winfo_height(), 1)
            if top < visible_top:
                canvas.yview_moveto(max(0, top - 12) / total)
            elif bottom > visible_bottom:
                canvas.yview_moveto((bottom - canvas.winfo_height() + 12) / total)
        self.bind("<FocusIn>", reveal_focus)
        body.columnconfigure(0, weight=1)
        ttk.Label(body, text="Phone Number Generator", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(body, text="Choose your ranges. Set a quantity. Save your list.").grid(row=1, column=0, sticky="w", pady=(3, 20))
        ttk.Label(body, text="1   Choose your number ranges", style="Step.TLabel").grid(row=2, column=0, sticky="w")
        modes = ttk.Frame(body)
        modes.grid(row=3, column=0, sticky="w", pady=10)
        ttk.Radiobutton(modes, text="North America (+1)", variable=self.mode, value="nanp", command=self.change_mode).pack(side="left", padx=(0, 24))
        ttk.Radiobutton(modes, text="Custom international", variable=self.mode, value="custom", command=self.change_mode).pack(side="left")
        ttk.Radiobutton(modes, text="Any starting digits", variable=self.mode, value="prefix", command=self.change_mode).pack(side="left", padx=(24, 0))
        self.hint = ttk.Label(body, text="Area codes, NPA-NXX pairs, or both. Separate with commas, spaces, or new lines.", wraplength=710)
        self.hint.grid(row=4, column=0, sticky="w")
        self.entries = tk.Text(body, height=4, wrap="word", font=("Consolas", 12), relief="solid", bd=1, padx=12, pady=10, undo=True)
        self.entries.grid(row=5, column=0, sticky="ew", pady=(8, 4))
        self.entries.bind("<Tab>", lambda e: (e.widget.tk_focusNext().focus_set(), "break")[-1])
        self.entries.bind("<Shift-Tab>", lambda e: (e.widget.tk_focusPrev().focus_set(), "break")[-1])
        self.example = ttk.Label(body, text="Example: 206, 425, 503-234, 503-235", wraplength=710)
        self.example.grid(row=6, column=0, sticky="w")
        self.custom_row = ttk.Frame(body)
        ttk.Label(self.custom_row, text="Country calling code").pack(side="left")
        ttk.Entry(self.custom_row, textvariable=self.country, width=6).pack(side="left", padx=(8, 24))
        ttk.Label(self.custom_row, text="Random digits after each prefix").pack(side="left")
        ttk.Entry(self.custom_row, textvariable=self.remaining, width=6).pack(side="left", padx=8)
        self.prefix_row = ttk.Frame(body)
        ttk.Label(self.prefix_row, text="How many digits remain?").pack(side="left")
        ttk.Entry(self.prefix_row, textvariable=self.prefix_remaining, width=6).pack(side="left", padx=8)
        ttk.Label(self.prefix_row, text="Random digits to add after each start").pack(side="left", padx=8)
        ttk.Label(body, text="2   Set your quantity and format", style="Step.TLabel").grid(row=8, column=0, sticky="w", pady=(20, 8))
        settings = ttk.Frame(body)
        settings.grid(row=9, column=0, sticky="ew")
        ttk.Label(settings, text="Total numbers").grid(row=0, column=0, sticky="w")
        ttk.Label(settings, text="Number format").grid(row=0, column=1, sticky="w", padx=20)
        ttk.Entry(settings, textvariable=self.count, width=17).grid(row=1, column=0, sticky="w", pady=5)
        self.format_box = ttk.Combobox(settings, textvariable=self.output_format, values=FORMATS, state="readonly", width=35)
        self.format_box.grid(row=1, column=1, padx=20, pady=5)
        ttk.Label(body, text="Quantity is shared across all ranges. Up to 1,000,000 unique numbers per file.").grid(row=10, column=0, sticky="w", pady=(2, 12))
        preview_row = ttk.Frame(body)
        preview_row.grid(row=11, column=0, sticky="ew")
        self.preview_button = ttk.Button(preview_row, text="Preview sample", command=self.preview)
        self.preview_button.pack(side="left")
        ttk.Label(preview_row, textvariable=self.capacity).pack(side="left", padx=12)
        self.sample_box = tk.Text(body, height=3, font=("Consolas", 11), bg="#e7edf7", fg="#24334b", relief="flat", padx=12, pady=8, state="disabled")
        self.sample_box.grid(row=12, column=0, sticky="ew", pady=(8, 14))
        ttk.Label(body, text="3   Save your list", style="Step.TLabel").grid(row=13, column=0, sticky="w")
        destination_row = ttk.Frame(body)
        destination_row.grid(row=14, column=0, sticky="ew", pady=(8, 0))
        destination_row.columnconfigure(1, weight=1)
        ttk.Label(destination_row, text="Save folder").grid(row=0, column=0, padx=(0, 8))
        destination_entry = ttk.Entry(destination_row, textvariable=self.destination)
        destination_entry.grid(row=0, column=1, sticky="ew")
        destination_entry.bind("<FocusOut>", lambda _: self.remember_destination())
        destination_entry.bind("<Return>", lambda _: self.remember_destination())
        ttk.Button(destination_row, text="Browse…", command=self.browse_destination).grid(row=0, column=2, padx=(8, 0))
        actions = ttk.Frame(body)
        actions.grid(row=15, column=0, sticky="ew", pady=10)
        self.save_button = ttk.Button(actions, text="Generate & save…", style="Primary.TButton", command=self.save)
        self.save_button.pack(side="left")
        self.cancel_button = ttk.Button(actions, text="Cancel", command=self.cancel, state="disabled")
        self.cancel_button.pack(side="left", padx=10)
        self.open_button = ttk.Button(actions, text="Open output folder", command=self.open_folder, state="disabled")
        self.open_button.pack(side="right")
        self.progress = ttk.Progressbar(body, mode="determinate")
        self.progress.grid(row=16, column=0, sticky="ew")
        ttk.Label(body, textvariable=self.status, wraplength=740).grid(row=17, column=0, sticky="w", pady=8)
        ttk.Label(body, text="Offline candidate generation only. Numbers may be unassigned or inactive.\nNo carrier or HLR lookup is performed. Duplicates are prevented within each export.", wraplength=740).grid(row=18, column=0, sticky="w", pady=(8, 0))
        ttk.Label(body, text=f"Version {__version__}  •  No account needed", font=("Segoe UI", 9)).grid(row=19, column=0, sticky="w", pady=(8, 0))

    def remember_destination(self) -> None:
        folder = self.destination.get().strip()
        if folder:
            try:
                save_folder(self.settings_path, folder)
            except OSError:
                self.status.set("Could not remember the save folder. Check your user settings folder permissions.")

    def browse_destination(self) -> None:
        current = Path(self.destination.get()).expanduser()
        folder = filedialog.askdirectory(parent=self, title="Choose save folder", initialdir=str(current if current.is_dir() else Path.home()))
        if folder:
            self.destination.set(folder)
            self.remember_destination()

    def change_mode(self) -> None:
        self.custom_row.grid_remove()
        self.prefix_row.grid_remove()
        if self.mode.get() == "custom":
            self.custom_row.grid(row=7, column=0, sticky="w", pady=(8, 0))
            self.hint.configure(text="Enter prefixes without the country code or domestic trunk zero.")
            self.example.configure(text="Example: country 44, prefixes 7700, 7701, remaining digits 6")
            self.format_box.configure(values=FORMATS[:2])
            if self.output_format.get() not in FORMATS[:2]:
                self.output_format.set(FORMATS[0])
        elif self.mode.get() == "prefix":
            self.prefix_row.grid(row=7, column=0, sticky="w", pady=(8, 0))
            self.hint.configure(text="Enter any starting digits. Hyphens are optional; separate starts with commas or new lines.")
            self.example.configure(text="Example: 12067745 with 3 remaining digits makes 12067745XXX. No country code is added.")
            self.format_box.configure(values=(FORMATS[1],))
            self.output_format.set(FORMATS[1])
        else:
            self.custom_row.grid_remove()
            self.hint.configure(text="Area codes, NPA-NXX pairs, or both. Separate with commas, spaces, or new lines.")
            self.example.configure(text="Example: 206, 425, 503-234, 503-235")
            self.format_box.configure(values=FORMATS)
        self.capacity.set("")
        self.set_sample("")

    def request(self):
        text = self.entries.get("1.0", "end").strip()
        if self.mode.get() == "nanp":
            space = nanp_space(text)
        else:
            try:
                remaining = int(self.prefix_remaining.get() if self.mode.get() == "prefix" else self.remaining.get())
            except ValueError:
                raise ValueError("Remaining digits must be a whole number.") from None
            space = prefix_space(text, remaining) if self.mode.get() == "prefix" else custom_space(self.country.get(), text, remaining)
        try:
            count = int(self.count.get().replace(",", ""))
        except ValueError:
            raise ValueError("Total numbers must be a whole number, such as 1000.") from None
        if not 1 <= count <= min(MAX_COUNT, space.capacity):
            raise ValueError(f"These ranges support 1 to {min(MAX_COUNT, space.capacity):,} numbers per export.")
        return space, count, self.output_format.get()

    def set_sample(self, text: str) -> None:
        self.sample_box.configure(state="normal")
        self.sample_box.delete("1.0", "end")
        self.sample_box.insert("1.0", text)
        self.sample_box.configure(state="disabled")

    def preview(self) -> None:
        try:
            space, count, style = self.request()
            values = [format_number(n, style, space.nanp) for n in space.sample(min(count, 6))]
            self.set_sample("   ".join(values[:3]) + ("\n" + "   ".join(values[3:]) if len(values) > 3 else ""))
            self.capacity.set(f"{space.capacity:,} possible combinations")
            self.status.set("Sample only. Your saved list will be newly generated.")
        except ValueError as error:
            self.set_sample("")
            self.capacity.set("")
            messagebox.showerror("Check your entries", str(error), parent=self)

    def save(self) -> None:
        try:
            space, count, style = self.request()
        except ValueError as error:
            messagebox.showerror("Check your entries", str(error), parent=self)
            return
        folder = Path(self.destination.get().strip()).expanduser()
        if not self.destination.get().strip() or not folder.is_dir():
            messagebox.showerror("Check save folder", "Choose an existing save folder using Browse, or enter a valid folder path.", parent=self)
            return
        self.remember_destination()
        filename = filedialog.asksaveasfilename(parent=self, title="Save your phone number list", initialdir=str(folder), initialfile="phone_numbers.txt", defaultextension=".txt", filetypes=[("Text file (one number per line)", "*.txt"), ("CSV file (phone_number column)", "*.csv")], confirmoverwrite=False)
        if not filename:
            return
        path = Path(filename)
        self.destination.set(str(path.parent))
        self.remember_destination()
        overwrite = path.exists()
        if overwrite and not messagebox.askyesno("Replace existing file?", f"Replace {path.name}?\nIts current contents will be replaced only after generation succeeds.", parent=self):
            return
        self.busy = True
        self.cancel_event.clear()
        self.progress.configure(maximum=count, value=0)
        self.save_button.configure(state="disabled")
        self.preview_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.open_button.configure(state="disabled")
        self.status.set(f"Generating {count:,} numbers…")
        # Snapshot all settings before starting; worker never accesses Tk.
        def work():
            try:
                export_numbers(space, count, path, style, overwrite=overwrite, cancel=self.cancel_event, progress=lambda done: self.events.put(("progress", done)))
                self.events.put(("success", (path, count)))
            except Cancelled:
                self.events.put(("cancelled", None))
            except Exception as error:
                self.events.put(("error", str(error)))
        threading.Thread(target=work, daemon=True).start()

    def cancel(self) -> None:
        self.cancel_event.set()
        self.cancel_button.configure(state="disabled")
        self.status.set("Cancelling…")

    def poll(self) -> None:
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "progress":
                    self.progress.configure(value=value)
                    self.status.set(f"Generated {value:,} numbers…")
                    continue
                self.busy = False
                self.save_button.configure(state="normal")
                self.preview_button.configure(state="normal")
                self.cancel_button.configure(state="disabled")
                if kind == "success":
                    self.last_file, count = value
                    self.status.set(f"Saved {count:,} unique numbers to {self.last_file.name}.")
                elif kind == "cancelled":
                    self.progress.configure(value=0)
                    self.status.set("Cancelled. No output file was changed.")
                else:
                    self.progress.configure(value=0)
                    self.status.set("Could not save your list. Check the message and try again.")
                    messagebox.showerror("Unable to save", value, parent=self)
                if self.last_file:
                    self.open_button.configure(state="normal")
        except queue.Empty:
            pass
        self._poll_after = self.after(100, self.poll)

    def destroy(self) -> None:
        if getattr(self, "_poll_after", None) is not None:
            self.after_cancel(self._poll_after)
            self._poll_after = None
        super().destroy()

    def open_folder(self) -> None:
        if self.last_file:
            try:
                if os.name == "nt":
                    os.startfile(self.last_file.parent)
                else:
                    import webbrowser
                    webbrowser.open(self.last_file.parent.as_uri())
            except OSError as error:
                messagebox.showerror("Unable to open folder", str(error), parent=self)

    def close(self) -> None:
        if self.busy:
            messagebox.showinfo("Export in progress", "Cancel the export or let it finish before closing.", parent=self)
        else:
            self.remember_destination()
            self.destroy()


def main() -> None:
    import sys
    if len(sys.argv) == 3 and sys.argv[1] == "--self-test":
        from .diagnostics import run_checks
        raise SystemExit(run_checks(Path(sys.argv[2])))
    App().mainloop()
