import customtkinter as ctk

from analysis.relic_analysis import (
    calculate_relic_statistics,
)
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

        self.build_table()

    def get_run_summary(self):

        return (
            f"{len(self.runs)} runs analysed"
        )

    def build_table(self):

        for widget in self.table_frame.winfo_children():
            widget.destroy()

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

    def update_runs(
        self,
        runs: list[RunData],
    ):

        self.runs = runs

        self.subtitle_label.configure(
            text=self.get_run_summary()
        )

        self.build_table()

    def close(self):

        self.destroy()