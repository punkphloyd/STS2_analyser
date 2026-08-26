import customtkinter as ctk

from analysis.combat_analysis import (
    get_available_acts,
    get_available_encounter_types,
    get_available_encounters,
)
from analysis.relic_analysis import (
    calculate_relic_encounter_statistics,
    calculate_relic_statistics,
)
from data_models.encounter_filter import EncounterFilter
from data_models.run_data import RunData
from gui.analysis_table import AnalysisTable
from gui.formatters import format_relic_name


class RelicAnalysisWindow(ctk.CTkToplevel):

    def __init__(
            self,
            master,
            runs: list[RunData],
    ):
        super().__init__(master)

        self.title("Relic Analysis")
        self.geometry("1600x900")
        self.minsize(1200, 600)

        self.runs = runs

        self.selected_act: int | None = None
        self.selected_encounter_type: str | None = None
        self.selected_encounter_name: str | None = None

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

        self.build_ui()

    def build_ui(self):
        # ============================================================
        # Header
        # ============================================================

        header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header_frame.pack(
            fill="x",
            padx=20,
            pady=(20, 0)
        )

        title_label = ctk.CTkLabel(
            header_frame,
            text="Relic Analysis",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )
        title_label.pack(
            anchor="w"
        )

        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            text=self.get_run_summary(),
            font=ctk.CTkFont(size=14)
        )
        self.subtitle_label.pack(
            anchor="w",
            pady=(0, 15)
        )

        # ============================================================
        # Encounter Filters
        # ============================================================

        filter_frame = ctk.CTkFrame(
            self,
        )
        filter_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 15),
        )

        filter_title = ctk.CTkLabel(
            filter_frame,
            text="Encounter Filter",
            font=ctk.CTkFont(
                size=15,
                weight="bold",
            ),
        )
        filter_title.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            padx=15,
            pady=(12, 8),
        )

        # Act

        act_label = ctk.CTkLabel(
            filter_frame,
            text="Act",
        )
        act_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=(15, 5),
            pady=(0, 12),
        )

        self.act_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["All"],
            command=self.on_act_changed,
            width=180,
        )
        self.act_menu.grid(
            row=1,
            column=1,
            sticky="w",
            padx=5,
            pady=(0, 12),
        )

        # Encounter type

        type_label = ctk.CTkLabel(
            filter_frame,
            text="Type",
        )
        type_label.grid(
            row=1,
            column=2,
            sticky="w",
            padx=(30, 5),
            pady=(0, 12),
        )

        self.encounter_type_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["All"],
            command=self.on_encounter_type_changed,
            width=180,
        )
        self.encounter_type_menu.grid(
            row=1,
            column=3,
            sticky="w",
            padx=5,
            pady=(0, 12),
        )

        # Encounter

        encounter_label = ctk.CTkLabel(
            filter_frame,
            text="Encounter",
        )
        encounter_label.grid(
            row=1,
            column=4,
            sticky="w",
            padx=(30, 5),
            pady=(0, 12),
        )

        self.encounter_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["All"],
            command=self.on_encounter_changed,
            width=300,
        )
        self.encounter_menu.grid(
            row=1,
            column=5,
            sticky="w",
            padx=5,
            pady=(0, 12),
        )

        filter_frame.grid_columnconfigure(
            6,
            weight=1,
        )

        # ============================================================
        # Table
        # ============================================================

        self.table_frame = ctk.CTkScrollableFrame(
            self,
            label_text="Relics",
        )
        self.table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.refresh_filter_options()
        self.build_table()

    # ================================================================
    # Filter handling
    # ================================================================

    def get_encounter_filter(self) -> EncounterFilter:
        return EncounterFilter(
            act=self.selected_act,
            encounter_type=self.selected_encounter_type,
            encounter_name=self.selected_encounter_name,
        )

    def on_act_changed(
        self,
        value: str,
    ):
        if value == "All":
            self.selected_act = None
        else:
            self.selected_act = int(value)

        self.selected_encounter_type = None
        self.selected_encounter_name = None

        self.refresh_type_menu()
        self.refresh_encounter_menu()
        self.build_table()

    def on_encounter_type_changed(
        self,
        value: str,
    ):
        if value == "All":
            self.selected_encounter_type = None
        else:
            self.selected_encounter_type = value

        self.selected_encounter_name = None

        self.refresh_encounter_menu()
        self.build_table()

    def on_encounter_changed(
        self,
        value: str,
    ):
        if value == "All":
            self.selected_encounter_name = None
        else:
            self.selected_encounter_name = value

        self.build_table()

    def refresh_filter_options(self):
        self.refresh_act_menu()
        self.refresh_type_menu()
        self.refresh_encounter_menu()

    def refresh_act_menu(self):
        acts = get_available_acts(
            self.runs,
        )

        values = ["All"] + [
            str(act)
            for act in acts
        ]

        self.act_menu.configure(
            values=values,
        )

        if self.selected_act is None:
            self.act_menu.set("All")
        elif self.selected_act in acts:
            self.act_menu.set(
                str(self.selected_act)
            )
        else:
            self.selected_act = None
            self.act_menu.set("All")

    def refresh_type_menu(self):
        encounter_filter = EncounterFilter(
            act=self.selected_act,
        )

        encounter_types = get_available_encounter_types(
            self.runs,
            encounter_filter,
        )

        values = ["All"] + encounter_types

        self.encounter_type_menu.configure(
            values=values,
        )

        if (
            self.selected_encounter_type is not None
            and self.selected_encounter_type
            in encounter_types
        ):
            self.encounter_type_menu.set(
                self.selected_encounter_type
            )
        else:
            self.selected_encounter_type = None
            self.encounter_type_menu.set("All")

    def refresh_encounter_menu(self):
        encounter_filter = EncounterFilter(
            act=self.selected_act,
            encounter_type=self.selected_encounter_type,
        )

        encounters = get_available_encounters(
            self.runs,
            encounter_filter,
        )

        values = ["All"] + encounters

        self.encounter_menu.configure(
            values=values,
        )

        if (
            self.selected_encounter_name is not None
            and self.selected_encounter_name
            in encounters
        ):
            self.encounter_menu.set(
                self.selected_encounter_name
            )
        else:
            self.selected_encounter_name = None
            self.encounter_menu.set("All")

    # ================================================================
    # Run summary
    # ================================================================

    def get_run_summary(self):

        if self.has_encounter_filter():
            return (
                f"{len(self.runs)} runs analysed"
                " • Encounter filter active"
            )

        return (
            f"{len(self.runs)} runs analysed"
        )

    def has_encounter_filter(self) -> bool:
        return (
            self.selected_act is not None
            or self.selected_encounter_type is not None
            or self.selected_encounter_name is not None
        )

    # ================================================================
    # Table
    # ================================================================

    def build_table(self):

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        if self.has_encounter_filter():
            self.build_encounter_table()
        else:
            self.build_relic_table()

        self.subtitle_label.configure(
            text=self.get_run_summary()
        )

    def build_relic_table(self):

        statistics = calculate_relic_statistics(
            self.runs
        )

        if not statistics:
            self.build_empty_message(
                self.table_frame,
                "No relic acquisitions available for analysis."
            )
            return

        total_runs = len(self.runs)

        columns = [
            "Relic",
            "Runs Acquired",
            "% of Runs",
            "Wins",
            "Win Rate",
        ]

        rows = []

        for relic, stats in sorted(
            statistics.items()
        ):

            percentage = (
                stats.runs_acquired / total_runs
                if total_runs > 0
                else 0
            )

            rows.append(
                (
                    format_relic_name(relic),
                    stats.runs_acquired,
                    percentage,
                    stats.wins,
                    stats.win_rate,
                )
            )

        table = AnalysisTable(
            self.table_frame,
            columns,
            rows,
            percentage_columns={2, 4},
        )

        table.pack(
            fill="x",
            expand=True,
        )

    def build_encounter_table(self):

        statistics = calculate_relic_encounter_statistics(
            self.runs,
            encounter_filter=self.get_encounter_filter(),
        )

        if not statistics:
            self.build_empty_message(
                self.table_frame,
                "No relic encounter data available for the selected filters."
            )
            return

        columns = [
            "Relic",
            "Fights",
            "Wins",
            "Win Rate",
            "Average Damage",
            "Median Damage",
            "Min Damage",
            "Max Damage",
            "Average Turns",
            "Min Turns",
            "Max Turns",
            "Damage / Turn",
        ]

        rows = []

        for relic, stats in sorted(
            statistics.items()
        ):

            rows.append(
                (
                    format_relic_name(relic),
                    stats.fights,
                    stats.wins,
                    stats.win_rate,
                    stats.average_damage,
                    stats.median_damage,
                    stats.minimum_damage,
                    stats.maximum_damage,
                    stats.average_turns,
                    stats.minimum_turns,
                    stats.maximum_turns,
                    stats.average_damage_per_turn,
                )
            )

        table = AnalysisTable(
            self.table_frame,
            columns,
            rows,
            percentage_columns={3},
        )

        table.pack(
            fill="x",
            expand=True,
        )

    # ================================================================
    # Empty state
    # ================================================================

    @staticmethod
    def build_empty_message(
        parent,
        text,
    ):

        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=14)
        )
        label.pack(
            pady=20
        )

    # ================================================================
    # External updates
    # ================================================================

    def update_runs(
        self,
        runs: list[RunData],
    ):

        self.runs = runs

        self.selected_act = None
        self.selected_encounter_type = None
        self.selected_encounter_name = None

        self.refresh_filter_options()

        self.build_table()

    # ================================================================
    # Close
    # ================================================================

    def close(self):

        self.destroy()