import customtkinter as ctk
from tkinter import filedialog
from discovery.run_discovery import discover_runs


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Slay the Spire 2 - Run Analyser")
        self.geometry("800x600")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.directory = ctk.StringVar()
        self.status = ctk.StringVar(value="Ready")

        self.build_ui()

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="Slay the Spire 2 - Run Analyser",
            font=("Segoe UI", 22, "bold")
        )
        title.pack(pady=(20,25))

        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=20)

        label = ctk.CTkLabel(frame, text="Run directory")
        label.pack(anchor="w", padx=15, pady=(15,5))

        entry = ctk.CTkEntry(
            frame,
            textvariable=self.directory
        )
        entry.pack(side="left", expand=True, padx=(15,10), pady=(0, 15))

        browse = ctk.CTkButton(
            frame,
            text="Browse...",
            command=self.browse_directory,
            width=120
        )
        browse.pack(side="right", padx=(0, 15), pady=(0, 15))

        load = ctk.CTkButton(
            self,
            text="Load Runs",
            command=self.load_runs
        )
        load.pack(pady=20)

        status = ctk.CTkLabel(
            self,
            textvariable=self.status
        )
        status.pack(pady=(0, 20))

    def browse_directory(self):

        folder = filedialog.askdirectory()

        if folder:
            self.directory.set(folder)

    def load_runs(self):

        run_files = discover_runs(self.directory.get())

        self.status.set(f"Found {len(run_files)} run files.")
