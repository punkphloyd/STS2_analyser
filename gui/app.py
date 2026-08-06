import customtkinter as ctk
from tkinter import filedialog, ttk
from discovery.run_discovery import discover_runs
from gui import filter_frame
from parsers.metadata_parser import parse_metadata
from data_models.run_metadata import RunMetadata
from typing import cast
from filters.filters import RunFilter
from filters.run_filters import apply_filters

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Slay the Spire 2 - Run Analyser")
        self.geometry("1280x720")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.directory = ctk.StringVar()
        self.status = ctk.StringVar(value="Ready")

        self.results = None
        self.run_metadata: list[RunMetadata] = []

        self.details_frame = None

        self.date_label = None
        self.character_label = None
        self.ascension_label = None
        self.result_label = None

        # Current filter storage
        self.current_filter = RunFilter()

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

        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(
            row=3,
            column=0,
            padx=20,
            pady=(0,10),
            sticky="ew"
        )

        character_label = ctk.CTkLabel(
            filter_frame,
            text="Character: -",
            font=("Segoe UI", 16, "bold")
        )
        character_label.pack(side="left", padx=(10,5))

        self.character_filter = ctk.StringVar(value="All")

        character_combo = ctk.CTkComboBox(
            filter_frame,
            values=[
                "All",
                "Ironclad",
                "Silent",
                "Regent",
                "Necrobinder",
                "Defect"
            ],
            variable=self.character_filter,
            command=self.on_character_filter_changed,
            width=160
        )

        character_combo.pack(side="left", padx=(0,20))



        content_frame = ctk.CTkFrame(self)
        content_frame.grid(
            row=4,
            column=0,
            padx=20,
            pady=10,
            sticky="nsew"
        )

        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=3)

        results_frame = ctk.CTkFrame(content_frame)
        results_frame.grid(
            row=0,
            column=0,
            padx=(0,10),
            sticky="nsew"
        )

        self.details_frame = ctk.CTkFrame(content_frame)
        self.details_frame.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        details_label = ctk.CTkLabel(
        self.details_frame,
        text="Run Details",
        font=("Segoe UI", 16, "bold")
        )

        results_frame.grid_rowconfigure(1, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        self.details_frame.grid_rowconfigure(1, weight=1)
        self.details_frame.grid_columnconfigure(0, weight=1)

        details_label.pack(
            anchor="w",
            padx=10,
            pady=(10, 0)
        )

        self.date_label = ctk.CTkLabel(
            self.details_frame,
            text="Date: -"
        )
        self.date_label.pack(anchor="w", padx=10)

        self.character_label = ctk.CTkLabel(
            self.details_frame,
            text="Character: -"
        )
        self.character_label.pack(anchor="w", padx=10)

        self.ascension_label = ctk.CTkLabel(
            self.details_frame,
            text="Ascension: -"
        )
        self.ascension_label.pack(anchor="w", padx=10)

        self.result_label = ctk.CTkLabel(
            self.details_frame,
            text="Result: -"
        )
        self.result_label.pack(anchor="w", padx=10)

        results_label = ctk.CTkLabel(
            results_frame,
            text="Runs",
            font=("Segoe UI", 16, "bold")
        )
        results_label.pack(anchor="w", padx=10, pady=(10, 0))

        table_frame = ctk.CTkFrame(results_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.results = ttk.Treeview(
            table_frame,
            columns=("date", "character", "ascension", "result"),
            show="headings"
        )

        self.results.bind(
            "<<TreeviewSelect>>",
            self.on_run_selected
        )

        self.results.heading("date", text="Date")
        self.results.heading("character", text="Character")
        self.results.heading("ascension", text="Ascension")
        self.results.heading("result", text="Result")

        self.results.column("date", width=150)
        self.results.column("character", width=150)
        self.results.column("ascension", width=100, anchor="center")
        self.results.column("result", width=100, anchor="center")


        # Add scroll bar to results table section
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.results.yview
        )

        self.results.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")

        self.results.pack(
            side="left",
            fill="both",
            expand=True
        )

        status_label = ctk.CTkLabel(
            self,
            textvariable=self.status
        )

        status_label.grid(
            row=5,
            column=0,
            pady=10
        )


    def browse_directory(self):

        folder = filedialog.askdirectory()

        if folder:
            self.directory.set(folder)

    def load_runs(self):

        if not self.directory.get():
            for row in self.results.get_children():
                self.results.delete(row)

            self.status.set("Please select a run directory first.")
            return

        run_files = discover_runs(self.directory.get())
        parsed_metadata: list[RunMetadata] = [
            parse_metadata(run)
            for run in run_files
        ]
        parsed_metadata.sort(
            key=lambda m: m.start_time,
            reverse=True
        )

        self.run_metadata = parsed_metadata
        self.refresh_run_table()

    # Function to refresh run table when changing/updating filters
    def refresh_run_table(self):

        filtered_runs = apply_filters(
            self.run_metadata,
            self.current_filter
        )

        for row in self.results.get_children():
            self.results.delete(row)

        for run in filtered_runs:

            result = "Win" if run.victory else "Loss"

            self.results.insert(
                "",
                "end",
                values=(
                    run.start_time.strftime("%Y-%m-%d"),
                    run.character,
                    run.ascension,
                    result
                )
            )

        self.status.set(f"Showing {len(filtered_runs)} runs.")

    def on_run_selected(self, _event):

        selected = self.results.selection()

        if not selected:
            return

        index = cast(int, self.results.index(selected[0]))

        selected_run = self.run_metadata[index]

        self.date_label.configure(
            text=f"Date: {selected_run.start_time:%Y-%m-%d}"
        )

        self.character_label.configure(
            text=f"Character: {selected_run.character}"
        )

        self.ascension_label.configure(
            text=f"Ascension: {selected_run.ascension}"
        )

        self.result_label.configure(
            text=f"Result: {'Victory' if selected_run.victory else 'Defeat'}"
        )

    def on_character_filter_changed(self, value: str):

        if value == "All":
            self.current_filter.characters = None
        else:
            self.current_filter.characters = {value}

        self.refresh_run_table()

    def clear_filters(self):

        self.character_filter.set("All")

        self.current_filter = RunFilter()

        self.refresh_run_table()