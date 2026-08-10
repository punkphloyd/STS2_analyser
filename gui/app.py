import customtkinter as ctk
from gui.details_frame import DetailsFrame
from datetime import datetime, timedelta, date
from tkinter import filedialog, ttk

from data_models.run_metadata import RunMetadata
from filters.filters import RunFilter
from filters.run_filters import apply_filters
from gui.filter_frame import FilterFrame
from gui.results_frame import ResultsFrame
from services.run_loader import load_run_metadata
from gui.directory_frame import DirectoryFrame

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

        self.run_metadata: list[RunMetadata] = []

        # Frames definition

        self.results_frame = None
        self.details_frame = None
        self.filter_frame = None

        # Current filter storage
        self.current_filter = RunFilter()
        self.build_ui()

    def build_ui(self):

        # ============================================================
        # 1. Title
        # ============================================================

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

        # ============================================================
        # 2. Directory selection
        # ============================================================

        self.directory_frame = DirectoryFrame(
            self,
            directory=self.directory,
            on_browse=self.browse_directory
        )

        self.directory_frame.grid(
            row=1,
            column=0,
            padx=20,
            pady=10,
            sticky="ew"
        )

        # ============================================================
        # 3. Load button
        # ============================================================

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

        # ============================================================
        # 4. Filter frame
        # ============================================================

        self.filter_frame = FilterFrame(
            self,
                on_character_changed=self.on_character_filter_changed,
                on_result_changed=self.on_result_filter_changed,
                on_min_ascension_changed=self.on_min_ascension_changed,
                on_max_ascension_changed=self.on_max_ascension_changed,
                on_date_changed=self.on_date_filter_changed,
                on_clear_filters=self.clear_filters,
                on_custom_dates_applied=self.on_custom_dates_applied
        )

        self.filter_frame.grid(
            row=3,
            column=0,
            padx=20,
            pady=10,
            sticky="ew"
        )

        # ============================================================
        # 6. Main content
        # ============================================================

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

        # ------------------------------------------------------------
        # 6a. Results frame
        # ------------------------------------------------------------

        self.results_frame = ResultsFrame(
            content_frame,
            on_run_selected=self.on_run_selected
        )

        self.results_frame.grid(
            row=0,
            column=0,
            padx=(0, 10),
            sticky="nsew"
        )

        # ------------------------------------------------------------
        # 6b. Details frame
        # ------------------------------------------------------------

        self.details_frame = DetailsFrame(
            content_frame
        )

        self.details_frame.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        # ============================================================
        # 7. Status
        # ============================================================

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

        self.results_frame.set_runs(filtered_runs)

        self.status.set(
            f"Found {len(filtered_runs)} runs."
        )

    def on_run_selected(self, _event):

        selected_run = self.results_frame.get_selected_run()

        if selected_run is None:
            return

        self.details_frame.show_run(selected_run)

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

        now = datetime.now().date()

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
            self.filter_frame.show_custom_dates()
            return

        self.filter_frame.hide_custom_dates()

        self.refresh_run_table()

    def on_custom_dates_applied(
            self,
            start_date: date,
            end_date: date
    ):

        if start_date > end_date:
            self.status.set(
                "Start date cannot be after end date"
            )
            return

        self.current_filter.date_mode = "Custom"
        self.current_filter.start_date = start_date
        self.current_filter.end_date = end_date

        self.refresh_run_table()

    def clear_filters(self):

        self.filter_frame.character_combo.set("All")
        self.filter_frame.result_combo.set("All")
        self.filter_frame.min_ascension_combo.set("0")
        self.filter_frame.max_ascension_combo.set("10")
        self.filter_frame.date_combo.set("All")

        self.filter_frame.from_date_entry.delete(0, "end")
        self.filter_frame.to_date_entry.delete(0, "end")

        self.filter_frame.hide_custom_dates()

        self.current_filter = RunFilter()

        self.refresh_run_table()