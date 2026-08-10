from idlelib.query import CustomRun

import customtkinter as ctk
from tkinter import filedialog, ttk
from gui import filter_frame
from data_models.run_metadata import RunMetadata
from filters.filters import RunFilter
from filters.run_filters import apply_filters
from services.run_loader import load_run_metadata
from datetime import datetime, timedelta, time


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Slay the Spire 2 - Run Analyser")
        self.geometry("1280x720")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.directory = ctk.StringVar()
        self.status = ctk.StringVar(value="Ready")

        self.results = None
        self.run_metadata: list[RunMetadata] = []
        self.run_lookup: dict[str, RunMetadata] = {}

        self.details_frame = None

        self.date_label = None
        self.character_label = None
        self.ascension_label = None
        self.result_label = None

        # Current filter storage
        self.current_filter = RunFilter()
        self.custom_date_frame = None
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

        result_label = ctk.CTkLabel(
            filter_frame,
            text="Result: -",
            font=("Segoe UI", 16, "bold")
        )
        result_label.pack(side="left", padx=(0, 5))
        self.result_filter = ctk.StringVar(value="All")

        result_combo = ctk.CTkComboBox(
            filter_frame,
            values=["All", "Wins", "Losses"],
            variable=self.result_filter,
            command=self.on_result_filter_changed,
            width=120
        )

        result_combo.pack(side="left", padx=(0, 20))

        # Ascension labels and comboboxes
        ascension_label = ctk.CTkLabel(
            filter_frame,
            text="Ascension"
        )
        ascension_label.pack(side="left", padx=(0, 5))

        self.min_ascension_filter = ctk.StringVar(value="0")

        min_ascension_combo = ctk.CTkComboBox(
            filter_frame,
            values=[str(i) for i in range(11)],
            variable=self.min_ascension_filter,
            command=self.on_min_ascension_changed,
            width=70
        )

        min_ascension_combo.pack(side="left", padx=(0, 5))

        to_label = ctk.CTkLabel(
            filter_frame,
            text="to"
        )
        to_label.pack(side="left", padx=(0, 5))

        self.max_ascension_filter = ctk.StringVar(value="10")

        max_ascension_combo = ctk.CTkComboBox(
            filter_frame,
            values=[str(i) for i in range(11)],
            variable=self.max_ascension_filter,
            command=self.on_max_ascension_changed,
            width=70
        )

        max_ascension_combo.pack(side="left", padx=(0, 20))

        date_label = ctk.CTkLabel(
            filter_frame,
            text="Date"
        )

        date_label.pack(
            side="left",
            padx=(0, 5)
        )

        self.date_filter = ctk.StringVar(value="All")

        date_combo = ctk.CTkComboBox(
            filter_frame,
            values=[
                "All",
                "Last 7 days",
                "Last 30 days",
                "Last 90 days",
                "Last 365 days",
                "Custom..."
            ],
            variable=self.date_filter,
            command=self.on_date_filter_changed,
            width=150
        )

        date_combo.pack(
            side="left",
            padx=(0, 20)
        )




        content_frame = ctk.CTkFrame(self)
        content_frame.grid(
            row=5,
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

        clear_filters_button = ctk.CTkButton(
            filter_frame,
            text="Clear Filters",
            command=self.clear_filters,
            width=100
        )

        clear_filters_button.pack(
            side="left",
            padx=(10, 0)
        )

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

        self.custom_date_frame = ctk.CTkFrame(self)
        from_label = ctk.CTkLabel(
            self.custom_date_frame,
            text="From"
        )
        from_label.pack(
            side="left",
            padx=(10, 5)
        )

        self.from_date_entry = ctk.CTkEntry(
            self.custom_date_frame,
            width=120,
            placeholder_text="DD/MM/YYYY"
        )
        self.from_date_entry.pack(
            side="left",
            padx=(0, 20)
        )

        to_label = ctk.CTkLabel(
            self.custom_date_frame,
            text="To"
        )
        to_label.pack(
            side="left",
            padx=(0, 5)
        )

        self.to_date_entry = ctk.CTkEntry(
            self.custom_date_frame,
            width=120,
            placeholder_text="DD/MM/YYYY"
        )
        self.to_date_entry.pack(
            side="left",
            padx=(0, 20)
        )

        apply_button = ctk.CTkButton(
            self.custom_date_frame,
            text="Apply",
            command=self.apply_custom_dates,
            width=80
        )
        apply_button.pack(
            side="left",
            padx=(0,10)
        )

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
            row=6,
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

        self.run_metadata = load_run_metadata(
            self.directory.get()
        )

        self.refresh_run_table()

        self.status.set(
            f"Found {len(self.run_metadata)} runs."
        )


    # Function to refresh run table when changing/updating filters
    def refresh_run_table(self):

        filtered_runs = apply_filters(
            self.run_metadata,
            self.current_filter
        )

        # Clear lookup before rebuilding table
        for row in self.results.get_children():
            self.results.delete(row)

        self.run_lookup.clear()

        for run in filtered_runs:

            result = "Win" if run.victory else "Loss"

            item_id = self.results.insert(
                "",
                "end",
                values=(
                    run.start_time.strftime("%Y-%m-%d"),
                    run.character,
                    run.ascension,
                    result
                )
            )

            self.run_lookup[item_id] = run

        self.status.set(f"Showing {len(filtered_runs)} runs.")

    def on_run_selected(self, _event):

        selected = self.results.selection()

        if not selected:
            return

        selected_run = self.run_lookup[selected[0]]

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


    def on_result_filter_changed(self, value: str):

        if value == "All":
            self.current_filter.victory = None

        elif value == "Wins":
            self.current_filter.victory = True

        elif value == "Losses":
            self.current_filter.victory = False

        self.refresh_run_table()

    def on_min_ascension_changed(self, value: str):

        self.current_filter.min_ascension = int(value)

        self.refresh_run_table()


    def on_max_ascension_changed(self, value: str):

        self.current_filter.max_ascension = int(value)

        self.refresh_run_table()

    def on_date_filter_changed(self, value: str):

        now = datetime.now()

        self.current_filter.date_mode = value
        self.current_filter.start_date = None
        self.current_filter.end_date = None

        if value == "Last 7 days":
            self.current_filter.start_date = now - timedelta(days=7)

        elif value == "Last 30 days":
            self.current_filter.start_date = now - timedelta(days=30)

        elif value == "Last 90 days":
            self.current_filter.start_date = now - timedelta(days=90)

        elif value == "Last 365 days":
            self.current_filter.start_date = now - timedelta(days=365)

        elif value == "Custom...":
            self.custom_date_frame.grid(
                row=4,
                column=0,
                padx=20,
                pady=(0, 10),
                sticky="ew"
            )
            return

        self.custom_date_frame.grid_remove()

        self.refresh_run_table()

    def apply_custom_dates(self):
        from_text = self.from_date_entry.get().strip()
        to_text = self.to_date_entry.get().strip()

        try:
            start_date = (
                datetime.strptime(from_text, "%d/%m/%Y")
                if from_text
                else None
            )

            end_date = (
                datetime.strptime(to_text, "%d/%m/%Y")
                if to_text
                else None
            )

            # Force end date recorded time to be 23:59:59
            if end_date is not None:
                end_date = end_date.replace(
                    hour=23,
                    minute=59,
                    second=59,
                    microsecond=999999
                )

        except ValueError:
            self.status.set("Invalid date format. Please use DD/MM/YYYY.")
            return

        if start_date and end_date and start_date > end_date:
            self.status.set("Start date cannot be after end date")
            return

        self.current_filter.date_mode = "Custom"
        self.current_filter.start_date = start_date
        self.current_filter.end_date = end_date

        self.refresh_run_table()

    def clear_filters(self):

        self.character_filter.set("All")
        self.result_filter.set("All")
        self.min_ascension_filter.set("0")
        self.max_ascension_filter.set("10")
        self.date_filter.set("All")

        self.from_date_entry.delete(0, "end")
        self.to_date_entry.delete(0, "end")

        self.custom_date_frame.grid_remove()

        self.current_filter = RunFilter()

        self.refresh_run_table()