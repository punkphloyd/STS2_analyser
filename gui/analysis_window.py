import customtkinter as ctk

from analysis.relic_analysis import calculate_neow_relic_statistics
from data_models.run_data import RunData
from gui.analysis_table import AnalysisTable


class AnalysisWindow(ctk.CTkToplevel):

    def __init__(
        self,
        master,
        runs: list[RunData],
        title="Neow's Bonus Relic Analysis",
    ):
        super().__init__(master)

        self.title(title)
        self.geometry("950x650")
        self.minsize(800, 500)

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
            corner_radius=10
        )
        header_frame.pack(
            fill="x",
            padx=15,
            pady=(15, 10)
        )

        title_label = ctk.CTkLabel(
            header_frame,
            text="Neow's Bonus Relics",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )
        title_label.pack(
            anchor="w",
            padx=20,
            pady=(15, 2)
        )

        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            text=f"{len(self.runs)} runs analysed",
            font=ctk.CTkFont(size=14)
        )

        self.subtitle_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        # ============================================================
        # Table
        # ============================================================

        self.table_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=10,
            fg_color="#F2F3F5"
        )
        self.table_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.build_table()

    def build_table(self):

        statistics = calculate_neow_relic_statistics(
            self.runs
        )

        headers = [
            "Relic",
            "Offered",
            "Picked",
            "Pick Rate",
            "Wins",
            "Win Rate",
        ]

        rows = []

        for relic, stats in statistics.items():

            rows.append(
                (
                    self.format_relic_name(relic),
                    stats.offered,
                    stats.picks,
                    stats.pick_rate,
                    stats.wins,
                    (
                        stats.win_rate
                        if stats.win_rate is not None
                        else "N/A"
                    ),
                )
            )

        table = AnalysisTable(
            self.table_frame,
            headers,
            rows,
            percentage_columns={3, 5},
            column_weights=[
                3,
                1,
                1,
                2,
                1,
                2,
            ],
        )

        table.pack(
            fill="x",
            expand=True,
            padx=5,
            pady=5,
        )

    @staticmethod
    def format_relic_name(relic: str) -> str:
        return relic.replace("_", " ").title()

    def update_runs(self, runs: list[RunData]):

        self.runs = runs

        self.subtitle_label.configure(
            text=f"{len(self.runs)} runs analysed"
        )

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        self.build_table()

    def close(self):
        self.destroy()