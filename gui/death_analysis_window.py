import customtkinter as ctk

from data_models.run_data import RunData
from analysis.death_analysis import (
    calculate_floor_statistics,
    calculate_floor_statistics_by_ascension,
    calculate_floor_statistics_by_character,
    calculate_floor_statistics_by_character_and_ascension,
    calculate_top_killed_by,
)


class DeathAnalysisWindow(ctk.CTkToplevel):

    def __init__(
        self,
        master,
        runs: list[RunData],
    ):
        super().__init__(master)

        self.title("Death Analysis")
        self.geometry("950x750")

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
            label_text="Floor Reached"
        )
        self.scroll_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.floor_table_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="transparent"
        )
        self.floor_table_frame.pack(
            fill="x",
            expand=True
        )

        self.death_section_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="transparent"
        )
        self.death_section_frame.pack(
            fill="x",
            pady=(30, 0)
        )

        self.build_floor_table("Overall")
        self.build_killed_by_table()

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

        self.build_table(
            self.floor_table_frame,
            columns,
            rows
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

        self.build_table(
            self.death_section_frame,
            columns,
            rows,
            percentage_columns={3}
        )

    def build_table(
        self,
        parent,
        columns,
        rows,
        percentage_columns=None
    ):

        if percentage_columns is None:
            percentage_columns = set()

        table = ctk.CTkFrame(
            parent,
            corner_radius=8
        )
        table.pack(
            fill="x",
            expand=True
        )

        weights = [
            3,
            1,
            1,
            1,
            1,
            1,
        ]

        if len(columns) == 4:
            weights = [
                1,
                4,
                1,
                2,
            ]

        for column, weight in enumerate(weights[:len(columns)]):
            table.grid_columnconfigure(
                column,
                weight=weight
            )

        header_frame = ctk.CTkFrame(
            table,
            fg_color="transparent"
        )
        header_frame.grid(
            row=0,
            column=0,
            columnspan=len(columns),
            sticky="ew"
        )

        for column, heading in enumerate(columns):

            anchor = (
                "w"
                if column == 0
                else "e"
            )

            label = ctk.CTkLabel(
                header_frame,
                text=heading,
                font=ctk.CTkFont(
                    size=13,
                    weight="bold"
                ),
                anchor=anchor,
                text_color="#202020",
            )

            label.grid(
                row=0,
                column=column,
                sticky="ew",
                padx=10,
                pady=8
            )

            header_frame.grid_columnconfigure(
                column,
                weight=weights[column]
            )

        for row_index, row in enumerate(rows, start=1):

            background = (
                "#EAF2F8"
                if row_index % 2 == 0
                else "#F5F5F5"
            )

            row_frame = ctk.CTkFrame(
                table,
                fg_color=background,
                corner_radius=0
            )
            row_frame.grid(
                row=row_index,
                column=0,
                columnspan=len(columns),
                sticky="ew"
            )

            for column, value in enumerate(row):

                if column in percentage_columns:
                    text = f"{value:.1%}"
                elif isinstance(value, float):
                    text = f"{value:.1f}"
                else:
                    text = str(value)

                anchor = (
                    "w"
                    if column == 0
                    else "e"
                )

                label = ctk.CTkLabel(
                    row_frame,
                    text=text,
                    anchor=anchor,
                    text_color="#202020",
                )

                label.grid(
                    row=0,
                    column=column,
                    sticky="ew",
                    padx=10,
                    pady=6
                )

                row_frame.grid_columnconfigure(
                    column,
                    weight=weights[column]
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