import customtkinter as ctk

from analysis.combat_analysis import (
    calculate_elite_boss_statistics,
)
from analysis.death_analysis import (
    calculate_floor_statistics,
    calculate_floor_statistics_by_ascension,
    calculate_floor_statistics_by_character,
    calculate_floor_statistics_by_character_and_ascension,
    calculate_top_killed_by,
)
from data_models.run_data import RunData
from gui.analysis_table import AnalysisTable
from gui.formatters import format_encounter_name


class DeathAnalysisWindow(ctk.CTkToplevel):

    def __init__(
        self,
        master,
        runs: list[RunData],
    ):
        super().__init__(master)

        self.title("Death Analysis")
        self.geometry("1200x750")
        self.minsize(1000, 600)

        self.runs = runs

        self.build_ui()

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

    def build_ui(self):

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
            text="Death Analysis",
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

        controls_frame = ctk.CTkFrame(self)
        controls_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 10)
        )

        view_label = ctk.CTkLabel(
            controls_frame,
            text="Floor View:"
        )
        view_label.pack(
            side="left",
            padx=(10, 5)
        )

        self.view_combo = ctk.CTkComboBox(
            controls_frame,
            values=[
                "Overall",
                "By Character",
                "By Ascension",
                "By Character & Ascension",
            ],
            command=self.on_view_changed,
            width=220
        )
        self.view_combo.set("Overall")
        self.view_combo.pack(
            side="left",
            padx=(0, 10)
        )

        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=10,
        )
        self.scroll_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.content_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="transparent"
        )
        self.content_frame.pack(
            fill="both",
            expand=True
        )

        self.content_frame.grid_columnconfigure(
            0,
            weight=1,
            uniform="analysis",
        )
        self.content_frame.grid_columnconfigure(
            1,
            weight=1,
            uniform="analysis",
        )

        self.left_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.left_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8)
        )

        self.right_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.right_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0)
        )

        self.floor_section_frame = ctk.CTkFrame(
            self.left_frame,
            fg_color="transparent"
        )
        self.floor_section_frame.pack(
            fill="x"
        )

        self.floor_table_frame = ctk.CTkFrame(
            self.floor_section_frame,
            fg_color="transparent"
        )
        self.floor_table_frame.pack(
            fill="x",
            expand=True
        )

        self.death_section_frame = ctk.CTkFrame(
            self.left_frame,
            fg_color="transparent"
        )
        self.death_section_frame.pack(
            fill="x",
            pady=(30, 0)
        )

        self.encounter_section_frame = ctk.CTkFrame(
            self.right_frame,
            fg_color="transparent"
        )
        self.encounter_section_frame.pack(
            fill="x"
        )

        self.build_floor_table("Overall")
        self.build_killed_by_table()
        self.build_encounter_table()

    def get_run_summary(self):

        deaths = sum(
            1
            for run in self.runs
            if run.death_data is not None
        )

        return (
            f"{len(self.runs)} runs analysed "
            f"· {deaths} deaths"
        )

    def on_view_changed(self, value):

        self.build_floor_table(value)

    def build_floor_table(self, view):

        for widget in self.floor_table_frame.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(
            self.floor_section_frame,
            text="Floor Reached",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        title.pack(
            anchor="w",
            pady=(0, 10)
        )

        if view == "Overall":
            statistics = calculate_floor_statistics(
                self.runs
            )

            if statistics is None:
                self.build_empty_message(
                    self.floor_table_frame,
                    "No runs available for analysis."
                )
                return

            rows = [
                self.floor_statistics_row(
                    "Overall",
                    statistics,
                )
            ]

            columns = [
                "Group",
                "Runs",
                "Average",
                "Median",
                "Highest",
                "Lowest",
            ]

        elif view == "By Character":
            statistics = (
                calculate_floor_statistics_by_character(
                    self.runs
                )
            )

            rows = [
                self.floor_statistics_row(
                    character,
                    stats,
                )
                for character, stats
                in sorted(statistics.items())
            ]

            columns = [
                "Character",
                "Runs",
                "Average",
                "Median",
                "Highest",
                "Lowest",
            ]

        elif view == "By Ascension":
            statistics = (
                calculate_floor_statistics_by_ascension(
                    self.runs
                )
            )

            rows = [
                self.floor_statistics_row(
                    ascension,
                    stats,
                )
                for ascension, stats
                in sorted(statistics.items())
            ]

            columns = [
                "Ascension",
                "Runs",
                "Average",
                "Median",
                "Highest",
                "Lowest",
            ]

        elif view == "By Character & Ascension":
            statistics = (
                calculate_floor_statistics_by_character_and_ascension(
                    self.runs
                )
            )

            rows = [
                self.floor_statistics_row(
                    f"{character} A{ascension}",
                    stats,
                )
                for (
                    character,
                    ascension
                ), stats in sorted(statistics.items())
            ]

            columns = [
                "Character / Ascension",
                "Runs",
                "Average",
                "Median",
                "Highest",
                "Lowest",
            ]

        else:
            return

        table = AnalysisTable(
            self.floor_table_frame,
            columns,
            rows,
        )

        table.pack(
            fill="x",
            expand=True,
        )

    def build_killed_by_table(self):

        for widget in self.death_section_frame.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(
            self.death_section_frame,
            text="Top 10 Causes of Death",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )
        title.pack(
            anchor="w",
            pady=(0, 10)
        )

        statistics = calculate_top_killed_by(
            self.runs
        )

        if not statistics:
            self.build_empty_message(
                self.death_section_frame,
                "No deaths available for analysis."
            )
            return

        columns = [
            "Rank",
            "Killed By",
            "Deaths",
            "% of Deaths",
        ]

        rows = [
            (
                index,
                result.killed_by,
                result.deaths,
                result.percentage,
            )
            for index, result
            in enumerate(statistics, start=1)
        ]

        table = AnalysisTable(
            self.death_section_frame,
            columns,
            rows,
            percentage_columns={3},
        )

        table.pack(
            fill="x",
            expand=True,
        )

    def build_encounter_table(self):

        for widget in self.encounter_section_frame.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(
            self.encounter_section_frame,
            text="Elite & Boss Performance",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )
        title.pack(
            anchor="w",
            pady=(0, 10)
        )

        statistics = calculate_elite_boss_statistics(
            self.runs
        )

        if not statistics:
            self.build_empty_message(
                self.encounter_section_frame,
                "No elite or boss encounters available for analysis."
            )
            return

        columns = [
            "Type",
            "Encounter",
            "Faced",
            "Won",
            "Success Rate",
        ]

        rows = [
            (
                statistics[encounter].encounter_type.title(),
                format_encounter_name(encounter),
                statistics[encounter].faced,
                statistics[encounter].wins,
                statistics[encounter].success_rate,
            )
            for encounter in sorted(statistics)
        ]

        table = AnalysisTable(
            self.encounter_section_frame,
            columns,
            rows,
            percentage_columns={4},
            column_weights=[
                1,
                3,
                1,
                1,
                2,
            ],
        )

        table.pack(
            fill="x",
            expand=True,
        )

    @staticmethod
    def build_empty_message(parent, text):

        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=14)
        )
        label.pack(
            pady=20
        )

    def update_runs(self, runs: list[RunData]):

        self.runs = runs

        self.subtitle_label.configure(
            text=self.get_run_summary()
        )

        self.build_floor_table(
            self.view_combo.get()
        )

        self.build_killed_by_table()
        self.build_encounter_table()

    def close(self):

        self.destroy()

    def floor_statistics_row(
            self,
            group,
            statistics,
    ):
        return (
            group,
            statistics.runs,
            statistics.average,
            statistics.median,
            statistics.highest,
            statistics.lowest,
        )