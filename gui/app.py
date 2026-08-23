import customtkinter as ctk
from gui.details_frame import DetailsFrame
from datetime import datetime, timedelta, date
from tkinter import filedialog

from data_models.run_metadata import RunMetadata
from filters.filters import RunFilter
from filters.run_filters import apply_filters
from gui.filter_frame import FilterFrame
from gui.results_frame import ResultsFrame
from services.run_loader import (
    load_run_data,
    load_run_metadata,
)

from gui.directory_frame import DirectoryFrame
from gui.quick_plots_frame import QuickPlotsFrame
from gui.plot_window import PlotWindow
from gui.analysis_window import AnalysisWindow
from gui.death_analysis_window import DeathAnalysisWindow
from gui.combat_analysis_window import CombatAnalysisWindow
from gui.relic_analysis_window import RelicAnalysisWindow


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Slay the Spire 2 - Run Analyser")
        self.geometry("1600x900")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.directory = ctk.StringVar()
        self.status = ctk.StringVar(value="Ready")

        self.run_metadata: list[RunMetadata] = []
        self.filtered_runs = []

        # Sub window declarations
        self.plot_window = None
        self.analysis_window = None
        self.death_analysis_window = None
        self.combat_analysis_window = None
        self.relic_analysis_window = None

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
            on_custom_dates_applied=self.on_custom_dates_applied,
            on_exclude_daily_changed=self.on_exclude_daily_changed,
            on_exclude_custom_changed=self.on_exclude_custom_changed,
            on_game_version_changed=self.on_game_version_changed,
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
        # 7. Quick plots frame
        # ============================================================

        self.quick_plots_frame = QuickPlotsFrame(
            self,
            on_plot=self.on_quick_plot
        )

        self.quick_plots_frame.grid(
            row=6,
            column=0,
            padx=20,
            pady=(10, 5),
            sticky="ew"
        )

        # ============================================================
        # 8. Analysis
        # ============================================================

        analysis_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        analysis_frame.grid(
            row=7,
            column=0,
            padx=20,
            pady=(5, 10),
            sticky="ew"
        )

        analysis_frame.grid_columnconfigure(
            0,
            weight=1
        )

        analysis_frame.grid_columnconfigure(
            1,
            weight=1
        )

        analysis_frame.grid_columnconfigure(
            2,
            weight=1
        )

        analysis_frame.grid_columnconfigure(
            3,
            weight=1
        )

        neow_analysis_button = ctk.CTkButton(
            analysis_frame,
            text="Neow's Bonus Relic Analysis",
            command=self.open_neow_analysis
        )

        neow_analysis_button.grid(
            row=0,
            column=0,
            padx=(0, 5),
            sticky="ew"
        )

        death_analysis_button = ctk.CTkButton(
            analysis_frame,
            text="Death Analysis",
            command=self.open_death_analysis
        )

        death_analysis_button.grid(
            row=0,
            column=1,
            padx=5,
            sticky="ew"
        )

        combat_analysis_button = ctk.CTkButton(
            analysis_frame,
            text="Combat Analysis",
            command=self.open_combat_analysis
        )

        combat_analysis_button.grid(
            row=0,
            column=2,
            padx=5,
            sticky="ew"
        )

        relic_analysis_button = ctk.CTkButton(
            analysis_frame,
            text="Relic Analysis",
            command=self.open_relic_analysis
        )

        relic_analysis_button.grid(
            row=0,
            column=3,
            padx=(5, 0),
            sticky="ew"
        )

        # ============================================================
        # 9. Status
        # ============================================================

        status_label = ctk.CTkLabel(
            self,
            textvariable=self.status
        )

        status_label.grid(
            row=8,
            column=0,
            pady=10
        )

    def browse_directory(self):

        folder = filedialog.askdirectory()

        if folder:
            self.directory.set(folder)

    def load_runs(self):

        if not self.directory.get():
            self.status.set(
                "Please select a run directory first."
            )
            return

        self.run_metadata = load_run_metadata(
            self.directory.get()
        )

        versions = self.sort_game_versions({
            run.game_version
            for run in self.run_metadata
        })

        self.filter_frame.set_game_versions(
            versions
        )

        self.current_filter = RunFilter()
        self.refresh_run_table()

    # Function to refresh run table when changing/updating filters
    def refresh_run_table(self):

        self.filtered_runs = apply_filters(
            self.run_metadata,
            self.current_filter
        )

        self.results_frame.set_runs(
            self.filtered_runs
        )

        if self.plot_window is not None:
            self.plot_window.update_runs(
                self.filtered_runs
            )

        self.update_analysis_windows(
            self.filtered_runs
        )

        self.status.set(
            f"Found {len(self.filtered_runs)} runs."
        )

    def on_run_selected(self, _event):

        selected_run = (
            self.results_frame.get_selected_run()
        )

        if selected_run is None:
            return

        self.details_frame.show_run(
            selected_run
        )

    def on_character_filter_changed(
        self,
        value: str
    ):

        if value == "All":
            self.current_filter.characters = None
        else:
            self.current_filter.characters = {
                value
            }

        self.refresh_run_table()

    def on_result_filter_changed(
        self,
        value: str
    ):

        if value == "All":
            self.current_filter.victory = None

        elif value == "Wins":
            self.current_filter.victory = True

        elif value == "Losses":
            self.current_filter.victory = False

        self.refresh_run_table()

    def on_min_ascension_changed(
        self,
        value: str
    ):

        self.current_filter.min_ascension = int(
            value
        )

        self.refresh_run_table()

    def on_max_ascension_changed(
        self,
        value: str
    ):

        self.current_filter.max_ascension = int(
            value
        )

        self.refresh_run_table()

    def on_date_filter_changed(
        self,
        value: str
    ):

        now = datetime.now().date()

        self.current_filter.start_date = None
        self.current_filter.end_date = None

        if value == "Last 7 days":
            self.current_filter.start_date = (
                now - timedelta(days=7)
            )

        elif value == "Last 30 days":
            self.current_filter.start_date = (
                now - timedelta(days=30)
            )

        elif value == "Last 90 days":
            self.current_filter.start_date = (
                now - timedelta(days=90)
            )

        elif value == "Last 365 days":
            self.current_filter.start_date = (
                now - timedelta(days=365)
            )

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

        self.current_filter.start_date = start_date
        self.current_filter.end_date = end_date

        self.refresh_run_table()

    def on_quick_plot(self):

        selected_plot = (
            self.quick_plots_frame.plot_combo.get()
        )

        if not self.filtered_runs:
            self.status.set(
                "No runs available for plotting."
            )
            return

        if selected_plot == "Win Rate":

            self.plot_window = PlotWindow(
                self,
                self.filtered_runs,
                title="Win Rate"
            )

        elif selected_plot == "Win Rate Over Time":

            self.plot_window = PlotWindow(
                self,
                self.filtered_runs,
                title="Win Rate Over Time",
                plot_type="Win Rate Over Time"
            )

    # Open Neow relic analysis window
    def open_neow_analysis(self):

        if not self.filtered_runs:
            self.status.set(
                "No runs available for analysis."
            )
            return

        run_data = load_run_data(
            self.filtered_runs
        )

        if self.analysis_window is not None:
            try:
                if self.analysis_window.winfo_exists():
                    self.analysis_window.destroy()
            except Exception:
                pass

        self.analysis_window = AnalysisWindow(
            self,
            run_data,
        )

    def on_exclude_daily_changed(self):

        self.current_filter.exclude_daily = (
            self.filter_frame.exclude_daily_checkbox.get()
        )

        self.refresh_run_table()

    def on_exclude_custom_changed(self):

        self.current_filter.exclude_custom = (
            self.filter_frame.exclude_custom_checkbox.get()
        )

        self.refresh_run_table()

    def on_game_version_changed(
        self,
        value: str
    ):

        if value == "All":
            self.current_filter.game_version = None
        else:
            self.current_filter.game_version = value

        self.refresh_run_table()

    def sort_game_versions(self, versions):

        return sorted(
            versions,
            key=lambda version: [
                int(part)
                for part in version.lstrip("v").split(".")
            ],
            reverse=True
        )

    def clear_filters(self):

        self.filter_frame.character_combo.set(
            "All"
        )

        self.filter_frame.result_combo.set(
            "All"
        )

        self.filter_frame.min_ascension_combo.set(
            "0"
        )

        self.filter_frame.max_ascension_combo.set(
            "10"
        )

        self.filter_frame.date_combo.set(
            "All"
        )

        self.filter_frame.exclude_daily_checkbox.deselect()
        self.filter_frame.exclude_custom_checkbox.deselect()

        self.filter_frame.from_date_entry.delete(
            0,
            "end"
        )

        self.filter_frame.to_date_entry.delete(
            0,
            "end"
        )

        self.filter_frame.hide_custom_dates()
        self.filter_frame.game_version_combo.set(
            "All"
        )

        self.current_filter = RunFilter()

        self.refresh_run_table()

    def open_death_analysis(self):

        if not self.filtered_runs:
            self.status.set(
                "No runs available for analysis."
            )
            return

        run_data = load_run_data(
            self.filtered_runs
        )

        if self.death_analysis_window is not None:
            try:
                if self.death_analysis_window.winfo_exists():
                    self.death_analysis_window.destroy()
            except Exception:
                pass

        self.death_analysis_window = DeathAnalysisWindow(
            self,
            run_data,
        )

    def open_combat_analysis(self):

        if not self.filtered_runs:
            self.status.set(
                "No runs available for analysis."
            )
            return

        run_data = load_run_data(
            self.filtered_runs
        )

        if self.combat_analysis_window is not None:
            try:
                if self.combat_analysis_window.winfo_exists():
                    self.combat_analysis_window.destroy()
            except Exception:
                pass

        self.combat_analysis_window = CombatAnalysisWindow(
            self,
            run_data,
        )

    def open_relic_analysis(self):

        if not self.filtered_runs:
            self.status.set(
                "No runs available for analysis."
            )
            return

        run_data = load_run_data(
            self.filtered_runs
        )

        if self.relic_analysis_window is not None:
            try:
                if self.relic_analysis_window.winfo_exists():
                    self.relic_analysis_window.destroy()
            except Exception:
                pass

        self.relic_analysis_window = RelicAnalysisWindow(
            self,
            run_data,
        )

    def update_analysis_window(
        self,
        window,
        runs,
    ):

        if window is None:
            return

        if not window.winfo_exists():
            return

        run_data = load_run_data(
            runs
        )

        window.update_runs(
            run_data
        )

    def update_analysis_windows(
        self,
        runs
    ):

        self.update_analysis_window(
            self.analysis_window,
            runs,
        )

        self.update_analysis_window(
            self.death_analysis_window,
            runs,
        )

        self.update_analysis_window(
            self.combat_analysis_window,
            runs,
        )

        self.update_analysis_window(
            self.relic_analysis_window,
            runs,
        )