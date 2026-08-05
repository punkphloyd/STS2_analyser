import customtkinter as ctk
from tkinter import filedialog
from discovery.run_discovery import discover_runs


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Slay the Spire 2 - Run Analyser")
        self.geometry("1280x720")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.directory = ctk.StringVar()
        self.status = ctk.StringVar(value="Ready")

        self.results = None

        self.build_ui()

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="Slay the Spire 2 - Run Analyser",
            font=("Segoe UI", 22, "bold")
        )
        title.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 15)
        )

        directory_frame = ctk.CTkFrame(self)
        directory_frame.grid_columnconfigure(0, weight=1)
        directory_frame.grid(
            row=1,
            column=0,
            padx=20,
            pady=10,
            sticky="ew"
        )

        directory_label = ctk.CTkLabel(directory_frame, text="Run directory")
        directory_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=15,
            pady=(15, 5)
        )

        directory_entry = ctk.CTkEntry(
            directory_frame,
            textvariable=self.directory
        )
        directory_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(15, 10),
            pady=(0, 15)
        )

        browse_button = ctk.CTkButton(
            directory_frame,
            text="Browse...",
            command=self.browse_directory,
            width=120
        )
        browse_button.grid(
            row=1,
            column=1,
            padx=(0, 15),
            pady=(0, 15)
        )

        load_button = ctk.CTkButton(
            self,
            text="Load Runs",
            command=self.load_runs
        )
        load_button.grid(
            row=2,
            column=0,
            padx=20,
            pady=15,
            sticky="se"
        )

        results_frame = ctk.CTkFrame(self)
        results_frame.grid(
            row=3,
            column=0,
            padx=20,
            pady=10,
            sticky="nsew"
        )

        results_label = ctk.CTkLabel(
            results_frame,
            text="Runs",
            font=("Segoe UI", 16, "bold")
        )
        results_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.results = ctk.CTkTextbox(results_frame, wrap="none")
        self.results.pack(fill="both", expand=True, padx=10, pady=10)
        self.results.configure(state="disabled")

        status_label = ctk.CTkLabel(
            self,
            textvariable=self.status
        )

        status_label.grid(
            row=4,
            column=0,
            pady=10
        )


    def browse_directory(self):

        folder = filedialog.askdirectory()

        if folder:
            self.directory.set(folder)

    def load_runs(self):

        if not self.directory.get():
            self.results.configure(state="normal")
            self.results.delete("1.0", "end")
            self.results.configure(state="disabled")

            self.status.set("Please select a run directory first.")
            return

        run_files = discover_runs(self.directory.get())

        self.results.configure(state="normal")

        self.results.delete("1.0", "end")

        for run in run_files:
            self.results.insert("end", f"{run.name}\n")

        self.results.configure(state="disabled")

        self.status.set(f"Found {len(run_files)} run files.")
